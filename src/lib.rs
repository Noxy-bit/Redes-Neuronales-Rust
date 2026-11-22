//! # Redes Neuronales desde Cero en Rust
//!
//! Biblioteca educativa que implementa una red neuronal artificial multicapa
//! utilizando exclusivamente la biblioteca estándar de Rust (`std`), sin crates
//! externos de aprendizaje automático ni de álgebra lineal.
//!
//! Organización por fases (documento base del proyecto):
//!
//! 1. [`math`]: álgebra lineal elemental (`Vector`, `Matrix`) y generador
//!    pseudoaleatorio reproducible (`Rng`).
//! 2. [`nn`]: neurona, funciones de activación, función de pérdida, capas y red
//!    con *forward*, *backward* (backpropagation), `predict` y `train`
//!    (descenso de gradiente).
//! 3. [`experiments`]: experimentos progresivos (`y = 2x`, `XOR`, vocales),
//!    prueba de escritorio y benchmarks con exportación a CSV.

pub mod experiments;
pub mod math;
pub mod nn;
