#!/usr/bin/env bash
# Regenera credenciales y tríptico (PDF + PNG) con el conteo real de cargo test.
# Uso: ./feria/kit_devin/compilar_kit.sh
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
RAIZ="$(cd "$DIR/../.." && pwd)"
mkdir -p "$DIR/build"
( cd "$RAIZ" && cargo test 2>&1 ) > "$DIR/build/cargo_test.txt" || { tail -30 "$DIR/build/cargo_test.txt"; exit 1; }
python3 "$DIR/generar_kit.py"
