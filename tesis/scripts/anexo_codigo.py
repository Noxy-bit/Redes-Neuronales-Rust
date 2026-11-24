#!/usr/bin/env python3
"""Genera tesis/generado/anexo_codigo.tex con el código fuente completo de src/ y Cargo.toml."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "tesis/generado/anexo_codigo.tex"

GRUPOS = [
    ("Configuración del paquete y punto de entrada", ["Cargo.toml", "src/lib.rs", "src/main.rs"]),
    ("Módulo \\texttt{math}: álgebra lineal y utilidades",
     ["src/math/mod.rs", "src/math/error.rs", "src/math/vector.rs", "src/math/matrix.rs", "src/math/rng.rs"]),
    ("Módulo \\texttt{nn}: red neuronal",
     ["src/nn/mod.rs", "src/nn/activation.rs", "src/nn/loss.rs", "src/nn/neuron.rs", "src/nn/layer.rs",
      "src/nn/network.rs"]),
    ("Módulo \\texttt{experiments}: experimentos y exportación",
     ["src/experiments/mod.rs", "src/experiments/csv.rs", "src/experiments/exp1_y2x.rs",
      "src/experiments/exp2_xor.rs", "src/experiments/exp3_vocales.rs", "src/experiments/prueba_escritorio.rs",
      "src/experiments/benchmarks.rs"]),
]


def tex(s):
    return s.replace("_", "\\_")


faltantes = sorted(str(p.relative_to(RAIZ)) for p in (RAIZ / "src").rglob("*.rs")
                   if str(p.relative_to(RAIZ)) not in {f for _, fs in GRUPOS for f in fs})
if faltantes:
    raise SystemExit(f"archivos sin incluir en el anexo: {faltantes}")

out = ["% Generado por tesis/scripts/anexo_codigo.py — no editar a mano."]
total = 0
for titulo, archivos in GRUPOS:
    out.append(f"\\section{{{titulo}}}")
    lineas = {a: len((RAIZ / a).read_text(encoding="utf-8").splitlines()) for a in archivos}
    out.append("Esta sección contiene " + ", ".join(
        f"\\texttt{{{tex(a)}}} ({n} líneas)" for a, n in lineas.items()) + ".")
    for a in archivos:
        total += lineas[a]
        lang = "TOML" if a.endswith(".toml") else "Rust"
        out.append(f"\\lstinputlisting[language={lang},style=anexo,caption={{Archivo \\texttt{{{tex(a)}}}}},"
                   f"label=cod:src:{a.replace('/', ':')}]{{../{a}}}")
(SALIDA.parent / "anexo_codigo_macros.tex").write_text(f"\\newcommand{{\\LineasFuente}}{{{total}}}\n", encoding="utf-8")
SALIDA.write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"anexo_codigo.tex: {total} líneas de código")
