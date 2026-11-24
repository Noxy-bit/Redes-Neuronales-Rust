#!/usr/bin/env python3
"""Generador del banner oficial del stand (RN · Redes Neuronales desde Cero en Rust).

Rellena banner_template.html con métricas del repositorio oficial (resultados/oficial/resumen.csv),
exporta cada formato a PDF vectorial con Chrome headless,
renderiza una vista previa PNG y verifica página única, medida exacta y QR legible.

Uso:  python3 feria/banner/generar_banner.py [--proy N] [--repo URL]
"""
import argparse, base64, csv, io, math, re, shutil, subprocess, sys
from pathlib import Path

# ======================= PARÁMETROS EDITABLES (una línea cada uno) =======================
PROY_NUM = "38"
REPO_URL = "https://github.com/lanorrron/neural-network"
FORMATOS = {  # nombre: (ancho_cm, alto_cm, ajustes de maquetación en rem = 1 % del ancho)
    "60x160": (60, 160, dict(lateral=5, franja=13, hueco=2.6, emblema=26, titulo=84, red=70, flujo=86,
                             qr=32, cta=4.6, cifra=8, cifra_exp=5.6, kpi_pad=2.2, seguro_inf=9)),
    "30x60": (30, 60, dict(lateral=5, franja=12, hueco=1.6, emblema=16, titulo=80, red=56, flujo=80,
                           qr=24, cta=4.2, cifra=6.5, cifra_exp=5, kpi_pad=1.6, seguro_inf=4)),
}  # Si el contenido no cabe, el generador reduce la escala global automáticamente (--escala).
MATERIA = "Programación 1 · INF120 · Grupo SH-SD"
DOCENTE = "MSc. Ing. Víctor Hugo Acosta Ortega"
INTEGRANTES = ["Ronal Miranda Vasquez", "Oscar Alejandro Nava Orihuela", "Carla Olivia Cano Quispe",
               "Diana Nayely Diaz Mamani", "Julio Cesar Piuca Achocalla"]
# ==========================================================================================

DIR = Path(__file__).resolve().parent
RAIZ = DIR.parent.parent
RES = RAIZ / "resultados"
BUILD = DIR / "build"


# ----------------------------------- Métricas reales -----------------------------------
def leer_csv(nombre):
    with open(RES / nombre, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sci(x, dec=1):
    e = math.floor(math.log10(abs(x)))
    return f"{x / 10 ** e:.{dec}f}×10<sup>−{-e}</sup>" if e < 0 else f"{x:.{dec}f}"


def pct(x):
    v = float(x) * 100
    return f"{v:.0f}&#8239;%" if abs(v - round(v)) < 1e-9 else f"{v:.1f}&#8239;%"


def miles(n):
    return f"{int(n):,}".replace(",", "&#8239;")


CRATES_ML = {"ndarray", "nalgebra", "candle-core", "candle-nn", "burn", "tch", "tensorflow", "linfa",
             "smartcore", "dfdx", "tract-onnx", "ort", "autograd", "rusty-machine", "juice"}


def oficial():
    """Métricas del repositorio oficial (scripts/auditar_repo_oficial.py -> resultados/oficial/resumen.csv)."""
    ruta = RAIZ / "resultados/oficial/resumen.csv"
    if not ruta.exists():
        sys.exit("Falta resultados/oficial/resumen.csv: ejecute scripts/auditar_repo_oficial.py")
    with open(ruta, newline="", encoding="utf-8") as f:
        r = {fila["metrica"]: fila["valor"] for fila in csv.DictReader(f)}
    deps, seccion = [], None
    for linea in (RAIZ / "repo_oficial/neural-network/Cargo.toml").read_text(encoding="utf-8").splitlines():
        linea = linea.split("#")[0].strip()
        if linea.startswith("["):
            seccion = linea.strip("[]")
        elif linea and "=" in linea and seccion and seccion.endswith("dependencies"):
            deps.append(linea.split("=")[0].strip())
    r["crates_ml"] = str(sum(d in CRATES_ML for d in deps))
    return r, ruta

def metricas():
    r, fuente = oficial()
    g = lambda k: float(r[k])
    m = {
        "CRATES_ML": r["crates_ml"],
        "EXPERIMENTOS": "3",
        "Y2X_VAL": f"MSE {sci(g('lineal_mse_final'))}",
        "Y2X_DET": f"peso aprendido w = {r['lineal_peso']}<br>"
                   f"{miles(r['lineal_epocas'])} épocas · α = {r['lineal_alpha']}",
        "BOOL_VAL": pct(g("booleano_exactitud")),
        "BOOL_DET": f"P(verdadero | 1) = {g('booleano_p1'):.2f}<br>"
                   f"P(verdadero | 0) = {g('booleano_p0'):.2f}",
        "VOC_VAL": pct(g("vocales_exactitud")),
        "VOC_DET": f"patrones 5×5 · softmax<br>"
                   f"confianza <span style=\"white-space:nowrap\">{g('vocales_confianza_min'):.1f}–{g('vocales_confianza_max'):.1f}&#8239;%</span>",
        "BENCH_VAL": f"{g('computo_ms_vocales'):.1f}&#8239;ms",
        "BENCH_QUE": f"entrena la red de vocales 25&#8239;→&#8239;5 durante {miles(r['vocales_epocas'])} épocas",
        "BENCH_DET": f"<code>--release</code> · sin pausas de demostración"
                     f" · binario de {g('binario_kib'):.0f}&#8239;KiB",
    }
    return m, fuente


# ------------------------------------- Recursos -----------------------------------------
def data_uri(ruta, mime):
    return f"data:{mime};base64," + base64.b64encode(Path(ruta).read_bytes()).decode()


def preparar_logos():
    """Recorta márgenes y lleva a blanco puro el fondo casi blanco de los sellos."""
    import numpy as np
    from PIL import Image
    salida = {}
    for clave, nombre in (("UAGRM", "logo_uagrm"), ("FICCT", "logo_ficct_escudo"), ("IICCT", "logo_iicct")):
        im = np.array(Image.open(RAIZ / f"assets/logos/{nombre}.jpeg").convert("RGB")).astype(int)
        fondo = im.min(axis=2) > 232
        im[fondo] = 255
        ys, xs = np.where(~fondo)
        pad = 12
        im = im[max(ys.min() - pad, 0):ys.max() + pad, max(xs.min() - pad, 0):xs.max() + pad]
        ruta = DIR / f"recursos/{nombre}.png"
        Image.fromarray(im.astype("uint8")).save(ruta, optimize=True)
        salida[f"LOGO_{clave}"] = data_uri(ruta, "image/png")
    return salida


def svg_qr(url):
    import segno
    qr = segno.make(url, error="q")
    buf = io.BytesIO()
    qr.save(buf, kind="svg", scale=10, border=4, dark="#070B1E", light="#FFFFFF",
            xmldecl=False, svgns=True, nl=False)
    svg = buf.getvalue().decode()
    (RAIZ / "feria/qr").mkdir(parents=True, exist_ok=True)
    qr.save(RAIZ / "feria/qr/qr_repositorio.svg", scale=10, border=4, dark="#070B1E")
    qr.save(RAIZ / "feria/qr/qr_repositorio.png", scale=40, border=4, dark="#070B1E")
    return re.sub(r'width="(\d+)" height="(\d+)"', r'viewBox="0 0 \1 \2"', svg, count=1)


GRADS = """<linearGradient id="gC" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#00D4FF"/>
<stop offset=".5" stop-color="#3B82F6"/><stop offset="1" stop-color="#A855F7"/></linearGradient>"""


def svg_isotipo():
    capas = [(150, [150, 225, 300]), (250, [110, 180, 250, 320]), (350, [185, 265])]
    lineas, nodos = [], []
    for (x1, ys1), (x2, ys2) in zip(capas, capas[1:]):
        for y1 in ys1:
            for y2 in ys2:
                lineas.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    colores = ["#00D4FF", "#6366F1", "#C084FC"]
    for (x, ys), c in zip(capas, colores):
        for y in ys:
            nodos.append(f'<circle cx="{x}" cy="{y}" r="30" fill="{c}" opacity=".16"/>'
                         f'<circle cx="{x}" cy="{y}" r="17" fill="#0B122B" stroke="{c}" stroke-width="6"/>'
                         f'<circle cx="{x}" cy="{y}" r="7" fill="{"#FFFFFF" if x == 350 else c}"/>')
    return f"""<svg class="emblema" viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg">
<defs>{GRADS}
<linearGradient id="gL" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#00D4FF"/><stop offset="1" stop-color="#A855F7"/></linearGradient>
<radialGradient id="gF" cx=".5" cy=".42" r=".6"><stop offset="0" stop-color="#1A2A66"/><stop offset="1" stop-color="#0A1027"/></radialGradient></defs>
<circle cx="250" cy="250" r="244" fill="#00D4FF" opacity=".08"/>
<circle cx="250" cy="250" r="232" fill="url(#gF)" stroke="url(#gC)" stroke-width="12"/>
<circle cx="250" cy="250" r="208" fill="none" stroke="#00D4FF" stroke-opacity=".3" stroke-width="2.5" stroke-dasharray="10 9"/>
<g stroke="url(#gL)" stroke-width="4" stroke-linecap="round" opacity=".8">{''.join(lineas)}</g>
{''.join(nodos)}
<ellipse cx="250" cy="398" rx="168" ry="34" fill="none" stroke="#00D4FF" stroke-width="4" opacity=".55" transform="rotate(-7 250 398)"/>
<text x="250" y="436" text-anchor="middle" font-family="Orbitron" font-weight="900" font-size="104" fill="#FFFFFF" letter-spacing="6">RN</text>
<circle cx="414" cy="378" r="7" fill="#F97316"/>
</svg>"""


def svg_titulo():
    return """<svg class="titulo" viewBox="0 0 1000 420" xmlns="http://www.w3.org/2000/svg">
<text x="500" y="140" text-anchor="middle" font-family="Orbitron" font-weight="900" font-size="150" fill="#FFFFFF" textLength="640" lengthAdjust="spacingAndGlyphs">REDES</text>
<text x="500" y="285" text-anchor="middle" font-family="Orbitron" font-weight="900" font-size="128" fill="#00D4FF" textLength="900" lengthAdjust="spacingAndGlyphs">NEURONALES</text>
<text x="500" y="395" text-anchor="middle" font-family="Orbitron" font-weight="800" font-size="74" fill="#FFFFFF" textLength="900" lengthAdjust="spacingAndGlyphs">DESDE CERO EN <tspan fill="#F97316">RUST</tspan></text>
</svg>"""


def svg_red():
    capas = [(170, [130, 250, 370], "#00D4FF"), (500, [70, 160, 250, 340, 430], "#6366F1"), (830, [190, 310], "#C084FC")]
    lineas, nodos = [], []
    for (x1, ys1, _), (x2, ys2, _) in zip(capas, capas[1:]):
        for y1 in ys1:
            for y2 in ys2:
                lineas.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    for x, ys, c in capas:
        for y in ys:
            nodos.append(f'<circle cx="{x}" cy="{y}" r="40" fill="{c}" opacity=".13"/>'
                         f'<circle cx="{x}" cy="{y}" r="26" fill="#0B122B" stroke="{c}" stroke-width="7"/>'
                         f'<circle cx="{x}" cy="{y}" r="10" fill="{c}"/>')
    rot = 'font-family="Montserrat" font-weight="800" font-size="30" fill="#FFFFFF" text-anchor="middle" letter-spacing="2"'
    sub = 'font-family="JetBrains Mono" font-weight="700" font-size="22" fill="#94A3B8" text-anchor="middle"'
    flecha = 'stroke="#00D4FF" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    return f"""<svg class="red" viewBox="0 0 1000 560" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="gE" x1="170" y1="0" x2="830" y2="0" gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="#00D4FF"/><stop offset="1" stop-color="#A855F7"/></linearGradient></defs>
<g stroke="url(#gE)" stroke-width="3.2" opacity=".6">{''.join(lineas)}</g>
{''.join(nodos)}
<text x="170" y="508" {rot}>ENTRADA</text><text x="170" y="545" {sub}>x</text>
<text x="500" y="508" {rot}>CAPA OCULTA</text><text x="500" y="545" {sub}>a = σ(W·x + b)</text>
<text x="830" y="508" {rot}>SALIDA</text><text x="830" y="545" {sub}>ŷ</text>
<path d="M258 498 H362 M350 487 L364 498 L350 509" {flecha}/>
<path d="M636 498 H740 M728 487 L742 498 L728 509" {flecha}/>
</svg>"""


def svg_flujo():
    pasos = [("Datos", "#00D4FF"), ("Forward Pass", "#00D4FF"), ("Gradiente", "#A855F7"), ("Predicción", "#F97316")]
    iconos = [
        '<ellipse cx="0" cy="-14" rx="24" ry="8" {s}/><path d="M-24 -14 V14 A24 8 0 0 0 24 14 V-14" {s}/><path d="M-24 0 A24 8 0 0 0 24 0" {s}/>',
        '<circle cx="-22" cy="-12" r="6" {f}/><circle cx="-22" cy="12" r="6" {f}/><circle cx="22" cy="0" r="7" {f}/>'
        '<path d="M-16 -10 L15 -1 M-16 10 L15 1" {s}/><path d="M30 -10 L40 0 L30 10" {s}/>',
        '<path d="M20 -14 A24 24 0 1 0 24 6" {s}/><path d="M10 -20 L22 -14 L14 -2" {s}/>',
        '<circle cx="0" cy="0" r="24" {s}/><circle cx="0" cy="0" r="13" {s}/><circle cx="0" cy="0" r="4" {f}/>',
    ]
    partes = []
    for i, ((nombre, c), ico) in enumerate(zip(pasos, iconos)):
        x = i * 265
        s = f'fill="none" stroke="{c}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"'
        f = f'fill="{c}"'
        ajuste = ' textLength="182" lengthAdjust="spacingAndGlyphs"' if len(nombre) > 12 else ""
        partes.append(
            f'<rect x="{x + 3}" y="3" width="199" height="154" rx="24" fill="#0F1736" stroke="{c}" stroke-width="4"/>'
            f'<circle cx="{x + 30}" cy="30" r="15" fill="{c}"/>'
            f'<text x="{x + 30}" y="37" text-anchor="middle" font-family="Orbitron" font-weight="900" font-size="18" fill="#070B1E">{i + 1}</text>'
            f'<g transform="translate({x + 102} 62)">{ico.format(s=s, f=f)}</g>'
            f'<text x="{x + 102}" y="130" text-anchor="middle" font-family="Montserrat" font-weight="800" font-size="25" fill="#FFFFFF"{ajuste}>{nombre}</text>')
        if i < 3:
            partes.append(f'<path d="M{x + 214} 80 H{x + 250} M{x + 240} 70 L{x + 252} 80 L{x + 240} 90" '
                          'fill="none" stroke="#00D4FF" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    return f"""<svg class="flujo" viewBox="0 0 1000 262" xmlns="http://www.w3.org/2000/svg">
{''.join(partes)}
<path d="M632 162 C632 222 367 222 367 172" fill="none" stroke="#A855F7" stroke-width="4.5" stroke-dasharray="12 9" stroke-linecap="round"/>
<path d="M357 182 L367 166 L377 182" fill="none" stroke="#A855F7" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>
<text x="500" y="254" text-anchor="middle" font-family="Montserrat" font-weight="600" font-size="22" fill="#CBD5E1">actualiza W y b con descenso de gradiente y repite</text>
</svg>"""


def svg_fondo(alto_u):
    """Fondo vectorial: retícula de puntos, halos, pistas de circuito y ondas de partículas."""
    p = []
    for cx, cy, r, c, o in ((88, alto_u * .17, 38, "#00D4FF", .16), (8, alto_u * .42, 45, "#7B2FF7", .2),
                            (92, alto_u * .66, 40, "#7B2FF7", .14), (20, alto_u * .9, 40, "#00D4FF", .12)):
        p.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="url(#h{c[1:]})" opacity="{o}"/>')

    def pista(x, y, sx, color):
        return (f'<path d="M{x} {y} h{6 * sx} l{2.5 * sx} 2.5 v{9} l{1.5 * sx} 1.5 h{2 * sx}" fill="none" '
                f'stroke="{color}" stroke-width=".22" opacity=".45"/>'
                f'<circle cx="{x + 10 * sx}" cy="{y + 13}" r=".55" fill="none" stroke="{color}" stroke-width=".22" opacity=".6"/>')
    for k, fy in enumerate((.2, .36, .55, .74)):
        y = alto_u * fy
        p.append(pista(0, y, 1, "#00D4FF" if k % 2 == 0 else "#F97316"))
        p.append(pista(100, y + 6, -1, "#A855F7" if k % 2 == 0 else "#00D4FF"))
    puntos = []
    for onda, (amp, fase, base, color) in enumerate(((3, 0, .5, "#00D4FF"), (4, 1.3, .51, "#A855F7"), (2.5, 2.4, .52, "#5B7CFF"))):
        for i in range(0, 101, 2):
            y = alto_u * base + amp * math.sin(i / 100 * 2 * math.pi * 1.3 + fase)
            o = .12 + .25 * (0.5 + 0.5 * math.sin(i / 9 + onda))
            puntos.append(f'<circle cx="{i}" cy="{y:.2f}" r=".22" fill="{color}" opacity="{o:.2f}"/>')
    return f"""<svg class="fondo" viewBox="0 0 100 {alto_u:.2f}" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
<defs><pattern id="ret" width="3" height="3" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r=".12" fill="#FFFFFF" opacity=".09"/></pattern>
<radialGradient id="h00D4FF"><stop offset="0" stop-color="#00D4FF"/><stop offset="1" stop-color="#00D4FF" stop-opacity="0"/></radialGradient>
<radialGradient id="h7B2FF7"><stop offset="0" stop-color="#7B2FF7"/><stop offset="1" stop-color="#7B2FF7" stop-opacity="0"/></radialGradient></defs>
<rect width="100" height="{alto_u:.2f}" fill="url(#ret)"/>{''.join(p)}{''.join(puntos)}
</svg>"""


# -------------------------------------- Exportación --------------------------------------
def buscar_chrome():
    for nombre in ("google-chrome", "chromium", "chromium-browser", "google-chrome-stable"):
        if shutil.which(nombre):
            return shutil.which(nombre)
    sys.exit("Se requiere Google Chrome o Chromium para exportar el PDF")


def exportar_pdf(html, pdf):
    subprocess.run([buscar_chrome(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--run-all-compositor-stages-before-draw", "--virtual-time-budget=15000",
                    f"--print-to-pdf={pdf}", html.as_uri()], check=True, capture_output=True)


def paginas(pdf):
    import pymupdf
    return len(pymupdf.open(pdf))


def verificar(pdf, ancho, alto, preview):
    import pymupdf
    doc = pymupdf.open(pdf)
    pag = doc[0]
    esperado = (ancho / 2.54 * 72, alto / 2.54 * 72)
    assert len(doc) == 1, f"{pdf.name}: {len(doc)} páginas (contenido desbordado)"
    assert abs(pag.rect.width - esperado[0]) < 2 and abs(pag.rect.height - esperado[1]) < 2, \
        f"{pdf.name}: medida {pag.rect} distinta de {esperado}"
    pag.get_pixmap(dpi=round(2400 / (alto / 2.54))).save(preview)
    estado_qr = "no verificado (instale opencv-python-headless)"
    try:
        import cv2, numpy as np
        pix = pag.get_pixmap(dpi=round(4000 / (alto / 2.54)))
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
        texto, _, _ = cv2.QRCodeDetector().detectAndDecode(np.ascontiguousarray(img[:, :, ::-1]))
        assert texto == REPO_URL, f"QR ilegible en {pdf.name} (leído: {texto!r})"
        estado_qr = "legible"
    except ImportError:
        pass
    fuentes = sorted({f[3] for f in pag.get_fonts()})
    return estado_qr, fuentes


def main():
    global REPO_URL
    ap = argparse.ArgumentParser()
    ap.add_argument("--proy", default=PROY_NUM)
    ap.add_argument("--repo", default=REPO_URL)
    a = ap.parse_args()
    REPO_URL = a.repo
    BUILD.mkdir(exist_ok=True)
    m, fuente_tests = metricas()
    comunes = {
        "PROY_NUM": a.proy, "MATERIA": MATERIA, "DOCENTE": DOCENTE,
        "INTEGRANTES": "Integrantes: " + " · ".join(n.replace(" ", "&nbsp;") for n in INTEGRANTES),
        "REPO_CORTO": re.sub(r"^https?://", "", REPO_URL),
        "FUENTE_MONTSERRAT": data_uri(DIR / "fuentes/Montserrat.ttf", "font/ttf"),
        "FUENTE_ORBITRON": data_uri(DIR / "fuentes/Orbitron.ttf", "font/ttf"),
        "SVG_QR": svg_qr(REPO_URL), "SVG_ISOTIPO": svg_isotipo(), "SVG_TITULO": svg_titulo(),
        "SVG_RED": svg_red(), "SVG_FLUJO": svg_flujo(), **preparar_logos(), **m,
    }
    (DIR / "recursos/isotipo_rn.svg").write_text(svg_isotipo().replace(' class="emblema"', ""), encoding="utf-8")
    plantilla = (DIR / "banner_template.html").read_text(encoding="utf-8")
    print(f"Métricas reales del repositorio oficial ({fuente_tests.relative_to(RAIZ)}):")
    for k, v in m.items():
        print(f"  {k:10s} {re.sub(r'<[^>]+>', ' ', v).replace('&#8239;', ' ')}")
    for nombre, (ancho, alto, aj) in FORMATOS.items():
        ruta_html = BUILD / f"banner_{nombre}.html"
        pdf = DIR / f"Proy-{a.proy}-BANNER-{nombre}.pdf"

        def construir(escala):
            variables = " ".join(f"--{k.replace('_', '-')}:{v}rem;" for k, v in aj.items())
            valores = {**comunes, "FORMATO": nombre.replace("x", "×"), "ANCHO_CM": str(ancho),
                       "ALTO_CM": str(alto), "VARIABLES_FORMATO": f"--escala:{escala:.3f}; {variables}",
                       "SVG_FONDO": svg_fondo(100 * alto / ancho)}
            ruta_html.write_text(re.sub(r"\{\{(\w+)\}\}", lambda x: valores[x.group(1)], plantilla),
                                 encoding="utf-8")
            exportar_pdf(ruta_html, pdf)
            return paginas(pdf) == 1

        # Búsqueda binaria de la mayor escala (≤ 1) con la que todo cabe en una sola página.
        bajo, alto_e = 0.5, 1.0
        if not construir(alto_e):
            for _ in range(6):
                medio = (bajo + alto_e) / 2
                if construir(medio):
                    bajo = medio
                else:
                    alto_e = medio
            escala = bajo * 0.97
            assert construir(escala), f"{nombre}: no cabe ni a escala {escala:.2f}"
        else:
            escala = 1.0
        print(f"{nombre}: escala de contenido {escala:.3f}")
        qr, fuentes = verificar(pdf, ancho, alto, DIR / f"preview_{nombre}.png")
        print(f"{pdf.relative_to(RAIZ)}: {ancho}×{alto} cm, 1 página, QR {qr}, fuentes: {', '.join(fuentes)}")


if __name__ == "__main__":
    main()
