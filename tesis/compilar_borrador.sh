#!/usr/bin/env bash
# Compila el borrador de sala: tesis/build/Proy-<NUM>-Borrador-Sala.pdf
set -euo pipefail
cd "$(dirname "$0")"
RAIZ=..
NUM=$(sed -n 's/.*\\ProyNum}{\(.*\)}/\1/p' config_caratula.tex)
( cd "$RAIZ" && cargo run --release -q -- --all > /dev/null )
( cd "$RAIZ" && cargo test 2>&1 | grep -E "^(running|test |test result)" | sed 's/^test result/RESULTADO/' ) > generado/cargo_test.txt
python3 scripts/bibliografia.py
python3 scripts/resultados.py
python3 scripts/extraer_codigo.py
mkdir -p build
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build/aux borrador_sala.tex > build/aux_latexmk.log 2>&1 || { tail -40 build/aux_latexmk.log; exit 1; }
cp build/aux/borrador_sala.pdf "build/Proy-${NUM}-Borrador-Sala.pdf"
echo "PDF: tesis/build/Proy-${NUM}-Borrador-Sala.pdf"
