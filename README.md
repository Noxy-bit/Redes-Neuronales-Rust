# Redes Neuronales desde Cero en Rust

Implementación educativa y modular de una red neuronal artificial desde cero en Rust (sin frameworks externos de ML), desarrollada para la Feria Facultativa FICCT - UAGRM (Gestión 2-2026).

## Estructura

| Módulo | Contenido |
|---|---|
| `src/math/` | `Vector`, `Matrix` (operaciones con `Result`), errores y PRNG SplitMix64 reproducible |
| `src/nn/` | Activaciones (Sigmoid, ReLU, Lineal), pérdida MSE, `Neuron`, `Layer`, `Network` (forward, backpropagation, Gradient Descent) |
| `src/experiments/` | `y = 2x`, XOR, vocales A-E-I-O-U, prueba de escritorio, benchmarks y exportación CSV |
| `resultados/` | CSV generados por ejecuciones reales del binario |

Sin dependencias externas: solo la biblioteca estándar de Rust.

## Uso

```bash
cargo test                          # pruebas unitarias (incluye gradient checking)
cargo run --release -- --all        # ejecuta todo y escribe resultados/*.csv
cargo run --release -- --exp2       # un experimento concreto (--exp1, --exp3, --escritorio, --bench)
cargo run --release -- --all --export otra_carpeta --seed 7
```
