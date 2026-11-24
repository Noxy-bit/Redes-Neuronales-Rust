//! Funciones de activación y sus derivadas analíticas.

use crate::math::Vector;

/// Contrato de una función de activación escalar `f: ℝ → ℝ` y su derivada `f'`.
///
/// Ambas operaciones se evalúan sobre la suma ponderada `z` de una neurona y
/// tienen costo `O(1)`; sobre un vector de `n` componentes cuestan `O(n)`.
pub trait ActivationFn {
    /// Evalúa `a = f(z)`.
    fn activate(&self, z: f64) -> f64;
    /// Evalúa la derivada analítica `f'(z) = df/dz`.
    fn derivative(&self, z: f64) -> f64;
    /// Nombre legible de la función.
    fn name(&self) -> &'static str;
}

/// Función logística **Sigmoid**: `σ(z) = 1 / (1 + e^{−z})`, rango `(0, 1)`.
///
/// Derivada: `σ'(z) = σ(z)·(1 − σ(z))`, con máximo `0.25` en `z = 0`.
/// Se implementa de forma numéricamente estable para `z` muy negativos
/// (`σ(z) = e^{z} / (1 + e^{z})` cuando `z < 0`).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub struct Sigmoid;

/// Unidad lineal rectificada **ReLU**: `ReLU(z) = max(0, z)`, rango `[0, ∞)`.
///
/// Derivada: `ReLU'(z) = 1` si `z > 0`, `0` si `z ≤ 0` (por convención se toma
/// `0` en el punto no diferenciable `z = 0`).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub struct ReLU;

/// Activación **identidad (lineal)**: `f(z) = z`, `f'(z) = 1`.
///
/// Se usa en la salida de problemas de regresión (experimento `y = 2x`), donde
/// la salida no debe estar acotada.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub struct Linear;

impl ActivationFn for Sigmoid {
    fn activate(&self, z: f64) -> f64 {
        if z >= 0.0 {
            1.0 / (1.0 + (-z).exp())
        } else {
            let e = z.exp();
            e / (1.0 + e)
        }
    }

    fn derivative(&self, z: f64) -> f64 {
        let s = self.activate(z);
        s * (1.0 - s)
    }

    fn name(&self) -> &'static str {
        "Sigmoid"
    }
}

impl ActivationFn for ReLU {
    fn activate(&self, z: f64) -> f64 {
        z.max(0.0)
    }

    fn derivative(&self, z: f64) -> f64 {
        if z > 0.0 { 1.0 } else { 0.0 }
    }

    fn name(&self) -> &'static str {
        "ReLU"
    }
}

impl ActivationFn for Linear {
    fn activate(&self, z: f64) -> f64 {
        z
    }

    fn derivative(&self, _z: f64) -> f64 {
        1.0
    }

    fn name(&self) -> &'static str {
        "Lineal"
    }
}

/// Selector de activación almacenable en cada capa (`Copy`, sin asignación
/// dinámica). Despacha a [`Sigmoid`], [`ReLU`] o [`Linear`].
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Activation {
    /// `σ(z) = 1 / (1 + e^{−z})`.
    Sigmoid,
    /// `max(0, z)`.
    ReLU,
    /// `f(z) = z`.
    Linear,
}

impl ActivationFn for Activation {
    fn activate(&self, z: f64) -> f64 {
        match self {
            Activation::Sigmoid => Sigmoid.activate(z),
            Activation::ReLU => ReLU.activate(z),
            Activation::Linear => Linear.activate(z),
        }
    }

    fn derivative(&self, z: f64) -> f64 {
        match self {
            Activation::Sigmoid => Sigmoid.derivative(z),
            Activation::ReLU => ReLU.derivative(z),
            Activation::Linear => Linear.derivative(z),
        }
    }

    fn name(&self) -> &'static str {
        match self {
            Activation::Sigmoid => Sigmoid.name(),
            Activation::ReLU => ReLU.name(),
            Activation::Linear => Linear.name(),
        }
    }
}

impl Activation {
    /// Aplica la activación componente a componente: `a = f(z)`, `z ∈ ℝⁿ`. `O(n)`.
    pub fn activate_vector(&self, z: &Vector) -> Vector {
        z.map(|x| self.activate(x))
    }

    /// Derivada componente a componente: `f'(z)`, `z ∈ ℝⁿ`. `O(n)`.
    pub fn derivative_vector(&self, z: &Vector) -> Vector {
        z.map(|x| self.derivative(x))
    }
}
