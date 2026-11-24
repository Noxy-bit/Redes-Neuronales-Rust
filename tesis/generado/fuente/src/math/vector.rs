//! Vector denso de números reales.

use super::error::{MathError, MathResult};

/// Vector columna denso **v ∈ ℝⁿ** almacenado de forma contigua en memoria.
///
/// Representa entradas `x`, sesgos `b`, sumas ponderadas `z`, activaciones `a`
/// y gradientes `δ` de la red. Todas las operaciones binarias validan que ambos
/// operandos tengan la misma longitud `n` y devuelven [`MathError`] en caso
/// contrario (nunca entran en pánico por dimensiones).
#[derive(Debug, Clone, PartialEq, Default)]
pub struct Vector {
    data: Vec<f64>,
}

impl Vector {
    /// Crea un vector a partir de sus componentes. `O(1)` (toma el `Vec`).
    pub fn new(data: Vec<f64>) -> Self {
        Self { data }
    }

    /// Vector nulo **0 ∈ ℝⁿ**. `O(n)`.
    pub fn zeros(len: usize) -> Self {
        Self {
            data: vec![0.0; len],
        }
    }

    /// Vector con todas sus componentes iguales a `value`. `O(n)`.
    pub fn filled(len: usize, value: f64) -> Self {
        Self {
            data: vec![value; len],
        }
    }

    /// Longitud `n` del vector. `O(1)`.
    pub fn len(&self) -> usize {
        self.data.len()
    }

    /// Indica si el vector no tiene componentes (`n = 0`). `O(1)`.
    pub fn is_empty(&self) -> bool {
        self.data.is_empty()
    }

    /// Vista de solo lectura de las componentes. `O(1)`.
    pub fn as_slice(&self) -> &[f64] {
        &self.data
    }

    /// Vista mutable de las componentes. `O(1)`.
    pub fn as_mut_slice(&mut self) -> &mut [f64] {
        &mut self.data
    }

    /// Consume el vector y devuelve el `Vec<f64>` interno. `O(1)`.
    pub fn into_vec(self) -> Vec<f64> {
        self.data
    }

    /// Acceso seguro a `vᵢ`. Error si `i ≥ n`. `O(1)`.
    pub fn get(&self, index: usize) -> MathResult<f64> {
        self.data
            .get(index)
            .copied()
            .ok_or(MathError::IndexOutOfBounds {
                indice: (index, 0),
                forma: (self.len(), 1),
            })
    }

    /// Asignación segura `vᵢ ← value`. Error si `i ≥ n`. `O(1)`.
    pub fn set(&mut self, index: usize, value: f64) -> MathResult<()> {
        let forma = (self.len(), 1);
        match self.data.get_mut(index) {
            Some(x) => {
                *x = value;
                Ok(())
            }
            None => Err(MathError::IndexOutOfBounds {
                indice: (index, 0),
                forma,
            }),
        }
    }

    fn check_same_len(&self, other: &Vector, operacion: &'static str) -> MathResult<()> {
        if self.len() == other.len() {
            Ok(())
        } else {
            Err(MathError::DimensionMismatch {
                operacion,
                izquierda: (self.len(), 1),
                derecha: (other.len(), 1),
            })
        }
    }

    fn zip_with(
        &self,
        other: &Vector,
        operacion: &'static str,
        f: impl Fn(f64, f64) -> f64,
    ) -> MathResult<Vector> {
        self.check_same_len(other, operacion)?;
        Ok(Vector::new(
            self.data
                .iter()
                .zip(&other.data)
                .map(|(&a, &b)| f(a, b))
                .collect(),
        ))
    }

    /// Suma componente a componente: `(u + v)ᵢ = uᵢ + vᵢ`. Requiere `n` igual. `O(n)`.
    pub fn add(&self, other: &Vector) -> MathResult<Vector> {
        self.zip_with(other, "suma de vectores", |a, b| a + b)
    }

    /// Resta componente a componente: `(u − v)ᵢ = uᵢ − vᵢ`. Requiere `n` igual. `O(n)`.
    pub fn sub(&self, other: &Vector) -> MathResult<Vector> {
        self.zip_with(other, "resta de vectores", |a, b| a - b)
    }

    /// Producto de Hadamard: `(u ⊙ v)ᵢ = uᵢ·vᵢ`. Requiere `n` igual. `O(n)`.
    ///
    /// Se usa en backpropagation: `δ = ∂L/∂a ⊙ f'(z)`.
    pub fn hadamard(&self, other: &Vector) -> MathResult<Vector> {
        self.zip_with(other, "producto de Hadamard (vectores)", |a, b| a * b)
    }

    /// Producto punto: `u · v = Σᵢ uᵢ·vᵢ`. Requiere `n` igual. `O(n)`.
    pub fn dot(&self, other: &Vector) -> MathResult<f64> {
        self.check_same_len(other, "producto punto")?;
        Ok(self.data.iter().zip(&other.data).map(|(a, b)| a * b).sum())
    }

    /// Multiplicación por escalar: `(k·v)ᵢ = k·vᵢ`. `O(n)`.
    pub fn scale(&self, k: f64) -> Vector {
        self.map(|x| k * x)
    }

    /// Aplica `f` a cada componente: `(f(v))ᵢ = f(vᵢ)`. `O(n)`.
    pub fn map(&self, f: impl Fn(f64) -> f64) -> Vector {
        Vector::new(self.data.iter().map(|&x| f(x)).collect())
    }

    /// Suma de componentes `Σᵢ vᵢ`. `O(n)`.
    pub fn sum(&self) -> f64 {
        self.data.iter().sum()
    }

    /// Norma euclidiana `‖v‖₂ = √(Σᵢ vᵢ²)`. `O(n)`.
    pub fn norm(&self) -> f64 {
        self.data.iter().map(|x| x * x).sum::<f64>().sqrt()
    }

    /// Índice de la componente máxima (`argmaxᵢ vᵢ`); `None` si está vacío.
    /// En caso de empate devuelve el primer índice. `O(n)`.
    pub fn argmax(&self) -> Option<usize> {
        let mut best: Option<(usize, f64)> = None;
        for (i, &x) in self.data.iter().enumerate() {
            match best {
                Some((_, b)) if x <= b => {}
                _ => best = Some((i, x)),
            }
        }
        best.map(|(i, _)| i)
    }
}

impl From<Vec<f64>> for Vector {
    fn from(data: Vec<f64>) -> Self {
        Vector::new(data)
    }
}
