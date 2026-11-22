//! Fase 1 — Fundamentos matemáticos.
//!
//! Contiene las estructuras algebraicas sobre las que se construye la red:
//! vectores y matrices densas de `f64`, el tipo de error de dimensiones y un
//! generador pseudoaleatorio determinista para inicializar pesos.

pub mod error;
pub mod matrix;
pub mod rng;
pub mod vector;

pub use error::{MathError, MathResult};
pub use matrix::Matrix;
pub use rng::Rng;
pub use vector::Vector;
