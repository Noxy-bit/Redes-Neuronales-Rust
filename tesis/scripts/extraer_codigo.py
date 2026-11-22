#!/usr/bin/env python3
"""Extrae funciones reales del código Rust para incluirlas como listados en la tesis."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "tesis/generado/codigo"
SALIDA.mkdir(parents=True, exist_ok=True)

EXTRACTOS = {
    "matmul": ("src/math/matrix.rs", "pub fn matmul("),
    "sigmoid": ("src/nn/activation.rs", "impl ActivationFn for Sigmoid"),
    "mse": ("src/nn/loss.rs", "impl LossFn for Mse"),
    "layer_forward": ("src/nn/layer.rs", "pub fn forward("),
    "layer_backward": ("src/nn/layer.rs", "pub fn backward("),
    "train_step": ("src/nn/network.rs", "pub fn train_step("),
    "rng": ("src/math/rng.rs", "pub fn next_u64("),
}


def extraer(ruta, firma):
    lineas = (RAIZ / ruta).read_text(encoding="utf-8").splitlines()
    ini = next(i for i, l in enumerate(lineas) if firma in l)
    while ini > 0 and lineas[ini - 1].strip().startswith(("///", "#[")):
        ini -= 1
    prof, fin, abierto = 0, None, False
    for j in range(ini, len(lineas)):
        codigo = lineas[j].split("//")[0]
        prof += codigo.count("{") - codigo.count("}")
        abierto |= "{" in codigo
        if abierto and prof == 0:
            fin = j
            break
    bloque = lineas[ini:fin + 1]
    sangria = min(len(l) - len(l.lstrip()) for l in bloque if l.strip())
    return "\n".join(l[sangria:] for l in bloque) + "\n"


for nombre, (ruta, firma) in EXTRACTOS.items():
    (SALIDA / f"{nombre}.rs").write_text(extraer(ruta, firma).replace("≫", ">>"), encoding="utf-8")
print("extractos:", ", ".join(EXTRACTOS))
