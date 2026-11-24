#!/usr/bin/env python3
"""Genera la versión editable en Word del Documento Final a partir de las fuentes LaTeX.

Flujo: LaTeX aplanado -> Markdown (Pandoc) -> DOCX (Pandoc + citeproc APA 7) -> ajustes de estilo (python-docx).
Uso: python3 scripts/generar_docx.py build/Proy-38-Doc-Final.docx   (ejecutar desde tesis/)
"""
import re
import warnings
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

warnings.filterwarnings("ignore", category=UserWarning)
TESIS = Path(__file__).resolve().parents[1]
RAIZ = TESIS.parent
AUX = TESIS / "build/docx"
AUX.mkdir(parents=True, exist_ok=True)
SALIDA = TESIS / (sys.argv[1] if len(sys.argv) > 1 else "build/Proy-38-Doc-Final.docx")
MARINO = RGBColor(0x0F, 0x2A, 0x5F)
PIZARRA = RGBColor(0x33, 0x41, 0x55)


def aplanar(ruta: Path) -> str:
    texto = ruta.read_text(encoding="utf-8")

    def sustituir(m):
        nombre = m.group(1)
        archivo = TESIS / (nombre if nombre.endswith(".tex") else nombre + ".tex")
        return aplanar(archivo)

    return re.sub(r"\\input\{([^}]+)\}", sustituir, texto)


def preparar_latex() -> str:
    tex = aplanar(TESIS / "documento_final.tex")
    cuerpo = tex[tex.index("\\begin{document}"):]
    macros = "\n".join((TESIS / f).read_text(encoding="utf-8") for f in
                       ("config_caratula.tex", "generado/resultados.tex", "generado/anexo_codigo_macros.tex"))
    # Bibliografía: la genera citeproc (APA 7) en la posición marcada.
    cuerpo = re.sub(r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}", "MARCADORREFERENCIAS",
                    cuerpo, flags=re.S)
    cuerpo = cuerpo.replace("\\clearpage\\phantomsection\\addcontentsline{toc}{chapter}{Bibliografía}",
                            "\\chapter*{Bibliografía}")
    # Recuadros técnicos: título en negrita seguido del contenido.
    cuerpo = re.sub(r"\\begin\{nota\}\[([^\]]*)\]", r"\\par\\textbf{\1.} ", cuerpo)
    cuerpo = re.sub(r"\\begin\{nota\}", r"\\par\\textbf{Nota técnica.} ", cuerpo)
    cuerpo = cuerpo.replace("\\end{nota}", "\\par")
    cuerpo = re.sub(r"\\path\{([^}]*)\}", lambda m: "\\texttt{" + m.group(1).replace("_", "\\_") + "}", cuerpo)
    cuerpo = notas_fuera_de_figuras(cuerpo)
    cuerpo = re.sub(r"\\fuente\{", r"\\par\\emph{Nota.} {", cuerpo)
    # Índices: Word los genera con «Actualizar campos»; se omiten las listas de LaTeX.
    for cmd in ("\\tableofcontents", "\\listoffigures", "\\listoftables", "\\lstlistoflistings"):
        cuerpo = cuerpo.replace(cmd, "")
    cuerpo = re.sub(r"\\begin\{titlepage\}", "", cuerpo).replace("\\end{titlepage}", "")
    cuerpo = re.sub(r"\\[Bb]ig[lr]?(?=[()|.\\\[\]])", "", cuerpo)
    cuerpo = re.sub(r"\\(needspace|vspace\*?)\{[^}]*\}", "", cuerpo)
    nums = etiquetas()
    cuerpo = rotular_codigos(cuerpo, nums)
    cuerpo = re.sub(r"\\eqref\{([^}]+)\}", lambda m: f"({nums.get(m.group(1), '?')})", cuerpo)
    cuerpo = re.sub(r"\\ref\{([^}]+)\}", lambda m: nums.get(m.group(1), "?"), cuerpo)
    cuerpo = re.sub(r"\\lstinputlisting\[[^\]]*language=TOML[^\]]*\]\{([^}]+)\}",
                    lambda m: "\\begin{verbatim}\n" + (TESIS / m.group(1)).read_text(encoding="utf-8") + "\\end{verbatim}",
                    cuerpo)
    return "\\documentclass{report}\n" + macros + "\n" + cuerpo


def notas_fuera_de_figuras(cuerpo: str) -> str:
    """Word coloca la nota junto a la imagen si queda dentro de la figura: se mueve debajo de ella."""
    salida, pos = [], 0
    while (ini := cuerpo.find("\\begin{figure}", pos)) != -1:
        fin = cuerpo.index("\\end{figure}", ini) + len("\\end{figure}")
        bloque = cuerpo[ini:fin]
        nota = ""
        if (k := bloque.find("\\fuente{")) != -1:
            cierre = argumento(bloque, k + len("\\fuente"))
            nota = bloque[k:cierre + 1]
            bloque = bloque[:k] + bloque[cierre + 1:]
        salida.append(cuerpo[pos:ini] + bloque + "\n" + nota + "\n")
        pos = fin
    salida.append(cuerpo[pos:])
    return "".join(salida)


def etiquetas() -> dict:
    """Números de figuras, tablas, códigos, ecuaciones y capítulos resueltos por XeLaTeX (.aux)."""
    aux = (TESIS / "build/aux/documento_final.aux").read_text(encoding="utf-8")
    return dict(re.findall(r"\\newlabel\{([^}]+)\}\{\{([^}]*)\}", aux))


def argumento(texto: str, ini: int) -> int:
    """Devuelve la posición de la llave que cierra el grupo que empieza en texto[ini] == '{'."""
    prof = 0
    for i in range(ini, len(texto)):
        if texto[i] == "{":
            prof += 1
        elif texto[i] == "}":
            prof -= 1
            if prof == 0:
                return i
    raise ValueError("llaves desbalanceadas")


def rotular_codigos(cuerpo: str, nums: dict) -> str:
    """Antepone «Código N» y el título en cursiva a cada listado (como en el PDF)."""
    salida, pos = [], 0
    patron = re.compile(r"\\lstinputlisting\[|\\begin\{lstlisting\}\[")
    while (m := patron.search(cuerpo, pos)):
        ini_opts = m.end()
        prof, j = 1, ini_opts
        while prof:
            prof += {"[": 1, "]": -1}.get(cuerpo[j], 0) if cuerpo[j] in "[]" else 0
            if cuerpo[j] == "{":
                j = argumento(cuerpo, j)
            j += 1
        opts = cuerpo[ini_opts:j - 1]
        rotulo = ""
        if "caption=" in opts:
            c = opts.index("caption=") + len("caption=")
            titulo = opts[c + 1:argumento(opts, c)] if opts[c] == "{" else opts[c:].split(",")[0]
            lab = re.search(r"label=([^,\]]+)", opts)
            num = nums.get(lab.group(1).strip(), "") if lab else ""
            rotulo = f"\\par\\textbf{{Código {num}}}\\par\\emph{{{titulo}}}\\par\n"
        salida.append(cuerpo[pos:m.start()] + rotulo + cuerpo[m.start():j])
        pos = j
    salida.append(cuerpo[pos:])
    return "".join(salida)


def main():
    tex = preparar_latex()
    (AUX / "documento.tex").write_text(tex, encoding="utf-8")
    filtro = AUX / "referencias.lua"
    filtro.write_text(
        'function Para(el)\n'
        '  if pandoc.utils.stringify(el) == "MARCADORREFERENCIAS" then\n'
        '    return pandoc.Div({}, {id = "refs"})\n'
        '  end\nend\n', encoding="utf-8")
    referencia = AUX / "referencia.docx"
    subprocess.run(["pandoc", "-o", str(referencia), "--print-default-data-file", "reference.docx"], check=True)
    estilizar_referencia(referencia)
    subprocess.run(["pandoc", str(AUX / "documento.tex"), "-f", "latex", "-o", str(SALIDA),
                    "--lua-filter", str(filtro), "--citeproc",
                    "--bibliography", str(RAIZ / "referencias/bibliografia_zotero.bib"),
                    "--csl", str(TESIS / "estilos/apa.csl"), "-M", "lang=es-ES", "-M", "link-citations=true",
                    "--reference-doc", str(referencia), "--resource-path", str(TESIS)],
                   cwd=TESIS, check=True)
    ajustar(SALIDA)
    print(f"DOCX: {SALIDA.relative_to(TESIS.parent)} ({SALIDA.stat().st_size} bytes)")


def fuente(estilo, nombre, tam=None, color=None, negrita=None, cursiva=None):
    estilo.font.name = nombre
    rpr = estilo.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for atr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(atr), nombre)
    for atr in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        if rfonts.get(qn(atr)) is not None:
            del rfonts.attrib[qn(atr)]
    if tam:
        estilo.font.size = Pt(tam)
    if color is not None:
        estilo.font.color.rgb = color
    if negrita is not None:
        estilo.font.bold = negrita
    if cursiva is not None:
        estilo.font.italic = cursiva


def estilizar_referencia(ruta):
    doc = Document(ruta)
    sec = doc.sections[0]
    sec.orientation = WD_ORIENT.PORTRAIT
    sec.page_width, sec.page_height = Cm(21.59), Cm(27.94)
    for m in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, m, Cm(2.54))
    est = doc.styles
    for nombre in ("Normal", "Body Text", "First Paragraph", "Compact"):
        if nombre in [s.name for s in est]:
            e = est[nombre]
            fuente(e, "Times New Roman", 12, RGBColor(0, 0, 0))
            e.paragraph_format.line_spacing = 1.5
            e.paragraph_format.space_after = Pt(6)
    if "Body Text" in [s.name for s in est]:
        est["Body Text"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        est["Body Text"].paragraph_format.first_line_indent = Cm(1.27)
    for i, tam in ((1, 16), (2, 13), (3, 12), (4, 12)):
        e = est[f"Heading {i}"]
        fuente(e, "Times New Roman", tam, MARINO if i < 3 else PIZARRA, True, i == 4)
        e.paragraph_format.keep_with_next = True
        e.paragraph_format.space_before = Pt(18 if i == 1 else 12)
        e.paragraph_format.space_after = Pt(6)
    if "Title" in [s.name for s in est]:
        fuente(est["Title"], "Times New Roman", 20, MARINO, True)
    for nombre in ("Source Code", "Verbatim Char"):
        if nombre in [s.name for s in est]:
            fuente(est[nombre], "Consolas", 9)
    for nombre in ("Caption", "Table Caption", "Image Caption"):
        if nombre in [s.name for s in est]:
            fuente(est[nombre], "Times New Roman", 11, RGBColor(0, 0, 0), False, True)
            est[nombre].paragraph_format.keep_with_next = True
    if "Bibliography" in [s.name for s in est]:
        b = est["Bibliography"]
        fuente(b, "Times New Roman", 12, RGBColor(0, 0, 0))
        b.paragraph_format.left_indent = Cm(1.27)
        b.paragraph_format.first_line_indent = Cm(-1.27)
        b.paragraph_format.line_spacing = 1.5
    for nombre in ("Hyperlink",):
        if nombre in [s.name for s in est]:
            est[nombre].font.color.rgb = MARINO
    doc.save(ruta)


def borde(celda_o_tabla_pr, lado, valor="single", tam=8, color="0F2A5F"):
    b = OxmlElement(f"w:{lado}")
    b.set(qn("w:val"), valor)
    b.set(qn("w:sz"), str(tam))
    b.set(qn("w:space"), "0")
    b.set(qn("w:color"), color)
    celda_o_tabla_pr.append(b)


def ajustar(ruta):
    """Tablas APA (solo reglas horizontales azul marino) y numeración de figuras y tablas."""
    doc = Document(ruta)
    for t in doc.tables:
        tblpr = t._tbl.tblPr
        for viejo in tblpr.findall(qn("w:tblBorders")):
            tblpr.remove(viejo)
        bordes = OxmlElement("w:tblBorders")
        borde(bordes, "top", tam=12)
        borde(bordes, "bottom", tam=12)
        for lado in ("left", "right", "insideV", "insideH"):
            borde(bordes, lado, valor="nil")
        tblpr.append(bordes)
        if t.rows:
            for celda in t.rows[0].cells:
                tcpr = celda._tc.get_or_add_tcPr()
                bb = OxmlElement("w:tcBorders")
                borde(bb, "bottom", tam=6)
                tcpr.append(bb)
                for p in celda.paragraphs:
                    for r in p.runs:
                        r.font.bold = True
        for fila in t.rows:
            for celda in fila.cells:
                for p in celda.paragraphs:
                    p.paragraph_format.first_line_indent = Cm(0)
                    p.paragraph_format.line_spacing = 1.0
                    for r in p.runs:
                        r.font.size = Pt(10)
    cap, fig, tab = 0, 0, 0
    anexo = False
    for p in doc.paragraphs:
        nombre = p.style.name
        if nombre == "Heading 1":
            texto = p.text.strip()
            if texto.startswith(("Identificación", "Agradecimientos", "Resumen", "Abstract", "Bibliografía")):
                continue
            if texto.startswith("Salida de"):
                anexo, cap = True, 0
            cap += 1
            fig = tab = 0
            etiqueta = (chr(64 + cap) if anexo else str(cap))
            p.insert_paragraph_before(("ANEXO " if anexo else "CAPÍTULO ") + etiqueta, style="Heading 1") \
                .paragraph_format.page_break_before = True
            p.paragraph_format.page_break_before = False
            p._etiqueta = etiqueta
        elif nombre in ("Image Caption", "Table Caption") and p.text.strip():
            etiqueta = (chr(64 + cap) if anexo else str(cap)) + "."
            if cap == 0:
                etiqueta = ""
            if nombre == "Image Caption":
                fig += 1
                rotulo = f"Figura {etiqueta}{fig}"
            else:
                tab += 1
                rotulo = f"Tabla {etiqueta}{tab}"
            nuevo = p.insert_paragraph_before(style=nombre)
            r = nuevo.add_run(rotulo)
            r.bold, r.italic = True, False
            nuevo.paragraph_format.keep_with_next = True
    # APA: rótulo y título de la figura encima de la imagen.
    for p in list(doc.paragraphs):
        if p.style.name == "Image Caption" and p.text.startswith("Figura "):
            titulo = p._p.getnext()
            figura = p._p.getprevious()
            while figura is not None and not figura.xpath(".//w:drawing"):
                figura = figura.getprevious()
            if figura is not None:
                figura.addprevious(p._p)
                if titulo is not None:
                    figura.addprevious(titulo)
    # Carátula centrada (hasta el primer título de nivel 1).
    for p in doc.paragraphs:
        if p.style.name == "Heading 1":
            break
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
    doc.save(ruta)


if __name__ == "__main__":
    main()
