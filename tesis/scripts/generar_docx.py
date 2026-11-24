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
MARINO = RGBColor(0, 0, 0)
PIZARRA = RGBColor(0, 0, 0)
GRIS = "444444"
TITULO_CORTO = "Redes Neuronales desde Cero en Rust"


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
    cuerpo = re.sub(r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}", "\n\nMARCADORREFERENCIAS\n\n",
                    cuerpo, flags=re.S)
    cuerpo = cuerpo.replace("\\singlespacing", "")
    cuerpo = re.sub(r"\\\\\s+(?=Y TELECOMUNICACIONES)", " ", cuerpo)
    cuerpo = cuerpo.replace("\\newline", ",")
    cuerpo = limpiar_columnas(cuerpo)
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


def limpiar_columnas(cuerpo: str) -> str:
    """Pandoc pierde contenido con prefijos >{...} y @{...} en la especificación de columnas: se eliminan."""
    def limpiar(spec):
        out, i = [], 0
        while i < len(spec):
            if spec[i] in ">@" and i + 1 < len(spec) and spec[i + 1] == "{":
                i = argumento(spec, i + 1) + 1
                continue
            out.append(spec[i])
            i += 1
        return "".join(out)

    salida, pos = [], 0
    patron = re.compile(r"\\begin\{(tabularx|tabular\*)\}\{[^{}]*\}\{|\\begin\{tabular\}\{")
    while (m := patron.search(cuerpo, pos)):
        ini = m.end() - 1
        fin = argumento(cuerpo, ini)
        salida.append(cuerpo[pos:ini] + "{" + limpiar(cuerpo[ini + 1:fin]) + "}")
        pos = fin + 1
    salida.append(cuerpo[pos:])
    return "".join(salida)


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
        'local function marca(el)\n'
        '  if pandoc.utils.stringify(el):find("MARCADORREFERENCIAS") then\n'
        '    return pandoc.Div({}, {id = "refs"})\n'
        '  end\nend\n'
        'Para = marca\nPlain = marca\n', encoding="utf-8")
    referencia = AUX / "referencia.docx"
    subprocess.run(["pandoc", "-o", str(referencia), "--print-default-data-file", "reference.docx"], check=True)
    estilizar_referencia(referencia)
    subprocess.run(["pandoc", str(AUX / "documento.tex"), "-f", "latex", "-o", str(SALIDA),
                    "--lua-filter", str(filtro), "--citeproc", "--no-highlight",
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
            e.paragraph_format.line_spacing = 1.15
            e.paragraph_format.space_after = Pt(3)
    if "Body Text" in [s.name for s in est]:
        est["Body Text"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        est["Body Text"].paragraph_format.first_line_indent = Cm(1.27)
    for i, tam in ((1, 16), (2, 13), (3, 12), (4, 12)):
        e = est[f"Heading {i}"]
        fuente(e, "Times New Roman", tam, MARINO if i < 3 else PIZARRA, True, i == 4)
        e.paragraph_format.keep_with_next = True
        e.paragraph_format.space_before = Pt(12 if i == 1 else 8)
        e.paragraph_format.space_after = Pt(4)
    if "Title" in [s.name for s in est]:
        fuente(est["Title"], "Times New Roman", 20, MARINO, True)
    for nombre in ("Source Code", "Verbatim Char"):
        if nombre in [s.name for s in est]:
            fuente(est[nombre], "Consolas", 8)
    if "Source Code" in [s.name for s in est]:
        est["Source Code"].paragraph_format.line_spacing = 1.0
        est["Source Code"].paragraph_format.space_after = Pt(0)
        est["Source Code"].paragraph_format.space_before = Pt(0)
    for nombre in ("Caption", "Table Caption", "Image Caption"):
        if nombre in [s.name for s in est]:
            fuente(est[nombre], "Times New Roman", 11, RGBColor(0, 0, 0), False, True)
            est[nombre].paragraph_format.keep_with_next = True
    if "Bibliography" in [s.name for s in est]:
        b = est["Bibliography"]
        fuente(b, "Times New Roman", 12, RGBColor(0, 0, 0))
        b.paragraph_format.left_indent = Cm(1.27)
        b.paragraph_format.first_line_indent = Cm(-1.27)
        b.paragraph_format.line_spacing = 1.15
    for nombre in ("Hyperlink",):
        if nombre in [s.name for s in est]:
            est[nombre].font.color.rgb = MARINO
    doc.save(ruta)


def borde(celda_o_tabla_pr, lado, valor="single", tam=8, color=GRIS):
    b = OxmlElement(f"w:{lado}")
    b.set(qn("w:val"), valor)
    b.set(qn("w:sz"), str(tam))
    b.set(qn("w:space"), "0")
    b.set(qn("w:color"), color)
    celda_o_tabla_pr.append(b)


def estilo_parrafo(doc, nombre, base="Normal", tam=12, negrita=False, cursiva=False, centrado=False):
    est = doc.styles
    if nombre in [x.name for x in est]:
        return est[nombre]
    from docx.enum.style import WD_STYLE_TYPE
    e = est.add_style(nombre, WD_STYLE_TYPE.PARAGRAPH)
    e.base_style = est[base]
    fuente(e, "Times New Roman", tam, RGBColor(0, 0, 0), negrita, cursiva)
    e.paragraph_format.first_line_indent = Cm(0)
    e.paragraph_format.keep_with_next = True
    e.paragraph_format.space_before = Pt(6)
    e.paragraph_format.space_after = Pt(6)
    e.paragraph_format.line_spacing = 1.0
    if centrado:
        e.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return e


def anteponer(p, texto, negrita=None, cursiva=None, salto=False):
    """Inserta un run al inicio del párrafo (después de pPr)."""
    r = p.add_run(texto)
    if negrita is not None:
        r.bold = negrita
    if cursiva is not None:
        r.italic = cursiva
    if salto:
        r.add_break()
    ppr = p._p.pPr
    (ppr.addnext if ppr is not None else (lambda e: p._p.insert(0, e)))(r._r)
    return r


def campo(p, instruccion, texto_previo=""):
    """Añade un campo de Word (PAGE, TOC, …) al párrafo."""
    def fld(tipo):
        r = OxmlElement("w:r")
        f = OxmlElement("w:fldChar")
        f.set(qn("w:fldCharType"), tipo)
        if tipo == "begin":
            f.set(qn("w:dirty"), "true")
        r.append(f)
        return r
    p._p.append(fld("begin"))
    r = OxmlElement("w:r")
    t = OxmlElement("w:instrText")
    t.set(qn("xml:space"), "preserve")
    t.text = f" {instruccion} "
    r.append(t)
    p._p.append(r)
    p._p.append(fld("separate"))
    r = OxmlElement("w:r")
    t = OxmlElement("w:t")
    t.text = texto_previo or "1"
    r.append(t)
    p._p.append(r)
    p._p.append(fld("end"))


def encabezado(seccion, ancho_cm):
    seccion.header.is_linked_to_previous = False
    hdr = seccion.header
    p = hdr.paragraphs[0] if hdr.paragraphs else hdr.add_paragraph()
    for r in list(p.runs):
        r._r.getparent().remove(r._r)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(ancho_cm), alignment=2)
    r = p.add_run(TITULO_CORTO + "\t")
    r.font.size = Pt(10)
    r.font.name = "Times New Roman"
    campo(p, "PAGE")
    for r in p.runs:
        r.font.size = Pt(10)
    ppr = p._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr")
    borde(bdr, "bottom", tam=4, color="000000")
    ppr.append(bdr)


def numeracion_paginas(sectpr, formato, inicio=1):
    for viejo in sectpr.findall(qn("w:pgNumType")):
        sectpr.remove(viejo)
    pg = OxmlElement("w:pgNumType")
    pg.set(qn("w:fmt"), formato)
    pg.set(qn("w:start"), str(inicio))
    sectpr.append(pg)


def ajustar(ruta):
    """Tablas APA, numeración jerárquica, rótulos, índices, encabezados y paginación."""
    doc = Document(ruta)
    rot_fig = estilo_parrafo(doc, "Rotulo Figura", "Normal", 12)
    rot_tab = estilo_parrafo(doc, "Rotulo Tabla", "Normal", 12)
    rot_cod = estilo_parrafo(doc, "Rotulo Codigo", "Normal", 12)
    etiqueta_cap = estilo_parrafo(doc, "Etiqueta Capitulo", "Normal", 13, negrita=True, centrado=True)
    titulo_indice = estilo_parrafo(doc, "Titulo Indice", "Normal", 16, negrita=True, centrado=True)

    # Índices compactos (estilos TOC de Word)
    from docx.enum.style import WD_STYLE_TYPE
    for nivel in range(1, 4):
        nombre = f"toc {nivel}"
        try:
            e = doc.styles[nombre]
        except KeyError:
            e = doc.styles.add_style(nombre, WD_STYLE_TYPE.PARAGRAPH)
            e.base_style = doc.styles["Normal"]
        fuente(e, "Times New Roman", 11, RGBColor(0, 0, 0))
        e.paragraph_format.line_spacing = 1.0
        e.paragraph_format.space_after = Pt(2)
        e.paragraph_format.space_before = Pt(0)
        e.paragraph_format.first_line_indent = Cm(0)
        e.paragraph_format.left_indent = Cm(0.6 * (nivel - 1))

    # Tablas APA: solo reglas horizontales finas (gris neutro), encabezado en negrita
    for t in doc.tables:
        tblpr = t._tbl.tblPr
        for viejo in tblpr.findall(qn("w:tblBorders")):
            tblpr.remove(viejo)
        bordes = OxmlElement("w:tblBorders")
        borde(bordes, "top", tam=8)
        borde(bordes, "bottom", tam=8)
        for lado in ("left", "right", "insideV", "insideH"):
            borde(bordes, lado, valor="nil")
        tblpr.append(bordes)
        if t.rows:
            for celda in t.rows[0].cells:
                tcpr = celda._tc.get_or_add_tcPr()
                bb = OxmlElement("w:tcBorders")
                borde(bb, "bottom", tam=4)
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
                        r.font.size = Pt(9.5)

    # Numeración jerárquica, etiquetas de capítulo y rótulos
    cap, sec, sub, fig, tab = "", 0, 0, 0, 0
    anexo, numerar, primer_cap = False, False, None
    parrafos = list(doc.paragraphs)
    k = 0
    while k < len(parrafos):
        p = parrafos[k]
        nombre, texto = p.style.name, p.text.strip()
        if nombre == "Heading 1":
            if texto.startswith(("Identificación", "Agradecimientos", "Resumen", "Abstract", "Bibliografía")):
                numerar = False
                p.paragraph_format.page_break_before = True
            else:
                if texto.startswith("Salida de"):
                    anexo, n = True, 0
                n = (n + 1) if cap else 1
                cap = chr(64 + n) if anexo else str(n)
                sec = sub = fig = tab = 0
                numerar = True
                lab = p.insert_paragraph_before(("ANEXO " if anexo else "CAPÍTULO ") + cap, style=etiqueta_cap)
                lab.paragraph_format.page_break_before = True
                if primer_cap is None:
                    primer_cap = lab
                anteponer(p, cap + " ")
                p.paragraph_format.page_break_before = False
        elif nombre == "Heading 2" and numerar:
            sec, sub = sec + 1, 0
            anteponer(p, f"{cap}.{sec} ")
        elif nombre == "Heading 3" and numerar:
            sub += 1
            anteponer(p, f"{cap}.{sec}.{sub} ")
        elif nombre in ("Image Caption", "Table Caption") and texto:
            pre = f"{cap}." if numerar else ""
            if nombre == "Image Caption":
                fig += 1
                anteponer(p, f"Figura {pre}{fig}", negrita=True, cursiva=False, salto=True)
                p.style = rot_fig
            else:
                tab += 1
                anteponer(p, f"Tabla {pre}{tab}", negrita=True, cursiva=False, salto=True)
                p.style = rot_tab
            for r in p.runs[1:]:
                r.italic = True
        elif re.fullmatch(r"Código [A-Z0-9]+\.\d+", texto) and k + 1 < len(parrafos):
            titulo = parrafos[k + 1]
            p.style = rot_cod
            for r in p.runs:
                r.bold = True
            p.runs[-1].add_break()
            for r in list(titulo.runs):
                r.italic = True
                p._p.append(r._r)
            titulo._p.getparent().remove(titulo._p)
            k += 1
        k += 1

    # APA: rótulo y título de la figura encima de la imagen
    for p in list(doc.paragraphs):
        if p.style.name == "Rotulo Figura":
            figura = p._p.getprevious()
            while figura is not None and not figura.xpath(".//w:drawing"):
                figura = figura.getprevious()
            if figura is not None:
                figura.addprevious(p._p)

    # Carátula centrada (hasta el primer título de nivel 1)
    for p in doc.paragraphs:
        if p.style.name == "Heading 1":
            break
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)

    # Índices de Word (campos TOC) antes del Capítulo 1
    for titulo, instr in (("Índice General", 'TOC \\o "1-3" \\h \\z \\u'),
                          ("Índice de Figuras", 'TOC \\h \\z \\t "Rotulo Figura,1"'),
                          ("Índice de Tablas", 'TOC \\h \\z \\t "Rotulo Tabla,1"'),
                          ("Lista de Códigos", 'TOC \\h \\z \\t "Rotulo Codigo,1"')):
        t = primer_cap.insert_paragraph_before(titulo, style=titulo_indice)
        t.paragraph_format.page_break_before = titulo == "Índice General"
        t.paragraph_format.space_before = Pt(6 if titulo == "Índice General" else 18)
        cuerpo = primer_cap.insert_paragraph_before(style="Normal")
        campo(cuerpo, instr, "Clic derecho → Actualizar campo para generar el índice.")

    # Secciones: preliminares en romanos (sin encabezado en la carátula) y cuerpo en arábigos
    previo = primer_cap._p.getprevious()
    ppr = previo.get_or_add_pPr() if hasattr(previo, "get_or_add_pPr") else None
    final = doc.sections[0]._sectPr
    import copy
    sect1 = copy.deepcopy(final)
    for hr in sect1.findall(qn("w:headerReference")) + sect1.findall(qn("w:footerReference")):
        sect1.remove(hr)
    if ppr is None:
        ppr = OxmlElement("w:pPr")
        previo.insert(0, ppr)
    ppr.append(sect1)
    primer_cap.paragraph_format.page_break_before = False
    s1, s2 = doc.sections[0], doc.sections[1]
    ancho = (s1.page_width - s1.left_margin - s1.right_margin) / 360000
    s1.different_first_page_header_footer = True
    encabezado(s1, ancho)
    encabezado(s2, ancho)
    numeracion_paginas(s1._sectPr, "lowerRoman", 1)
    numeracion_paginas(s2._sectPr, "decimal", 1)

    # Word actualiza índices y campos al abrir el documento
    ajustes = doc.settings.element
    uf = OxmlElement("w:updateFields")
    uf.set(qn("w:val"), "true")
    ajustes.append(uf)
    doc.save(ruta)


if __name__ == "__main__":
    main()
