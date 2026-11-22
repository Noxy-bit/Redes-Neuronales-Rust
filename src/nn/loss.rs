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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn mse_valores_conocidos() {
        let y = Vector::new(vec![1.0, 2.0, 3.0]);
        assert_eq!(Mse.loss(&y, &y).unwrap(), 0.0);
        let p = Vector::new(vec![2.0, 2.0, 5.0]);
        assert!((Mse.loss(&p, &y).unwrap() - 5.0 / 3.0).abs() < 1e-15);
        let g = Mse.derivative(&p, &y).unwrap();
        let esperado = [2.0 / 3.0, 0.0, 4.0 / 3.0];
        for (a, b) in g.as_slice().iter().zip(esperado) {
            assert!((a - b).abs() < 1e-15);
        }
    }

    #[test]
    fn mse_errores_de_dimension() {
        let a = Vector::new(vec![1.0]);
        let b = Vector::new(vec![1.0, 2.0]);
        assert!(Mse.loss(&a, &b).is_err());
        assert!(Mse.derivative(&a, &b).is_err());
        assert!(Mse.loss(&Vector::default(), &Vector::default()).is_err());
    }

    #[test]
    fn gradient_checking_mse() {
        let y = Vector::new(vec![0.3, -1.2, 2.0, 0.0]);
        let p = Vector::new(vec![0.5, 0.1, 1.4, -0.7]);
        let g = Mse.derivative(&p, &y).unwrap();
        let h = 1e-6;
        for i in 0..p.len() {
            let mut mas = p.clone();
            let mut menos = p.clone();
            mas.as_mut_slice()[i] += h;
            menos.as_mut_slice()[i] -= h;
            let num = (Mse.loss(&mas, &y).unwrap() - Mse.loss(&menos, &y).unwrap()) / (2.0 * h);
            assert!((num - g.as_slice()[i]).abs() < 1e-8);
        }
    }
}
