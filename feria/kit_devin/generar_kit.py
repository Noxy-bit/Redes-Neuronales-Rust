#!/usr/bin/env python3
"""Kit impreso del stand (Proy. #38): 5 credenciales 9×13 cm y tríptico Carta doble cara.

Reutiliza la identidad del banner oficial sin modificarlo: fuentes de feria/banner/fuentes/,
isotipo feria/banner/recursos/isotipo_rn.svg, sellos limpios de feria/banner/recursos/ y
QR feria/qr/qr_repositorio.svg. Las cifras del tríptico se leen de resultados/oficial/resumen.csv
y de Cargo.toml del repositorio oficial.

Genera HTML editable (credenciales/*.html, triptico/*.html), exporta PDF vectorial con
Chrome headless, renderiza PNG con pdftoppm y verifica medidas, páginas, QR legible y que
ningún texto desborde su caja ni invada las zonas seguras de pliegue.

Uso:  python3 feria/kit_devin/generar_kit.py
"""
import csv, json, math, re, shutil, subprocess, sys
from pathlib import Path

# ======================= PARÁMETROS EDITABLES (una línea cada uno) =======================
PROY_NUM = "38"
REPO_URL = "https://github.com/lanorrron/neural-network"
CREDENCIALES = [  # (Nombre, Apellido, rol): en el frente va SOLO nombre y apellido
    ("Ronal", "Miranda", "Expositor"),
    ("Oscar", "Nava", "Expositor"),
    ("Carla", "Cano", "Expositora"),
    ("Diana", "Diaz", "Expositora"),
    ("Julio", "Piuca", "Expositor"),
]
INTEGRANTES = ["Ronal Miranda Vasquez", "Oscar Alejandro Nava Orihuela", "Carla Olivia Cano Quispe",
               "Diana Nayely Diaz Mamani", "Julio Cesar Piuca Achocalla"]
MATERIA = "Programación 1 · INF120 · Grupo SH-SD"
DOCENTE = "MSc. Ing. Víctor Hugo Acosta Ortega"
CRED_MM = (90, 130)          # credencial vertical 9 × 13 cm
RANURA_MM = 15               # zona superior despejada para el cordón
CARTA_MM = (215.9, 279.4)    # Tamaño Carta
PLIEGUE_SEGURO_MM = 8        # margen mínimo a cada lado de los pliegues del tríptico
MAX_PALABRAS_PANEL = 45
# ==========================================================================================

DIR = Path(__file__).resolve().parent
RAIZ = DIR.parent.parent
RES = RAIZ / "resultados"
BANNER = RAIZ / "feria/banner"
BUILD = DIR / "build"
D_CRED = DIR / "credenciales"
D_TRIP = DIR / "triptico"


# ----------------------------------- Métricas reales -----------------------------------
def leer_csv(nombre):
    with open(RES / nombre, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sci(x):
    e = math.floor(math.log10(abs(x)))
    return f"{x / 10 ** e:.1f}×10<sup>−{-e}</sup>"


def pct(x):
    v = float(x) * 100
    return f"{v:.0f}&#8239;%" if abs(v - round(v)) < 1e-9 else f"{v:.1f}&#8239;%"


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
    r, _ = oficial()
    g = lambda k: float(r[k])
    return {
        "crates": r["crates_ml"],
        "kib": f"{g('binario_kib'):.1f}",
        "y2x": sci(g("lineal_mse_final")),
        "bool": pct(g("booleano_exactitud")),
        "voc": f"{round(g('vocales_exactitud') * 5)}/5",
        "ms": f"{g('computo_ms_vocales'):.1f}",
        "ms_epocas": r["vocales_epocas"],
    }


# ------------------------------------- Recursos -----------------------------------------
def svg_inline(ruta, clase):
    svg = Path(ruta).read_text(encoding="utf-8")
    svg = re.sub(r"<\?xml[^>]*\?>\s*", "", svg)
    m = re.search(r'<svg([^>]*?)\swidth="(\d+)" height="(\d+)"', svg)
    if m:
        svg = svg.replace(m.group(0), f'<svg{m.group(1)} viewBox="0 0 {m.group(2)} {m.group(3)}"', 1)
    return svg.replace("<svg", f'<svg class="{clase}"', 1)


def rel(ruta, desde):
    import os
    return os.path.relpath(ruta, desde).replace(os.sep, "/")


def css_base(desde):
    return f"""
@font-face{{font-family:"Montserrat";src:url("{rel(BANNER / 'fuentes/Montserrat.ttf', desde)}") format("truetype");font-weight:100 900}}
@font-face{{font-family:"Orbitron";src:url("{rel(BANNER / 'fuentes/Orbitron.ttf', desde)}") format("truetype");font-weight:400 900}}
:root{{--marino:#070B1E;--marino2:#0F1736;--cian:#00D4FF;--purpura:#A855F7;--rust:#F97316;--blanco:#FFFFFF;
  --gris:#CBD5E1;--gris2:#94A3B8;--tinta:#334155;--verde:#16A34A}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{-webkit-print-color-adjust:exact;print-color-adjust:exact;font-family:"Montserrat",sans-serif}}
.hoja{{position:relative;overflow:hidden;break-after:page}}
.hoja:last-child{{break-after:auto}}
svg text{{font-family:"Orbitron"}}
"""


def logos(desde):
    return {k: rel(BANNER / f"recursos/{n}.png", desde)
            for k, n in (("UAGRM", "logo_uagrm"), ("FICCT", "logo_ficct_escudo"), ("IICCT", "logo_iicct"))}


# JS de verificación: cada .caja (zona segura) debe contener a todos sus descendientes visibles.
VERIFICADOR = """<script>
addEventListener('load', async () => {
  await document.fonts.ready;
  const fallos = [];
  document.querySelectorAll('.caja').forEach((caja, i) => {
    const r = caja.getBoundingClientRect(), cs = getComputedStyle(caja);
    const z = {l: r.left + parseFloat(cs.paddingLeft) - .5, t: r.top + parseFloat(cs.paddingTop) - .5,
               r: r.right - parseFloat(cs.paddingRight) + .5, b: r.bottom - parseFloat(cs.paddingBottom) + .5};
    caja.querySelectorAll('*').forEach(el => {
      if (el.closest('svg') && el.tagName.toLowerCase() !== 'svg') return;
      const e = el.getBoundingClientRect();
      if (!e.width || !e.height) return;
      if (e.left < z.l || e.top < z.t || e.right > z.r || e.bottom > z.b)
        fallos.push((caja.dataset.nombre || 'caja ' + i) + ' → ' + el.tagName + ' «' + (el.textContent || '').trim().slice(0, 30) + '»');
    });
    if (caja.scrollHeight > caja.clientHeight + 1 || caja.scrollWidth > caja.clientWidth + 1)
      fallos.push((caja.dataset.nombre || 'caja ' + i) + ' → desborde de contenido');
  });
  const palabras = {};
  document.querySelectorAll('[data-panel]').forEach(p => {
    palabras[p.dataset.panel] = p.innerText.replace(/[·→←−=|•]/g, ' ').split(/\\s+/).filter(w => /[\\p{L}\\p{N}]/u.test(w)).length;
  });
  const pre = document.createElement('pre');
  pre.id = 'verificacion'; pre.style.display = 'none';
  const fuentes = [...document.fonts].map(f => f.family.replace(/"/g, '') + ':' + f.status);
  pre.textContent = JSON.stringify({fallos, palabras, fuentes});
  document.body.appendChild(pre);
});
</script>"""


# ------------------------------------ Credenciales --------------------------------------
def css_credencial():
    w, h = CRED_MM
    return f"""
.cred{{position:relative;width:{w}mm;height:{h}mm;overflow:hidden;color:#fff;
  background:radial-gradient(60mm 46mm at 50% 38%,rgba(0,212,255,.10),transparent 70%),
             linear-gradient(180deg,var(--marino2) 0%,var(--marino) 62%)}}
.ranura{{position:absolute;left:50%;top:5.2mm;width:15mm;height:3.6mm;transform:translateX(-50%);
  border:.25mm dashed rgba(203,213,225,.28);border-radius:2mm}}
.cred .caja{{position:absolute;left:7mm;right:7mm;top:{RANURA_MM}mm;bottom:5mm;display:flex;flex-direction:column;align-items:center}}
.franja{{width:100%;display:flex;justify-content:space-between;align-items:center;height:8mm}}
.franja .inst{{font-weight:700;font-size:6.6pt;letter-spacing:.2em;color:var(--gris)}}
.pill-proy{{font-family:"Orbitron";font-weight:800;font-size:6.6pt;letter-spacing:.08em;color:var(--cian);
  border:.3mm solid var(--cian);border-radius:3mm;padding:.9mm 2.4mm .8mm}}
.linea{{width:100%;height:.45mm;border-radius:1mm;background:linear-gradient(90deg,var(--cian),var(--purpura) 60%,var(--rust))}}
.cred .emblema{{width:33mm;height:33mm;margin-top:7mm}}
.nombre{{margin-top:5.5mm;text-align:center;font-weight:800;font-size:29pt;line-height:1.04;color:#fff;letter-spacing:-.005em}}
.rol{{margin-top:4.5mm;font-weight:700;font-size:7.6pt;letter-spacing:.3em;padding:1.5mm 4.2mm 1.4mm 5mm;
  color:var(--cian);border:.35mm solid rgba(0,212,255,.75);border-radius:4mm}}
.pie{{position:absolute;bottom:0;left:0;right:0;text-align:center;font-weight:700;font-size:6.2pt;letter-spacing:.24em;color:var(--gris2)}}
.pie b{{color:var(--rust);font-weight:800}}
.cred.reverso .caja{{justify-content:flex-start}}
.cta{{margin-top:4mm;font-weight:700;font-size:6.6pt;letter-spacing:.22em;color:var(--cian)}}
.qr-caja{{margin-top:3mm;width:50mm;height:50mm;background:#fff;border-radius:3.5mm;padding:2.5mm}}
.qr-caja svg{{width:100%;height:100%;display:block}}
.url{{margin-top:3mm;font-weight:600;font-size:6.4pt;color:var(--gris)}}
.sellos{{position:absolute;bottom:9mm;left:0;right:0;height:17mm;background:#fff;border-radius:3.5mm;
  display:flex;align-items:center;justify-content:space-evenly;padding:0 3mm}}
.sellos img{{display:block;object-fit:contain}}
.sellos .uagrm{{height:8.5mm}} .sellos .ficct{{height:13mm}} .sellos .iicct{{height:7mm}}
.sellos i{{width:.25mm;height:8mm;background:#D7DEE8}}
"""


def cred_frente(nombre, apellido, rol, emblema):
    return f"""<div class="cred frente"><div class="ranura"></div>
<div class="caja" data-nombre="frente {nombre}">
  <div class="franja"><span class="inst">FICCT · UAGRM</span><span class="pill-proy">PROY. #{PROY_NUM}</span></div>
  <div class="linea"></div>
  {emblema}
  <div class="nombre">{nombre}<br>{apellido}</div>
  <div class="rol">{rol.upper()}</div>
  <div class="pie">REDES NEURONALES EN <b>RUST</b></div>
</div></div>"""


def cred_reverso(qr, lg):
    return f"""<div class="cred reverso"><div class="ranura"></div>
<div class="caja" data-nombre="reverso">
  <div class="cta">ESCANEA EL REPOSITORIO</div>
  <div class="qr-caja">{qr}</div>
  <div class="url">{re.sub(r'^https?://', '', REPO_URL)}</div>
  <div class="sellos"><img class="uagrm" src="{lg['UAGRM']}" alt="UAGRM"><i></i>
    <img class="ficct" src="{lg['FICCT']}" alt="FICCT"><i></i><img class="iicct" src="{lg['IICCT']}" alt="IICCT"></div>
  <div class="pie">PROY. #{PROY_NUM} · FERIA FICCT 2-2026</div>
</div></div>"""


def html_doc(titulo, pagina_css, css, cuerpo):
    return f"""<!DOCTYPE html>
<!-- Generado por feria/kit_devin/generar_kit.py: edite los PARÁMETROS de ese script y regenere. -->
<html lang="es"><head><meta charset="UTF-8"><title>{titulo}</title>
<style>@page{{{pagina_css};margin:0}}{css}</style></head>
<body>{cuerpo}{VERIFICADOR}</body></html>"""


def credenciales():
    w, h = CRED_MM
    emblema = svg_inline(BANNER / "recursos/isotipo_rn.svg", "emblema")
    qr = svg_inline(RAIZ / "feria/qr/qr_repositorio.svg", "qr")
    css = css_base(D_CRED) + css_credencial()
    lg = logos(D_CRED)
    frentes = [cred_frente(n, a, r, emblema) for n, a, r in CREDENCIALES]
    reverso = cred_reverso(qr, lg)

    # PDF individual: frente y reverso intercalados (tiro y retiro a 9×13 cm).
    cuerpo = "".join(f'<section class="hoja" style="width:{w}mm;height:{h}mm">{f}</section>'
                     f'<section class="hoja" style="width:{w}mm;height:{h}mm">{reverso}</section>' for f in frentes)
    ind = D_CRED / "credenciales_individuales.html"
    ind.write_text(html_doc(f"Proy-{PROY_NUM} · Credenciales 9×13 cm", f"size:{w}mm {h}mm", css, cuerpo), encoding="utf-8")

    # Plancha Carta vertical 2×2 con marcas de corte; reverso espejado para dúplex por borde largo.
    cw, ch = CARTA_MM
    x0, y0 = (cw - 2 * w) / 2, (ch - 2 * h) / 2
    hojas = []
    grupos = [frentes[i:i + 4] for i in range(0, len(frentes), 4)]
    for g, grupo in enumerate(grupos):
        for cara in ("FRENTE", "REVERSO"):
            piezas, xs, ys = [], set(), set()
            for k, pieza in enumerate(grupo):
                fila, col = divmod(k, 2)
                if cara == "REVERSO":
                    col, pieza = 1 - col, reverso
                x, y = x0 + col * w, y0 + fila * h
                xs |= {x, x + w}; ys |= {y, y + h}
                piezas.append(f'<div style="position:absolute;left:{x:.2f}mm;top:{y:.2f}mm">{pieza}</div>')
            marcas = [f'<i class="m v" style="left:{x:.2f}mm;top:1.5mm"></i><i class="m v" style="left:{x:.2f}mm;bottom:1.5mm"></i>' for x in sorted(xs)]
            marcas += [f'<i class="m h" style="top:{y:.2f}mm;left:4mm"></i><i class="m h" style="top:{y:.2f}mm;right:4mm"></i>' for y in sorted(ys)]
            bx0, by0 = min(xs) - 2, min(ys) - 2
            sangrado = (f'<div class="sangrado" style="left:{bx0:.2f}mm;top:{by0:.2f}mm;'
                        f'width:{max(xs) - min(xs) + 4:.2f}mm;height:{max(ys) - min(ys) + 4:.2f}mm"></div>')
            n_hoja = len(hojas) + 1
            rotulo = (f'<div class="rot">Proy-{PROY_NUM} · Credenciales 9×13 · Hoja {n_hoja}/{2 * len(grupos)} · {cara}'
                      f'{" espejado (dúplex, borde largo)" if cara == "REVERSO" else ""}</div>')
            hojas.append(f'<section class="hoja carta">{sangrado}{"".join(piezas)}{"".join(marcas)}{rotulo}</section>')
    css_carta = css + f""".carta{{width:{cw}mm;height:{ch}mm;background:#fff}}
.m{{position:absolute;background:#000}} .m.v{{width:.12mm;height:{y0 - 4.5:.2f}mm;margin-left:-.06mm}}
.m.h{{height:.12mm;width:{x0 - 7:.2f}mm;margin-top:-.06mm}}
.sangrado{{position:absolute;background:#0A1028}}
.rot{{position:absolute;left:{x0 + 3:.2f}mm;bottom:2.6mm;font-size:5.5pt;color:#64748B;letter-spacing:.04em}}"""
    pl = D_CRED / "credenciales_plancha_carta.html"
    pl.write_text(html_doc(f"Proy-{PROY_NUM} · Credenciales · plancha Carta", "size:letter portrait", css_carta,
                           "".join(hojas)), encoding="utf-8")
    return ind, pl


# -------------------------------------- Tríptico ----------------------------------------
def svg_titulo():
    return """<svg class="titulo" viewBox="0 0 1000 420" xmlns="http://www.w3.org/2000/svg">
<text x="500" y="140" text-anchor="middle" font-weight="900" font-size="150" fill="#FFFFFF" textLength="640" lengthAdjust="spacingAndGlyphs">REDES</text>
<text x="500" y="285" text-anchor="middle" font-weight="900" font-size="128" fill="#00D4FF" textLength="900" lengthAdjust="spacingAndGlyphs">NEURONALES</text>
<text x="500" y="395" text-anchor="middle" font-weight="800" font-size="74" fill="#FFFFFF" textLength="900" lengthAdjust="spacingAndGlyphs">DESDE CERO EN <tspan fill="#F97316">RUST</tspan></text>
</svg>"""


def svg_red_clara():
    """Red 3-4-2 en versión clara (misma geometría y colores del banner)."""
    capas = [(120, [80, 170, 260], "#00D4FF"), (370, [50, 130, 210, 290], "#6366F1"), (620, [125, 215], "#A855F7")]
    lin, nod = [], []
    for (x1, ys1, _), (x2, ys2, _) in zip(capas, capas[1:]):
        lin += [f'<line x1="{x1}" y1="{a}" x2="{x2}" y2="{b}"/>' for a in ys1 for b in ys2]
    for x, ys, c in capas:
        nod += [f'<circle cx="{x}" cy="{y}" r="27" fill="{c}" opacity=".14"/><circle cx="{x}" cy="{y}" r="17" fill="#FFFFFF" '
                f'stroke="{c}" stroke-width="6"/><circle cx="{x}" cy="{y}" r="6.5" fill="{c}"/>' for y in ys]
    et = 'font-family="Montserrat" font-weight="800" font-size="25" fill="#070B1E" text-anchor="middle" letter-spacing="2"'
    return f"""<svg class="red" viewBox="0 0 740 380" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="gRC" x1="120" y1="0" x2="620" y2="0" gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="#00D4FF"/><stop offset="1" stop-color="#A855F7"/></linearGradient></defs>
<g stroke="url(#gRC)" stroke-width="3" opacity=".55">{''.join(lin)}</g>{''.join(nod)}
<text x="120" y="362" {et}>ENTRADA</text><text x="370" y="362" {et}>OCULTA</text><text x="620" y="362" {et}>SALIDA</text>
</svg>"""


ICONO_ESCUDO = """<svg viewBox="0 0 48 48" class="ico"><path d="M24 4 L40 10 V23 C40 33 33 40 24 44 C15 40 8 33 8 23 V10 Z"
 fill="none" stroke="#F97316" stroke-width="3.6" stroke-linejoin="round"/><path d="M16 24 L22 30 L33 18" fill="none"
 stroke="#F97316" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg>"""


def css_triptico():
    cw, ch = CARTA_MM[1], CARTA_MM[0]
    p = cw / 3
    s = PLIEGUE_SEGURO_MM + 1      # 9 mm junto al pliegue (≥ 8 mm exigidos)
    return f"""
.cara{{width:{cw}mm;height:{ch}mm;display:grid;grid-template-columns:repeat(3,{p:.3f}mm)}}
.ext{{background:radial-gradient(70mm 60mm at 83% 40%,rgba(0,212,255,.09),transparent 70%),
  linear-gradient(180deg,var(--marino2) 0%,var(--marino) 70%);color:#fff}}
.int{{background:#fff;color:var(--marino)}}
.panel{{position:relative;height:{ch}mm}}
.panel .caja{{position:absolute;top:12mm;bottom:11mm;display:flex;flex-direction:column}}
.panel.izq .caja{{left:10mm;right:{s}mm}} .panel.cen .caja{{left:{s}mm;right:{s}mm}} .panel.der .caja{{left:{s}mm;right:10mm}}
.pliegue{{position:absolute;width:.2mm;height:5mm;left:{p:.3f}mm}}
.pliegue.b{{left:{2 * p:.3f}mm}} .pliegue.top{{top:0}} .pliegue.bot{{bottom:0}}
.ext .pliegue{{background:rgba(203,213,225,.35)}} .int .pliegue{{background:#CBD5E1}}
.ceja{{font-family:"Orbitron";font-weight:800;font-size:8pt;letter-spacing:.14em;color:var(--rust)}}
.h2{{font-weight:800;font-size:17pt;line-height:1.12;margin-top:2mm}}
.ext .h2{{color:#fff}} .int .h2{{color:var(--marino)}}
.barra{{width:12mm;height:.9mm;border-radius:1mm;margin-top:3.5mm;background:linear-gradient(90deg,var(--cian),var(--purpura))}}
/* Portada */
.inst{{background:#fff;border-radius:3mm;height:15mm;display:flex;align-items:center;justify-content:space-evenly;padding:0 3mm}}
.inst img{{display:block;object-fit:contain}} .inst .uagrm{{height:8mm}} .inst .ficct{{height:12mm}} .inst .iicct{{height:6.5mm}}
.inst i{{width:.25mm;height:7mm;background:#D7DEE8}}
.portada{{align-items:center;text-align:center}}
.insignia{{margin-top:10mm;font-family:"Orbitron";font-weight:800;font-size:10pt;letter-spacing:.1em;color:#fff;
  padding:1.8mm 5mm 1.6mm;border-radius:4mm;background:linear-gradient(135deg,#7B2FF7,#3B5BFF 55%,var(--cian))}}
.portada .emblema{{width:40mm;height:40mm;margin-top:9mm}}
.portada .titulo{{width:68mm;margin-top:7mm}}
.eslogan{{margin-top:6mm;font-weight:800;font-size:7.6pt;letter-spacing:.26em;color:var(--cian)}}
.evento{{margin-top:auto;font-weight:600;font-size:6.6pt;letter-spacing:.18em;color:var(--gris2)}}
/* Contraportada */
.contra{{align-items:center;text-align:center}}
.contra .h2{{font-size:13.5pt;margin-top:0}}
.qr-caja{{margin-top:7mm;width:58mm;height:58mm;background:#fff;border-radius:4mm;padding:2.6mm}}
.qr-caja svg{{width:100%;height:100%;display:block}}
.url{{margin-top:3mm;font-weight:600;font-size:7pt;color:var(--cian)}}
.datos{{margin-top:auto;font-size:7.4pt;line-height:1.55;color:var(--gris)}}
.datos b{{color:#fff;font-weight:700}}
.equipo{{margin-top:6mm;font-weight:800;font-size:6.6pt;letter-spacing:.26em;color:var(--purpura)}}
.nombres{{margin-top:2.2mm;list-style:none;font-weight:600;font-size:8pt;line-height:1.6;color:#fff}}
/* Solapa */
.punto{{display:flex;flex-direction:column;margin-top:auto}}
.punto .cifra{{font-family:"Orbitron";font-weight:900;font-size:27pt;line-height:1}}
.punto .ico{{width:14mm;height:14mm;display:block}}
.punto .que{{margin-top:3mm;font-weight:800;font-size:11.5pt;color:#fff}}
.punto .det{{margin-top:1.2mm;font-size:8.6pt;color:var(--gris2);line-height:1.4}}
.c-cian{{color:var(--cian)}} .c-pur{{color:var(--purpura)}}
/* Interior */
.texto{{margin-top:7mm;font-size:9.8pt;line-height:1.5;color:var(--tinta)}}
.texto p+p{{margin-top:2.4mm}}
.texto b{{color:var(--marino)}}
.rotulo{{margin-top:auto;font-weight:800;font-size:6.6pt;letter-spacing:.26em;color:#64748B}}
.bloque{{margin-top:2.6mm;border-radius:2.6mm;padding:3.4mm 4mm;background:#F4F7FB;border-left:1.2mm solid var(--c)}}
.bloque code{{font-family:"JetBrains Mono","DejaVu Sans Mono",monospace;font-weight:700;font-size:9.4pt;color:var(--marino)}}
.bloque span{{display:block;margin-top:.6mm;font-size:7.6pt;color:#475569}}
.flecha{{align-self:center;margin-top:1.6mm;width:4mm;height:2.6mm}}
.cen .red{{width:100%;margin-top:auto}}
.pasos{{list-style:none;margin-top:auto}}
.pasos li{{display:flex;align-items:center;gap:3.2mm;margin-top:3.2mm}}
.pasos .n{{flex:none;width:7mm;height:7mm;border-radius:50%;background:var(--c);color:#fff;font-family:"Orbitron";
  font-weight:900;font-size:8.5pt;display:flex;align-items:center;justify-content:center}}
.pasos b{{display:block;font-size:9.6pt;color:var(--marino)}}
.pasos span{{display:block;font-size:7.8pt;color:#475569;margin-top:.3mm}}
.repite{{margin-top:4mm;font-size:7.4pt;color:var(--purpura);font-weight:700}}
.dv{{font-family:"DejaVu Sans";font-weight:700}}
.kpi{{margin-top:5mm;border-radius:2.8mm;padding:5mm 4mm;background:#F4F7FB;border-left:1.2mm solid var(--c);
  display:flex;align-items:center;justify-content:space-between;gap:3mm}}
.kpis{{margin-top:3mm}}
.kpi .v{{font-family:"Orbitron";font-weight:900;font-size:17pt;line-height:1;color:var(--c);white-space:nowrap}}
.kpi .v sup{{font-size:.55em;vertical-align:.75em;line-height:0}}
.kpi .l{{text-align:right;font-size:7.8pt;line-height:1.35;color:#475569}}
.kpi .l b{{display:block;font-size:9.6pt;color:var(--marino)}}
.tiempo{{margin-top:auto;display:flex;align-items:baseline;gap:3mm;border-top:.3mm solid #E2E8F0;padding-top:3.6mm}}
.tiempo .v{{font-family:"Orbitron";font-weight:900;font-size:15pt;color:var(--rust);white-space:nowrap}}
.tiempo span{{font-size:7.8pt;color:#475569;line-height:1.35}}
"""


def triptico(m):
    emblema = svg_inline(BANNER / "recursos/isotipo_rn.svg", "emblema")
    qr = svg_inline(RAIZ / "feria/qr/qr_repositorio.svg", "qr")
    lg = logos(D_TRIP)
    pliegues = ('<i class="pliegue top"></i><i class="pliegue bot"></i>'
                '<i class="pliegue b top"></i><i class="pliegue b bot"></i>')
    flecha = '<svg class="flecha" viewBox="0 0 16 10"><path d="M2 2 L8 8 L14 2" fill="none" stroke="#94A3B8" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    exterior = f"""<section class="hoja cara ext">{pliegues}
<div class="panel izq"><div class="caja" data-nombre="solapa" data-panel="Solapa">
  <div class="ceja">RUST PURO</div>
  <div class="h2">¿Por qué en<br>Rust puro?</div><div class="barra"></div>
  <div class="punto"><span class="cifra c-cian">{m['crates']}</span><span class="que">librerías de ML</span>
    <span class="det">Álgebra lineal propia, escrita desde cero.</span></div>
  <div class="punto"><span class="cifra c-pur">{m['kib']}&nbsp;KiB</span><span class="que">binario completo</span>
    <span class="det">Compilado en modo <i>release</i>.</span></div>
  <div class="punto">{ICONO_ESCUDO}<span class="que">Memoria segura</span>
    <span class="det">Sin GPU ni recolector de basura.</span></div>
</div></div>
<div class="panel cen"><div class="caja contra" data-nombre="contraportada" data-panel="Contraportada">
  <div class="h2">Escanea para ver<br>el código y la tesis</div>
  <div class="qr-caja">{qr}</div>
  <div class="url">{re.sub(r'^https?://', '', REPO_URL)}</div>
  <div class="datos">{MATERIA}<br>Tutor: <b>{DOCENTE}</b></div>
  <div class="equipo">EQUIPO</div>
  <ul class="nombres">{''.join(f'<li>{n}</li>' for n in INTEGRANTES)}</ul>
</div></div>
<div class="panel der"><div class="caja portada" data-nombre="portada" data-panel="Portada">
  <div class="inst" style="width:100%"><img class="uagrm" src="{lg['UAGRM']}" alt="UAGRM"><i></i>
    <img class="ficct" src="{lg['FICCT']}" alt="FICCT"><i></i><img class="iicct" src="{lg['IICCT']}" alt="IICCT"></div>
  <div class="insignia">PROY. #{PROY_NUM}</div>
  {emblema}
  {svg_titulo()}
  <div class="eslogan">ANALIZA · APRENDE · PREDICE</div>
  <div class="evento">FERIA FICCT 2-2026</div>
</div></div>
</section>"""
    interior = f"""<section class="hoja cara int">{pliegues}
<div class="panel izq"><div class="caja" data-nombre="interior izquierdo" data-panel="Interior izquierdo">
  <div class="ceja">01</div>
  <div class="h2">Romper la<br>caja negra</div><div class="barra"></div>
  <div class="texto"><p>Usamos IA a diario sin ver <b>cómo&nbsp;aprende</b>.</p>
    <p>Programamos una red neuronal <b>desde&nbsp;cero</b>, sin frameworks.</p>
    <p>Cada ecuación es código Rust legible y trazable.</p></div>
  <div class="rotulo">ARQUITECTURA</div>
  <div class="bloque" style="--c:var(--cian)"><code>math</code><span>Vector · Matrix</span></div>{flecha}
  <div class="bloque" style="--c:var(--purpura)"><code>neural</code><span>Neuron · Layer · MSE</span></div>{flecha}
  <div class="bloque" style="--c:var(--rust)"><code>experiments</code><span>y = 2x · Booleano · Vocales</span></div>
</div></div>
<div class="panel cen"><div class="caja" data-nombre="interior central" data-panel="Interior central">
  <div class="ceja">02</div>
  <div class="h2">¿Cómo aprende<br>la red?</div><div class="barra"></div>
  {svg_red_clara()}
  <ol class="pasos">
    <li style="--c:#00D4FF"><span class="n">1</span><div><b>Datos</b><span>Entradas x y objetivo y</span></div></li>
    <li style="--c:#3B82F6"><span class="n">2</span><div><b>Forward</b><span>ŷ = σ(W·x + b)</span></div></li>
    <li style="--c:#A855F7"><span class="n">3</span><div><b>Gradiente</b><span>Error MSE y ∇ de pesos</span></div></li>
    <li style="--c:#F97316"><span class="n">4</span><div><b>Predicción</b><span>La red reconoce</span></div></li>
  </ol>
  <div class="repite">↻ Repite: W <span class="dv">←</span> W − α·∇</div>
</div></div>
<div class="panel der"><div class="caja" data-nombre="interior derecho" data-panel="Interior derecho">
  <div class="ceja">03</div>
  <div class="h2">Resultados<br>reales</div><div class="barra"></div>
  <div class="kpis">
  <div class="kpi" style="--c:var(--verde)"><span class="v">3</span><span class="l"><b>experimentos</b>en vivo</span></div>
  <div class="kpi" style="--c:#00A9CC"><span class="v">{m['y2x']}</span><span class="l"><b>y = 2x</b>error MSE</span></div>
  <div class="kpi" style="--c:var(--purpura)"><span class="v">{m['bool']}</span><span class="l"><b>Booleano</b>0 falso · 1 verdadero</span></div>
  <div class="kpi" style="--c:var(--rust)"><span class="v">{m['voc']}</span><span class="l"><b>Vocales</b>patrones 5×5</span></div>
  </div>
  <div class="tiempo"><span class="v">{m['ms']}&#8239;ms</span><span>entrena las vocales durante {m['ms_epocas']} épocas</span></div>
</div></div>
</section>"""
    css = css_base(D_TRIP) + css_triptico()
    ruta = D_TRIP / "triptico.html"
    ruta.write_text(html_doc(f"Proy-{PROY_NUM} · Tríptico Carta", "size:letter landscape", css, exterior + interior),
                    encoding="utf-8")
    return ruta


# ----------------------------------- Exportación ----------------------------------------
def chrome():
    for n in ("google-chrome", "chromium", "chromium-browser", "google-chrome-stable"):
        if shutil.which(n):
            return shutil.which(n)
    sys.exit("Se requiere Google Chrome o Chromium")


def exportar(html, pdf):
    args = [chrome(), "--headless=new", "--disable-gpu", "--allow-file-access-from-files",
            "--run-all-compositor-stages-before-draw", "--virtual-time-budget=15000"]
    subprocess.run(args + ["--no-pdf-header-footer", f"--print-to-pdf={pdf}", html.as_uri()], check=True, capture_output=True)
    dom = subprocess.run(args + ["--dump-dom", html.as_uri()], check=True, capture_output=True, text=True).stdout
    v = re.search(r'<pre id="verificacion"[^>]*>(.*?)</pre>', dom, re.S)
    assert v, f"{html.name}: el verificador de maquetación no se ejecutó"
    import html as h
    return json.loads(h.unescape(v.group(1)))


def verificar_pdf(pdf, paginas, ancho_mm, alto_mm):
    import pymupdf
    doc = pymupdf.open(pdf)
    assert len(doc) == paginas, f"{pdf.name}: {len(doc)} páginas (se esperaban {paginas})"
    for p in doc:
        w, h = p.rect.width * 25.4 / 72, p.rect.height * 25.4 / 72
        assert abs(w - ancho_mm) < .8 and abs(h - alto_mm) < .8, f"{pdf.name}: página {w:.1f}×{h:.1f} mm"
    return sum(len(p.get_fonts()) for p in doc)


def png(pdf, pagina, salida, dpi=150):
    base = BUILD / f"{pdf.stem}_p{pagina}"
    subprocess.run(["pdftoppm", "-png", "-r", str(dpi), "-f", str(pagina), "-l", str(pagina), "-singlefile",
                    str(pdf), str(base)], check=True)
    shutil.move(f"{base}.png", salida)
    return salida


def leer_qr(ruta, cantidad=1):
    import cv2
    img = cv2.imread(str(ruta))
    det = cv2.QRCodeDetector()
    textos = det.detectAndDecodeMulti(img)[1] if cantidad > 1 else [det.detectAndDecode(img)[0]]
    assert list(textos).count(REPO_URL) == cantidad, f"QR ilegible en {ruta.name} (leído: {textos!r})"
    return ruta


def main():
    BUILD.mkdir(exist_ok=True)
    D_CRED.mkdir(exist_ok=True)
    D_TRIP.mkdir(exist_ok=True)
    m = metricas()
    print("Cifras reales:", {k: re.sub(r"<[^>]+>|&#8239;", "", str(v)) for k, v in m.items()})

    ind_html, pl_html = credenciales()
    trip_html = triptico(m)
    trabajos = [
        (ind_html, D_CRED / f"Proy-{PROY_NUM}-CREDENCIALES-INDIVIDUALES.pdf", 2 * len(CREDENCIALES), CRED_MM),
        (pl_html, D_CRED / f"Proy-{PROY_NUM}-CREDENCIALES-IMPRIMIR-CARTA.pdf", 2 * math.ceil(len(CREDENCIALES) / 4), CARTA_MM),
        (trip_html, D_TRIP / f"Proy-{PROY_NUM}-TRIPTICO.pdf", 2, (CARTA_MM[1], CARTA_MM[0])),
    ]
    for html, pdf, n, (w, h) in trabajos:
        v = exportar(html, pdf)
        assert not v["fallos"], f"{html.name}: texto fuera de zona segura:\n  " + "\n  ".join(v["fallos"])
        for panel, k in v["palabras"].items():
            assert k <= MAX_PALABRAS_PANEL, f"{panel}: {k} palabras (> {MAX_PALABRAS_PANEL})"
        for req in ("Montserrat:loaded", "Orbitron:loaded"):
            assert req in v["fuentes"], f"{html.name}: fuente no cargada ({v['fuentes']})"
        verificar_pdf(pdf, n, w, h)
        extra = f", palabras por panel {v['palabras']}" if v["palabras"] else ""
        print(f"{pdf.relative_to(RAIZ)}: {n} págs. de {w / 10:g}×{h / 10:g} cm, sin desbordes{extra}; Montserrat y Orbitron incrustadas")

    # Vistas previas (pdftoppm) y lectura del QR en cada pieza.
    from PIL import Image
    ind = trabajos[0][1]
    f, r = png(ind, 1, BUILD / "frente.png", 300), png(ind, 2, BUILD / "reverso.png", 300)
    leer_qr(r)
    a, b = Image.open(f), Image.open(r)
    sep = 60
    lienzo = Image.new("RGB", (a.width + b.width + sep * 3, a.height + sep * 2), "#E2E8F0")
    lienzo.paste(a, (sep, sep)); lienzo.paste(b, (a.width + 2 * sep, sep))
    lienzo.save(D_CRED / "preview_credencial.png", optimize=True)
    for i in range(1, 2 * len(CREDENCIALES) + 1, 2):
        png(ind, i, BUILD / f"frente_{(i + 1) // 2}.png", 120)
    leer_qr(png(trabajos[1][1], 2, BUILD / "plancha_reverso.png", 200), min(4, len(CREDENCIALES)))
    png(trabajos[1][1], 1, D_CRED / "preview_plancha.png", 110)
    trip = trabajos[2][1]
    leer_qr(png(trip, 1, D_TRIP / "preview_triptico_ext.png", 150))
    png(trip, 2, D_TRIP / "preview_triptico_int.png", 150)
    print("QR legible en credencial, plancha y tríptico; vistas previas PNG generadas con pdftoppm.")


if __name__ == "__main__":
    main()
