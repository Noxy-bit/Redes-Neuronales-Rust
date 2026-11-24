#!/usr/bin/env bash
# Compila el Documento Final Oficial: tesis/build/Proy-<NUM>-Doc-Final.PDF y .docx
# Uso: bash tesis/compilar_final.sh [--experimentos]   (--experimentos vuelve a ejecutar el binario y regenera los CSV)
set -euo pipefail
cd "$(dirname "$0")"
RAIZ=..
NUM=$(sed -n 's/.*\\ProyNum}{\(.*\)}/\1/p' config_caratula.tex)
if [[ "${1:-}" == "--experimentos" ]]; then
  ( cd "$RAIZ" && cargo run --release -q -- --all > /dev/null && python3 scripts/generar_graficas.py )
fi
( cd "$RAIZ" && cargo test 2>&1 | grep -E "^(running|test |test result)" ) > generado/cargo_test.txt
( cd "$RAIZ" && touch src/lib.rs && cargo clippy --all-targets 2>&1 | sed -E "s#$HOME#~#g; s/in [0-9.]+s$/in <t>/" ) > generado/cargo_clippy.txt
python3 scripts/bibliografia.py
python3 scripts/resultados.py
python3 scripts/extraer_codigo.py
python3 scripts/anexo_codigo.py
mkdir -p build
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build/aux documento_final.tex > build/aux_latexmk.log 2>&1 || { tail -40 build/aux_latexmk.log; exit 1; }
if grep -E "LaTeX Warning: (Reference|Citation).*undefined|Rerun to get cross" build/aux/documento_final.log; then
  echo "ERROR: referencias sin resolver"; exit 1
fi
cp build/aux/documento_final.pdf "build/Proy-${NUM}-Doc-Final.PDF"
python3 scripts/generar_docx.py build/docx/pandoc.docx
# LibreOffice actualiza índices y paginación del DOCX y exporta un PDF de verificación
python3 scripts/actualizar_indices_docx.py build/docx/pandoc.docx "build/Proy-${NUM}-Doc-Final.docx" build/docx/verificacion_docx.pdf
echo "PDF:  tesis/build/Proy-${NUM}-Doc-Final.PDF"
echo "DOCX: tesis/build/Proy-${NUM}-Doc-Final.docx"
