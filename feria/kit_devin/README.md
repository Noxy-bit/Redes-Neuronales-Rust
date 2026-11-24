# Kit impreso del stand — Proy. #38 (`feria/kit_devin/`)

Propuesta de credenciales y tríptico con la misma identidad del banner oficial (paleta, Montserrat/Orbitron,
isotipo RN, QR y sellos de `feria/banner/recursos/`). No modifica el banner, los logos ni la tesis.

| Archivo | Descripción |
|---|---|
| `credenciales/Proy-38-CREDENCIALES-INDIVIDUALES.pdf` | 10 págs. de 9 × 13 cm: frente y reverso intercalados por integrante (tiro y retiro). |
| `credenciales/Proy-38-CREDENCIALES-IMPRIMIR-CARTA.pdf` | 4 hojas Carta: 2 × 2 credenciales con marcas de corte y 2 mm de sangrado; las hojas de reverso van espejadas para dúplex por borde largo. |
| `credenciales/preview_credencial.png`, `preview_plancha.png` | Vistas previas (pdftoppm). |
| `triptico/Proy-38-TRIPTICO.pdf` | Carta apaisada, 2 págs. (cara exterior e interior), 3 cuerpos de 9.31 cm con marcas de pliegue. |
| `triptico/preview_triptico_ext.png`, `preview_triptico_int.png` | Vistas previas (pdftoppm). |
| `*/*.html` | Fuentes editables (generadas; los textos se editan en `generar_kit.py`). |

Regenerar: `./feria/kit_devin/compilar_kit.sh` (requiere cargo, Python 3 con `pymupdf`, `opencv-python-headless`,
`pillow`, Google Chrome/Chromium y `pdftoppm` de poppler-utils).

Edición: nombres, roles, integrantes, materia, docente, número de proyecto y medidas están en la cabecera de
`generar_kit.py` (una línea cada uno). Las cifras del tríptico (52 pruebas, MSE, exactitudes, 51.9 ms, 682.6 KiB)
se leen de `resultados/*.csv`, `Cargo.toml` y la salida de `cargo test`.

Verificación automática en cada ejecución: medidas y número de páginas exactos, fuentes cargadas, QR legible,
ningún texto fuera de su zona segura (franja de 1.5 cm para el cordón, ≥ 0.8 cm junto a cada pliegue) y
≤ 45 palabras por panel del tríptico.
