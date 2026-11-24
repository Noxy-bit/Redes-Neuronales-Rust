#!/usr/bin/env python3
"""Genera la identidad definitiva del isotipo RN en `feria/logos/`.

Salidas (todas regenerables con `python3 feria/logos/generar_logos.py [NRO]`):
  logo_rn_oscuro.svg/.png   versión para fondos oscuros (PNG transparente, 300 DPI)
  logo_rn_claro.svg/.png    versión para fondos blancos y documentos (PNG transparente, 300 DPI)
  logo_rn_isotipo_puro.svg  símbolo sin texto
  Proy-<NRO>-LOGO.PDF       entregable oficial (2 páginas, Carta)
El emblema es el mismo del banner (`feria/banner/recursos/isotipo_rn.svg`).
"""
import base64
import subprocess
import sys
import tempfile
from pathlib import Path

PROY_NUM = sys.argv[1] if len(sys.argv) > 1 else "38"
DIR = Path(__file__).resolve().parent
RAIZ = DIR.parent.parent
FUENTES = RAIZ / "feria" / "banner" / "fuentes"
PX = 2000  # 2000 px a 300 DPI = 16.9 cm de lado

NODOS = {"entrada": ([(150, 150), (150, 225), (150, 300)], "#00D4FF"),
         "oculta": ([(250, 110), (250, 180), (250, 250), (250, 320)], "#6366F1"),
         "salida": ([(350, 185), (350, 265)], "#C084FC")}


def emblema(tema="oscuro", texto=True):
    claro = tema == "claro"
    fondo = ('<radialGradient id="gF" cx=".5" cy=".42" r=".6"><stop offset="0" stop-color="#FFFFFF"/>'
             '<stop offset="1" stop-color="#EEF2FF"/></radialGradient>') if claro else (
            '<radialGradient id="gF" cx=".5" cy=".42" r=".6"><stop offset="0" stop-color="#1A2A66"/>'
            '<stop offset="1" stop-color="#0A1027"/></radialGradient>')
    nucleo = "#FFFFFF" if claro else "#0B122B"
    centro_salida = "#7B2FF7" if claro else "#FFFFFF"
    dy = 0 if texto else 22
    s = ['<svg viewBox="0 0 500 500" width="500" height="500" xmlns="http://www.w3.org/2000/svg">',
         '<defs><linearGradient id="gC" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#00D4FF"/>'
         '<stop offset=".5" stop-color="#3B82F6"/><stop offset="1" stop-color="#A855F7"/></linearGradient>'
         '<linearGradient id="gL" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#00D4FF"/>'
         f'<stop offset="1" stop-color="#A855F7"/></linearGradient>{fondo}</defs>',
         '<circle cx="250" cy="250" r="244" fill="#00D4FF" opacity=".08"/>',
         '<circle cx="250" cy="250" r="232" fill="url(#gF)" stroke="url(#gC)" stroke-width="12"/>',
         f'<circle cx="250" cy="250" r="208" fill="none" stroke="{"#0891B2" if claro else "#00D4FF"}" '
         'stroke-opacity=".3" stroke-width="2.5" stroke-dasharray="10 9"/>',
         f'<g transform="translate(0 {dy})">',
         f'<g stroke="url(#gL)" stroke-width="4" stroke-linecap="round" opacity="{".9" if claro else ".8"}">']
    capas = list(NODOS.values())
    for (a, _), (b, _) in zip(capas, capas[1:]):
        for x1, y1 in a:
            for x2, y2 in b:
                s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    s.append("</g>")
    for nombre, (pts, c) in NODOS.items():
        for x, y in pts:
            centro = centro_salida if nombre == "salida" else c
            s.append(f'<circle cx="{x}" cy="{y}" r="30" fill="{c}" opacity=".16"/>'
                     f'<circle cx="{x}" cy="{y}" r="17" fill="{nucleo}" stroke="{c}" stroke-width="6"/>'
                     f'<circle cx="{x}" cy="{y}" r="7" fill="{centro}"/>')
    s.append(f'<ellipse cx="250" cy="{398 - dy * 0.6:.0f}" rx="168" ry="34" fill="none" stroke="#00D4FF" '
             f'stroke-width="4" opacity=".55" transform="rotate(-7 250 {398 - dy * 0.6:.0f})"/>')
    if texto:
        s.append(f'<text x="250" y="436" text-anchor="middle" font-family="Orbitron" font-weight="900" '
                 f'font-size="104" fill="{"#0F1736" if claro else "#FFFFFF"}" letter-spacing="6">RN</text>')
    s.append(f'<circle cx="414" cy="{378 - dy * 0.6:.0f}" r="7" fill="#F97316"/>')
    s.append("</g></svg>\n")
    sufijo = f"{tema[0]}{'t' if texto else 'p'}"
    svg = "".join(s)
    for i in ("gC", "gL", "gF"):
        svg = svg.replace(f'id="{i}"', f'id="{i}{sufijo}"').replace(f"url(#{i})", f"url(#{i}{sufijo})")
    return svg


def fuente_css():
    b64 = base64.b64encode((FUENTES / "Orbitron.ttf").read_bytes()).decode()
    m64 = base64.b64encode((FUENTES / "Montserrat.ttf").read_bytes()).decode()
    return (f'@font-face{{font-family:"Orbitron";src:url(data:font/ttf;base64,{b64})}}'
            f'@font-face{{font-family:"Montserrat";src:url(data:font/ttf;base64,{m64})}}')


def chrome(*args):
    for nombre in ("google-chrome", "chromium", "chromium-browser"):
        try:
            subprocess.run([nombre, "--headless=new", "--disable-gpu", "--hide-scrollbars", *args],
                           check=True, capture_output=True, timeout=120)
            return
        except FileNotFoundError:
            continue
    raise SystemExit("No se encontró Chrome/Chromium para exportar")


def png(svg, destino):
    html = (f'<html><head><style>{fuente_css()}html,body{{margin:0;background:transparent}}'
            f'svg{{width:{PX}px;height:{PX}px;display:block}}</style></head><body>{svg}</body></html>')
    with tempfile.TemporaryDirectory() as tmp:
        h = Path(tmp) / "logo.html"
        h.write_text(html, encoding="utf-8")
        chrome(f"--window-size={PX},{PX}", "--default-background-color=00000000",
               "--force-device-scale-factor=1", f"--screenshot={destino}", h.as_uri())
    from PIL import Image
    with Image.open(destino) as im:
        im.load()
        im.save(destino, dpi=(300, 300))


PALETA = [("#070B1E", "Marino profundo", "Fondo: el espacio de datos"),
          ("#00D4FF", "Cian eléctrico", "Capa de entrada y flujo de datos"),
          ("#6366F1", "Índigo", "Capa oculta: transformación"),
          ("#A855F7", "Púrpura neón", "Capa de salida: predicción"),
          ("#F97316", "Naranja Rust", "Rust como lenguaje base"),
          ("#FFFFFF", "Blanco", "Monograma y legibilidad")]

GEOMETRIA = [("Nodos 3 → 4 → 2", "Red multicapa real: entrada, capa oculta y salida conectadas por completo (W·x + b)."),
             ("Degradado cian → púrpura", "Dirección de la propagación hacia adelante, de los datos a la predicción."),
             ("Anillo punteado", "Épocas: el entrenamiento repite el ciclo forward → backward → update."),
             ("Órbita inclinada", "Trayectoria del descenso de gradiente que converge al mínimo de la pérdida."),
             ("Punto naranja", "La red está implementada desde cero en Rust estándar (std)."),
             ("Círculo cerrado", "Sistema autocontenido y abierto: sin librerías externas de ML.")]


def pdf(svg_puro, svg_claro, svg_oscuro, destino):
    pal = "".join(f'<div class="sw"><span style="background:{c}"></span><div><b>{n}</b><code>{c}</code>'
                  f'<small>{u}</small></div></div>' for c, n, u in PALETA)
    geo = "".join(f"<tr><th>{t}</th><td>{d}</td></tr>" for t, d in GEOMETRIA)
    html = f"""<html><head><meta charset="utf-8"><style>{fuente_css()}
@page{{size:Letter;margin:0}}*{{box-sizing:border-box}}
body{{margin:0;font-family:"Montserrat";color:#0F1736}}
.pag{{width:8.5in;height:11in;padding:.75in;display:flex;flex-direction:column;page-break-after:always}}
.pag:last-child{{page-break-after:auto}}
h1{{font-family:"Orbitron";font-weight:900;font-size:22pt;letter-spacing:.06em;margin:0}}
h2{{font-family:"Orbitron";font-weight:800;font-size:12pt;letter-spacing:.12em;margin:0 0 .12in;color:#475569}}
.cab{{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:2px solid #0F1736;padding-bottom:.12in;margin-bottom:.3in}}
.cab span{{font-family:"Orbitron";font-weight:800;font-size:12pt}}
.puro{{flex:1;display:flex;align-items:center;justify-content:center}}
.puro svg{{width:4.1in;height:4.1in}}
.duo{{display:flex;gap:.3in}}
.duo div{{flex:1;border-radius:.18in;display:flex;align-items:center;justify-content:center;height:3in}}
.duo svg{{width:2.5in;height:2.5in}}
.et{{display:flex;gap:.3in;margin-top:.08in;font-size:9pt;color:#475569}}.et span{{flex:1;text-align:center}}
.sw{{display:flex;gap:.14in;align-items:center;width:48%}}
.sw span{{width:.62in;height:.62in;border-radius:.1in;border:1px solid #CBD5E1;flex:none}}
.sw b{{display:block;font-size:11pt}}.sw code{{font-size:10pt;color:#334155}}.sw small{{display:block;font-size:9pt;color:#64748B}}
.pal{{display:flex;flex-wrap:wrap;gap:.22in .2in;margin-bottom:.4in}}
table{{border-collapse:collapse;width:100%;font-size:10pt}}th{{text-align:left;width:2.1in;padding:.09in .1in .09in 0;vertical-align:top}}
td{{padding:.09in 0;color:#334155}}tr{{border-top:1px solid #E2E8F0}}
.uso{{margin-top:auto;font-size:9pt;color:#64748B;border-top:1px solid #E2E8F0;padding-top:.12in}}
</style></head><body>
<section class="pag"><div class="cab"><h1>RN · REDES NEURONALES</h1><span>PROY. #{PROY_NUM}</span></div>
<h2>ISOTIPO</h2><div class="puro">{svg_puro}</div>
<h2>MONOGRAMA RN</h2>
<div class="duo"><div style="background:#FFFFFF;border:1px solid #CBD5E1">{svg_claro}</div>
<div style="background:#070B1E">{svg_oscuro}</div></div>
<div class="et"><span>Versión clara · documentos académicos</span><span>Versión oscura · banner, credenciales y pantallas</span></div>
</section>
<section class="pag"><div class="cab"><h1>FICHA TÉCNICA</h1><span>PROY. #{PROY_NUM}</span></div>
<h2>PALETA</h2><div class="pal">{pal}</div>
<h2>GEOMETRÍA Y SIGNIFICADO</h2><table>{geo}</table>
<p class="uso">Archivos fuente: logo_rn_oscuro.svg · logo_rn_claro.svg · logo_rn_isotipo_puro.svg (vectoriales) y PNG transparente a 300 DPI.
Tipografía del monograma: Orbitron Black. Área de protección mínima: 1/8 del diámetro alrededor del círculo.</p>
</section></body></html>"""
    with tempfile.TemporaryDirectory() as tmp:
        h = Path(tmp) / "logo.html"
        h.write_text(html, encoding="utf-8")
        chrome("--no-pdf-header-footer", f"--print-to-pdf={destino}", h.as_uri())


def main():
    oscuro, claro, puro = emblema("oscuro"), emblema("claro"), emblema("oscuro", texto=False)
    for nombre, svg in [("logo_rn_oscuro", oscuro), ("logo_rn_claro", claro), ("logo_rn_isotipo_puro", puro)]:
        (DIR / f"{nombre}.svg").write_text(svg, encoding="utf-8")
    png(oscuro, DIR / "logo_rn_oscuro.png")
    png(claro, DIR / "logo_rn_claro.png")
    destino = DIR / f"Proy-{PROY_NUM}-LOGO.PDF"
    pdf(puro, claro, oscuro, destino)
    for f in sorted(DIR.glob("logo_rn_*")) + [destino]:
        print(f"  {f.relative_to(RAIZ)}  ({f.stat().st_size // 1024} KiB)")


if __name__ == "__main__":
    main()
