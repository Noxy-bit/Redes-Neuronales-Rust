//! Función de pérdida: error cuadrático medio (MSE).

use crate::math::{MathError, MathResult, Vector};

/// Contrato de una función de pérdida `L(ŷ, y)` y su gradiente `∂L/∂ŷ`.
pub trait LossFn {
    /// Valor escalar de la pérdida para una predicción `ŷ ∈ ℝⁿ` y objetivo `y ∈ ℝⁿ`.
    fn loss(&self, prediction: &Vector, target: &Vector) -> MathResult<f64>;
    /// Gradiente `∂L/∂ŷ ∈ ℝⁿ` respecto a la predicción.
    fn derivative(&self, prediction: &Vector, target: &Vector) -> MathResult<Vector>;
}

/// **Error cuadrático medio** (*Mean Squared Error*):
///
/// `MSE(ŷ, y) = (1/n)·Σᵢ (ŷᵢ − yᵢ)²`
///
/// Gradiente: `∂MSE/∂ŷᵢ = (2/n)·(ŷᵢ − yᵢ)`.
///
/// Ambas operaciones cuestan `O(n)` y exigen `ŷ` e `y` de igual longitud `n ≥ 1`.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub struct Mse;

fn validar(prediction: &Vector, target: &Vector, operacion: &'static str) -> MathResult<()> {
    if prediction.len() != target.len() || prediction.is_empty() {
        return Err(MathError::DimensionMismatch {
            operacion,
            izquierda: (prediction.len(), 1),
            derecha: (target.len(), 1),
        });
    }
    Ok(())
}

impl LossFn for Mse {
    fn loss(&self, prediction: &Vector, target: &Vector) -> MathResult<f64> {
        validar(prediction, target, "MSE")?;
        let diff = prediction.sub(target)?;
        Ok(diff.dot(&diff)? / prediction.len() as f64)
    }

    fn derivative(&self, prediction: &Vector, target: &Vector) -> MathResult<Vector> {
        validar(prediction, target, "derivada de MSE")?;
        Ok(prediction.sub(target)?.scale(2.0 / prediction.len() as f64))
    }
}
