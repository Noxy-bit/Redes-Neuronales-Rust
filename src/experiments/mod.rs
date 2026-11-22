//! Fases 5, 7 y 8 — Experimentos progresivos reproducibles.
//!
//! Cada experimento entrena redes con semilla fija y exporta sus registros
//! numéricos reales a archivos CSV dentro del directorio de salida
//! (por defecto `resultados/`).

pub mod benchmarks;
pub mod csv;
pub mod exp1_y2x;
pub mod exp2_xor;
pub mod exp3_vocales;
pub mod prueba_escritorio;

use crate::math::{MathError, Vector};
use crate::nn::Network;
use std::fmt;

/// Semilla por defecto del PRNG para todos los experimentos.
pub const SEMILLA_POR_DEFECTO: u64 = 42;

/// Error de un experimento: fallo de E/S al exportar CSV o error matemático.
#[derive(Debug)]
pub enum ExperimentError {
    /// Error de entrada/salida al escribir resultados.
    Io(std::io::Error),
    /// Error de dimensiones o argumentos en la red.
    Math(MathError),
}

impl fmt::Display for ExperimentError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ExperimentError::Io(e) => write!(f, "error de E/S: {e}"),
            ExperimentError::Math(e) => write!(f, "error matemático: {e}"),
        }
    }
}

impl std::error::Error for ExperimentError {}

impl From<std::io::Error> for ExperimentError {
    fn from(e: std::io::Error) -> Self {
        ExperimentError::Io(e)
    }
}

impl From<MathError> for ExperimentError {
    fn from(e: MathError) -> Self {
        ExperimentError::Math(e)
    }
}

/// Resultado de un experimento.
pub type ExperimentResult<T> = Result<T, ExperimentError>;

/// Exactitud de clasificación binaria con umbral `0.5` sobre una salida
/// escalar: `aciertos / N`. `O(N·P)`.
pub fn exactitud_binaria(red: &Network, xs: &[Vector], ys: &[Vector]) -> Result<f64, MathError> {
    let mut aciertos = 0usize;
    for (x, y) in xs.iter().zip(ys) {
        let p = red.predict(x)?.get(0)?;
        if ((p >= 0.5) as u8 as f64 - y.get(0)?).abs() < f64::EPSILON {
            aciertos += 1;
        }
    }
    Ok(aciertos as f64 / xs.len().max(1) as f64)
}

/// Exactitud multiclase por `argmax` (salida *one-hot*): `aciertos / N`. `O(N·P)`.
pub fn exactitud_argmax(red: &Network, xs: &[Vector], ys: &[Vector]) -> Result<f64, MathError> {
    let mut aciertos = 0usize;
    for (x, y) in xs.iter().zip(ys) {
        if red.predict(x)?.argmax() == y.argmax() {
            aciertos += 1;
        }
    }
    Ok(aciertos as f64 / xs.len().max(1) as f64)
}

#[cfg(test)]
pub(crate) fn directorio_temporal(nombre: &str) -> std::path::PathBuf {
    let dir = std::env::temp_dir().join(format!("rn_rust_test_{}_{}", nombre, std::process::id()));
    std::fs::create_dir_all(&dir).unwrap();
    dir
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::nn::Activation;

    #[test]
    fn exactitudes_y_errores() {
        let red = Network::new(&[1, 1], &[Activation::Linear], 1).unwrap();
        let xs = vec![Vector::new(vec![0.0])];
        let ys = vec![Vector::new(vec![0.0])];
        // Salida lineal con sesgo 0: predice 0 → clase 0 → acierto.
        assert_eq!(exactitud_binaria(&red, &xs, &ys).unwrap(), 1.0);
        assert_eq!(exactitud_argmax(&red, &xs, &ys).unwrap(), 1.0);
        assert!(exactitud_binaria(&red, &[Vector::zeros(2)], &ys).is_err());
        let e: ExperimentError = MathError::InvalidArgument("x".into()).into();
        assert!(e.to_string().contains("matemático"));
        let e: ExperimentError = std::io::Error::other("y").into();
        assert!(e.to_string().contains("E/S"));
    }
}
