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

#[cfg(test)]
mod tests {
    use super::*;

    fn derivada_numerica(f: &dyn ActivationFn, z: f64) -> f64 {
        let h = 1e-6;
        (f.activate(z + h) - f.activate(z - h)) / (2.0 * h)
    }

    #[test]
    fn sigmoid_valores_conocidos() {
        assert_eq!(Sigmoid.activate(0.0), 0.5);
        assert_eq!(Sigmoid.derivative(0.0), 0.25);
        assert!((Sigmoid.activate(2.0) - 0.880_797_077_977_882_3).abs() < 1e-15);
        assert!((Sigmoid.activate(-2.0) - 0.119_202_922_022_117_6).abs() < 1e-15);
        assert!(Sigmoid.activate(-1000.0) >= 0.0 && Sigmoid.activate(-1000.0).is_finite());
        assert!((Sigmoid.activate(1000.0) - 1.0).abs() < 1e-15);
        for z in [-3.0, -0.5, 0.7, 4.0] {
            assert!((Sigmoid.activate(z) + Sigmoid.activate(-z) - 1.0).abs() < 1e-15);
        }
    }

    #[test]
    fn relu_y_lineal_valores_conocidos() {
        assert_eq!(ReLU.activate(-3.0), 0.0);
        assert_eq!(ReLU.activate(2.5), 2.5);
        assert_eq!(ReLU.derivative(-1.0), 0.0);
        assert_eq!(ReLU.derivative(0.0), 0.0);
        assert_eq!(ReLU.derivative(3.0), 1.0);
        assert_eq!(Linear.activate(-7.0), -7.0);
        assert_eq!(Linear.derivative(123.0), 1.0);
    }

    #[test]
    fn gradient_checking_derivadas_analiticas() {
        let funcs: [&dyn ActivationFn; 6] = [
            &Sigmoid,
            &ReLU,
            &Linear,
            &Activation::Sigmoid,
            &Activation::ReLU,
            &Activation::Linear,
        ];
        // Se evitan puntos a menos de 1e-3 del pliegue de ReLU en z = 0.
        let puntos = [-4.0, -1.3, -0.2, 0.15, 0.9, 2.2, 5.0];
        for f in funcs {
            for &z in &puntos {
                let num = derivada_numerica(f, z);
                let ana = f.derivative(z);
                assert!(
                    (num - ana).abs() < 1e-8,
                    "{}: z={z} numérica={num} analítica={ana}",
                    f.name()
                );
            }
        }
    }

    #[test]
    fn enum_despacha_y_vectoriza() {
        let z = Vector::new(vec![-1.0, 0.0, 2.0]);
        assert_eq!(
            Activation::ReLU.activate_vector(&z).as_slice(),
            &[0.0, 0.0, 2.0]
        );
        assert_eq!(
            Activation::ReLU.derivative_vector(&z).as_slice(),
            &[0.0, 0.0, 1.0]
        );
        assert_eq!(Activation::Linear.activate_vector(&z), z);
        assert_eq!(
            Activation::Sigmoid.derivative_vector(&z).as_slice()[1],
            0.25
        );
        assert_eq!(Activation::Sigmoid.name(), "Sigmoid");
        assert_eq!(Activation::ReLU.name(), "ReLU");
        assert_eq!(Activation::Linear.name(), "Lineal");
    }
}
