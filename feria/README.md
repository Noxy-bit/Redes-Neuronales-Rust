# Kit gráfico de la Feria FICCT 2-2026

## Banner oficial del stand (`feria/banner/`)

| Archivo | Descripción |
|---|---|
| `Proy-<NUM>-BANNER-60x160.pdf` | Roll-up vertical 60 × 160 cm (PDF vectorial, 1 página). |
| `Proy-<NUM>-BANNER-30x60.pdf` | Banner de mesa 30 × 60 cm (PDF vectorial, 1 página). |
| `banner_template.html` | Plantilla HTML/CSS editable (textos, colores y maquetación). |
| `generar_banner.py` | Generador: lee las métricas de `resultados/*.csv`, crea los SVG (isotipo, red, flujo, QR) y exporta los PDF. |
| `compilar_banner.sh` | Ejecuta `cargo test` y regenera ambos formatos. |
| `preview_60x160.png`, `preview_30x60.png` | Vistas previas para verificación visual. |
| `recursos/` | Isotipo RN en SVG y recortes de los sellos institucionales. |
| `fuentes/` | Montserrat y Orbitron (licencia SIL OFL). |

Regenerar con otro número de proyecto:

```bash
./feria/banner/compilar_banner.sh 38   # produce Proy-38-BANNER-*.pdf
```

Requisitos: Rust (cargo), Python 3 con `segno`, `pymupdf`, `opencv-python-headless` y Google Chrome/Chromium.

Edición:
- `PROY_NUM`, `REPO_URL`, medidas, materia, docente e integrantes: cabecera de `generar_banner.py` (una línea cada uno). Para otra medida, añadir una entrada en `FORMATOS`.
- Textos fijos y estilos: `banner_template.html`.
- Las métricas no se escriben a mano: se leen de `resultados/resumen.csv`, `resultados/benchmarks.csv`, `Cargo.toml` y la salida de `cargo test`.
- Si el contenido no cabe en la página, el generador reduce la escala global automáticamente y verifica 1 página, medidas exactas y QR legible.

## QR del repositorio (`feria/qr/`)

`qr_repositorio.svg` y `qr_repositorio.png` apuntan a https://github.com/Noxy-bit/Redes-Neuronales-Rust.
