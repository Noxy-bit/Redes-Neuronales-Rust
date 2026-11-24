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
    "shuffle": ("src/math/rng.rs", "pub fn shuffle<"),
    "dot": ("src/math/vector.rs", "pub fn dot("),
    "argmax": ("src/math/vector.rs", "pub fn argmax("),
    "mul_vector": ("src/math/matrix.rs", "pub fn mul_vector("),
    "outer": ("src/math/matrix.rs", "pub fn outer("),
    "relu": ("src/nn/activation.rs", "impl ActivationFn for ReLU"),
    "activation_enum": ("src/nn/activation.rs", "pub enum Activation"),
    "neuron_forward": ("src/nn/neuron.rs", "pub fn forward("),
    "layer_new": ("src/nn/layer.rs", "pub fn new("),
    "apply_gradients": ("src/nn/layer.rs", "pub fn apply_gradients("),
    "network_new": ("src/nn/network.rs", "pub fn new("),
    "network_backward": ("src/nn/network.rs", "pub fn backward("),
    "train_callback": ("src/nn/network.rs", "pub fn train_with_callback<"),
    "con_ruido": ("src/experiments/exp3_vocales.rs", "pub fn con_ruido("),
    "confusion": ("src/experiments/exp3_vocales.rs", "pub fn matriz_confusion("),
    "csv_row": ("src/experiments/csv.rs", "pub fn write_row("),
    "parsear": ("src/main.rs", "fn parsear("),
}
OF = "repo_oficial/neural-network/src/"
EXTRACTOS.update({  # repositorio oficial lanorrron/neural-network
    "of_activacion": (OF + "neural/activation.rs", "impl Activacion"),
    "of_mse": (OF + "learning/loss.rs", "impl MSE"),
    "of_gradient": (OF + "learning/gradient.rs", "impl Gradient"),
    "of_optimizer": (OF + "learning/optimizer.rs", "impl GradientDescent"),
    "of_neuron_struct": (OF + "neural/neuron.rs", "pub struct Neuron"),
    "of_neuron": (OF + "neural/neuron.rs", "pub fn forward("),
    "of_layer": (OF + "neural/layer.rs", "pub fn forward("),
    "of_network": (OF + "neural/network.rs", "pub fn forward("),
    "of_dot": (OF + "math/vector.rs", "pub fn dot("),
    "of_multiply": (OF + "math/matrix.rs", "pub fn multiply("),
    "of_softmax": (OF + "experiments/vowels.rs", "fn softmax("),
    "of_encode": (OF + "experiments/vowels.rs", "fn encode("),
    "of_argmax": (OF + "experiments/vowels.rs", "fn argmax("),
    "of_parse": (OF + "experiments/vowels.rs", "fn parse_vowel("),
    "of_main": (OF + "main.rs", "fn main("),
    "of_lin_epoca": (OF + "experiments/linear.rs", "for epoch in 1..=max_epochs {"),
    "of_bool_muestras": (OF + "experiments/true_false.rs", "for &(input, target) in &samples {"),
    "of_voc_muestras": (OF + "experiments/vowels.rs", "for (sample_index, sample) in samples.iter().enumerate() {"),
    "of_voc_update": (OF + "experiments/vowels.rs", "for (output, neuron) in layer.neurons_mut().iter_mut().enumerate() {"),
})


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


def extraer_constante(ruta, firma):
    lineas = (RAIZ / ruta).read_text(encoding="utf-8").splitlines()
    ini = next(i for i, l in enumerate(lineas) if firma in l)
    while ini > 0 and lineas[ini - 1].strip().startswith("//"):
        ini -= 1
    fin = next(j for j in range(ini, len(lineas)) if lineas[j].rstrip().endswith("];"))
    return "\n".join(lineas[ini:fin + 1]) + "\n"


(SALIDA / "of_patrones.rs").write_text(extraer_constante(OF + "experiments/vowels.rs", "const PATTERNS"), encoding="utf-8")
for nombre, (ruta, firma) in EXTRACTOS.items():
    (SALIDA / f"{nombre}.rs").write_text(extraer(ruta, firma).replace("≫", ">>"), encoding="utf-8")
print("extractos:", ", ".join(EXTRACTOS))
