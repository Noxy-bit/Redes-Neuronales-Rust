//! Neurona artificial individual.

use super::activation::{Activation, ActivationFn};
use crate::math::{MathResult, Rng, Vector};

/// Neurona artificial con `n` entradas:
///
/// `z = w · x + b = Σⱼ wⱼ·xⱼ + b`  y  `a = f(z)`
///
/// donde `w ∈ ℝⁿ` son los pesos, `b ∈ ℝ` el sesgo (*bias*) y `f` la función
/// de activación. Cada fila de la matriz de pesos de una [`super::Layer`]
/// corresponde exactamente a una neurona de este tipo.
#[derive(Debug, Clone, PartialEq)]
pub struct Neuron {
    /// Pesos sinápticos `w ∈ ℝⁿ`.
    pub weights: Vector,
    /// Sesgo `b ∈ ℝ`.
    pub bias: f64,
    /// Función de activación `f`.
    pub activation: Activation,
}

impl Neuron {
    /// Crea una neurona con pesos, sesgo y activación explícitos. `O(1)`.
    pub fn new(weights: Vector, bias: f64, activation: Activation) -> Self {
        Self {
            weights,
            bias,
            activation,
        }
    }

    /// Crea una neurona con pesos `wⱼ ~ U[−l, l)` (`l = √(6/(n+1))`, Xavier)
    /// y sesgo `0`, usando un [`Rng`] determinista. `O(n)`.
    pub fn random(n_inputs: usize, activation: Activation, rng: &mut Rng) -> Self {
        let limit = (6.0 / (n_inputs as f64 + 1.0)).sqrt();
        let weights = Vector::new((0..n_inputs).map(|_| rng.uniform(-limit, limit)).collect());
        Self::new(weights, 0.0, activation)
    }

    /// Número de entradas `n`. `O(1)`.
    pub fn n_inputs(&self) -> usize {
        self.weights.len()
    }

    /// Suma ponderada `z = w·x + b`. Error si `x.len() ≠ n`. `O(n)`.
    pub fn weighted_sum(&self, inputs: &Vector) -> MathResult<f64> {
        Ok(self.weights.dot(inputs)? + self.bias)
    }

    /// Propagación hacia adelante `a = f(w·x + b)`. Error si `x.len() ≠ n`. `O(n)`.
    pub fn forward(&self, inputs: &Vector) -> MathResult<f64> {
        Ok(self.activation.activate(self.weighted_sum(inputs)?))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn forward_calculo_manual() {
        let n = Neuron::new(Vector::new(vec![0.5, -1.0]), 0.25, Activation::Linear);
        let x = Vector::new(vec![2.0, 3.0]);
        // z = 0.5·2 − 1·3 + 0.25 = −1.75
        assert_eq!(n.weighted_sum(&x).unwrap(), -1.75);
        assert_eq!(n.forward(&x).unwrap(), -1.75);
        let r = Neuron {
            activation: Activation::ReLU,
            ..n.clone()
        };
        assert_eq!(r.forward(&x).unwrap(), 0.0);
        let s = Neuron {
            activation: Activation::Sigmoid,
            bias: 2.0,
            ..n
        };
        assert_eq!(s.forward(&x).unwrap(), 0.5);
    }

    #[test]
    fn forward_error_de_dimension() {
        let n = Neuron::new(Vector::new(vec![1.0, 1.0]), 0.0, Activation::Linear);
        assert!(n.forward(&Vector::new(vec![1.0])).is_err());
    }

    #[test]
    fn inicializacion_reproducible() {
        let a = Neuron::random(3, Activation::Sigmoid, &mut Rng::new(5));
        let b = Neuron::random(3, Activation::Sigmoid, &mut Rng::new(5));
        assert_eq!(a, b);
        assert_eq!(a.n_inputs(), 3);
        assert_eq!(a.bias, 0.0);
        let limit = (6.0f64 / 4.0).sqrt();
        assert!(a.weights.as_slice().iter().all(|w| w.abs() <= limit));
    }
}
