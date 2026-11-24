#!/usr/bin/env bash
# Regenera credenciales y tríptico (PDF + PNG) con el conteo real de cargo test.
# Uso: ./feria/kit_devin/compilar_kit.sh
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
RAIZ="$(cd "$DIR/../.." && pwd)"
mkdir -p "$DIR/build"
[[ -f "$RAIZ/resultados/oficial/resumen.csv" ]] || python3 "$RAIZ/scripts/auditar_repo_oficial.py"
python3 "$DIR/generar_kit.py"
