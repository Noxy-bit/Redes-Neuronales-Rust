#!/usr/bin/env python3
"""Genera tesis/generado/anexo_codigo.tex con el código fuente completo de src/ y Cargo.toml."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "tesis/generado/anexo_codigo.tex"

SALIDA_FUENTE = RAIZ / "tesis/generado/fuente"
GRUPOS = [
    ("Configuración del paquete y biblioteca", ["Cargo.toml", "src/lib.rs"]),
    ("Módulo \\texttt{math}: álgebra lineal y utilidades",
     ["src/math/mod.rs", "src/math/error.rs", "src/math/vector.rs", "src/math/matrix.rs", "src/math/rng.rs"]),
    ("Módulo \\texttt{nn}: red neuronal",
     ["src/nn/mod.rs", "src/nn/activation.rs", "src/nn/loss.rs", "src/nn/neuron.rs", "src/nn/layer.rs",
      "src/nn/network.rs"]),
]


def produccion(ruta: str) -> str:
    """Código de producción: se excluye el módulo #[cfg(test)] (las pruebas se reportan en el Anexo A)."""
    lineas = (RAIZ / ruta).read_text(encoding="utf-8").splitlines()
    corte = next((i for i, l in enumerate(lineas) if l.strip() == "#[cfg(test)]"), len(lineas))
    lineas = lineas[:corte]
    while lineas and not lineas[-1].strip():
        lineas.pop()
    return "\n".join(lineas) + "\n"


def tex(s):
    return s.replace("_", "\\_")


out = ["% Generado por tesis/scripts/anexo_codigo.py — no editar a mano."]
total = 0
for titulo, archivos in GRUPOS:
    out.append(f"\\section{{{titulo}}}")
    lineas = {}
    for a in archivos:
        destino = SALIDA_FUENTE / a
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(produccion(a), encoding="utf-8")
        lineas[a] = len(destino.read_text(encoding="utf-8").splitlines())
    out.append("Esta sección contiene " + ", ".join(
        f"\\texttt{{{tex(a)}}} ({n} líneas)" for a, n in lineas.items()) + ".")
    for a in archivos:
        total += lineas[a]
        lang = "TOML" if a.endswith(".toml") else "Rust"
        out.append(f"\\lstinputlisting[language={lang},style=anexo,caption={{Archivo \\texttt{{{tex(a)}}}}},"
                   f"label=cod:src:{a.replace('/', ':')}]{{generado/fuente/{a}}}")
(SALIDA.parent / "anexo_codigo_macros.tex").write_text(f"\\newcommand{{\\LineasFuente}}{{{total}}}\n", encoding="utf-8")
SALIDA.write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"anexo_codigo.tex: {total} líneas de código de producción")
