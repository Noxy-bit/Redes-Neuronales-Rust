#!/usr/bin/env bash
# Regenera los banners 60x160 y 30x60 en PDF vectorial + vistas previas PNG.
# Uso: ./feria/banner/compilar_banner.sh [NRO_PROYECTO]   (por defecto 38)
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
RAIZ="$(cd "$DIR/../.." && pwd)"
mkdir -p "$DIR/build"
[[ -f "$RAIZ/resultados/oficial/resumen.csv" ]] || python3 "$RAIZ/scripts/auditar_repo_oficial.py"
python3 "$DIR/generar_banner.py" --proy "${1:-38}"
