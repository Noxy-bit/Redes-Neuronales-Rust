# Auditoría del repositorio oficial `lanorrron/neural-network`

- **Repositorio:** https://github.com/lanorrron/neural-network
- **Commit auditado:** `8667b4c` ("first commit", 24-11-2026, autor Roni). Instantánea en `repo_oficial/neural-network/`.
- **Reproducción:** `python3 scripts/auditar_repo_oficial.py` (compila, ejecuta, mide y regenera `resultados/oficial/*`).
- **Entorno de esta auditoría:** Linux x86_64, rustc 1.99.1, perfil `--release`.

Todas las cifras de este documento salen de `resultados/oficial/resumen.csv` y de las salidas completas
`resultados/oficial/{lineal,booleano,vocales,vocal_a}.txt`.

## 1. Lenguaje, configuración y dependencias

| Aspecto | Hallazgo |
|---|---|
| Lenguaje | Rust, edición 2024 (`Cargo.toml`, paquete `neural-network` 0.1.0) |
| Tipo de crate | Solo binario (`src/main.rs`), sin `lib.rs` |
| Dependencias | `rand = "0.9"` (única). Solo la usan `Vector::random` y `Matrix::random`, que ningún experimento invoca |
| Precisión numérica | `f32` en toda la red |
| Tamaño | 1 044 líneas en 20 archivos (`src/` + `Cargo.toml` + `README.md`) |
| Binario `--release` | 511 672 bytes (499.7 KiB) |
| Datos externos | Ninguno: los conjuntos están escritos en el código |

## 2. Arquitectura (`src/`)

| Módulo | Contenido |
|---|---|
| `math/vector.rs` | `Vector<T>` genérico: `new`, `zeros`, `len`, `get`, `set`, `as_slice(_mut)`, `add`, `sub`, `multiply_scalar`, `dot`, `map`, `random` |
| `math/matrix.rs` | `Matrix<T>` genérico (orden por filas): `new`, `get`, `set`, `transpose`, `print`, `add`, `sub`, `multiply_scalar`, `multiply`, `add_bias`, `map`, `zeros`, `multiply_elementwise`, `random`. **No se usa en ningún experimento** |
| `neural/neuron.rs` | `Neuron { weights: Vector<f32>, bias: f32 }`, `forward(x) = x·w + b` |
| `neural/layer.rs` | `Layer { neurons: Vec<Neuron> }`, `forward` y `neurons_mut` |
| `neural/network.rs` | `Network { layers }` con `forward` encadenado. **No se instancia en ningún experimento** |
| `neural/activation.rs` | `Activacion::relu` y `Activacion::sigmoid` (ReLU no se usa) |
| `learning/loss.rs` | `MSE::calculate` y `MSE::derivate` = 2(ŷ − y)/n |
| `learning/gradient.rs` | `Gradient::weights(δ, x) = δ·xᵢ` y `Gradient::bias(δ) = δ` |
| `learning/optimizer.rs` | `GradientDescent { learning_rate }`: `update_weights`, `update_bias` (θ ← θ − α∇) |
| `experiments/` | `linear.rs`, `true_false.rs`, `vowels.rs` (con `encode`, `softmax`, `argmax`, `parse_vowel`) |
| `main.rs` | CLI: `lineal`, `booleano`, `vocal <letra>`; sin argumento ejecuta vocales |

El entrenamiento no está dentro de `Network`: cada experimento escribe su ciclo de épocas, acumula los
gradientes de todo el conjunto (descenso de gradiente por lote completo) y actualiza una vez por época.
No hay retropropagación multicapa: los tres modelos tienen una sola capa entrenable.

## 3. Experimentos y resultados reales

| Experimento | Configuración | Resultado |
|---|---|---|
| `lineal` (y = 2x) | 1 neurona lineal, x ∈ {1, 2, 3, 4, 7, 8}, α = 0.02, MSE, meta MSE ≤ 10⁻¹², máx. 10 000 épocas | Meta alcanzada en **1 151 épocas**; MSE 95.33 → **9.47×10⁻¹³**; w = 1.9999996, b = 1.9×10⁻⁶ |
| `booleano` | 1 neurona Sigmoid, 0 → falso y 1 → verdadero, α = 0.5, 250 épocas, gradiente (p − y)/N | w = 6.3077, b = −2.9406; P(verdadero│0) = **0.0502**, P(verdadero│1) = **0.9667**; 2/2 correctas |
| `vocal` | Capa 25 → 5, softmax, 5 patrones 5×5 (uno por vocal), α = 0.3, 500 épocas | **5/5** vocales reconocidas, confianza 98.99 %–99.38 %; argmax correcto desde la época 1 |
| `vocal a` | Mismo entrenamiento y evaluación del patrón A | Reconoce **A** con 99.32 % |

Tiempos (`resultados/oficial/resumen.csv`):

| Experimento | Tiempo de pared del binario oficial | Tiempo de cómputo sin pausas (mediana de 5) |
|---|---|---|
| lineal | 8.71 s | 1.67 ms |
| booleano | 10.03 s | 1.18 ms |
| vocales | 40.10 s | 7.34 ms |

El tiempo de pared incluye las pausas `thread::sleep` (150 ms, 40 ms y 80 ms por informe) que el programa usa
para que la demostración se pueda seguir en pantalla. El tiempo de cómputo se midió con una copia idéntica a la
que solo se le quitaron esas pausas; incluye el arranque del proceso y la impresión en terminal.

## 4. Calidad y verificación

| Herramienta | Resultado |
|---|---|
| `cargo build --release` | Compila; 24 advertencias (código sin usar y funciones obsoletas de `rand`) |
| `cargo test` | **0 pruebas** definidas |
| `cargo clippy --release` | **1 error** (`clippy::modulo_one` en `vowels.rs:76`, `REPORT_EVERY = 1`) y 27 advertencias |

## 5. Diferencias clave con el motor previo (`Noxy-bit/Redes-Neuronales-Rust`)

| Aspecto | Repositorio oficial | Motor previo (ahora complementario) |
|---|---|---|
| Rol en la feria | **Implementación principal** que se presenta y demuestra | Validación extendida |
| Precisión | `f32` | `f64` |
| Dependencias | `rand 0.9` (no usada en los experimentos) | Ninguna |
| Errores | `assert!` (pánico) | `Result<T, MathError>` |
| Entrenamiento | Ciclo escrito en cada experimento, lote completo | `Network::train` genérico, por muestra |
| Capas entrenables | 1 (sin retropropagación multicapa) | Varias (2-4-1, 25-10-5) con retropropagación |
| Salida multiclase | Softmax + gradiente (p − y) | Sigmoid + MSE |
| y = 2x | 6 muestras, α = 0.02, 1 151 épocas, MSE 9.47×10⁻¹³ | 5 muestras, α = 0.01, 1 000 épocas, MSE 4.6×10⁻¹⁸ |
| Segundo experimento | Booleano 0/1 (linealmente separable) | XOR (no lineal): perceptrón 25 % vs. 2-4-1 100 % |
| Vocales | 5 patrones sin ruido, 5/5 | 25 de entrenamiento + 250 de prueba con ruido, 97.6 % |
| Pruebas | 0 | 52 (incluye *gradient checking*) |
| Binario | 499.7 KiB | 682.6 KiB |

## 6. Observaciones para el equipo

1. El README afirma que el experimento de vocales usa `Matrix::multiply`; el código usa `Layer::forward` (un
   producto punto por neurona) y `Matrix` no se construye en ningún punto.
2. `cargo clippy` falla por `REPORT_EVERY = 1`; basta con quitar la condición `epoch % REPORT_EVERY == 0` o
   cambiar la constante.
3. No hay pruebas automatizadas; el motor complementario aporta 52 pruebas sobre las mismas ecuaciones.
4. `rand` puede eliminarse si `random` no se va a usar, o actualizarse a `rand::rng()` / `random_range`.
