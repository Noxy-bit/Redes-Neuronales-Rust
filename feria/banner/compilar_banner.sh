#!/usr/bin/env bash
# Regenera los banners 60x160 y 30x60 en PDF vectorial + vistas previas PNG.
# Uso: ./feria/banner/compilar_banner.sh [NRO_PROYECTO]   (por defecto 0)
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
RAIZ="$(cd "$DIR/../.." && pwd)"
mkdir -p "$DIR/build"
( cd "$RAIZ" && cargo test 2>&1 ) > "$DIR/build/cargo_test.txt" || { tail -30 "$DIR/build/cargo_test.txt"; exit 1; }
python3 "$DIR/generar_banner.py" --proy "${1:-0}"
