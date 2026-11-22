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

#[cfg(test)]
mod tests {
    use super::*;

    fn v(d: &[f64]) -> Vector {
        Vector::new(d.to_vec())
    }

    #[test]
    fn creacion_y_acceso() {
        let z = Vector::zeros(3);
        assert_eq!(z.as_slice(), &[0.0, 0.0, 0.0]);
        assert_eq!(Vector::filled(2, 1.5).as_slice(), &[1.5, 1.5]);
        assert!(Vector::default().is_empty());
        let mut a = v(&[1.0, 2.0, 3.0]);
        assert_eq!(a.len(), 3);
        assert_eq!(a.get(1), Ok(2.0));
        assert!(matches!(a.get(3), Err(MathError::IndexOutOfBounds { .. })));
        a.set(0, 9.0).unwrap();
        assert_eq!(a.get(0), Ok(9.0));
        assert!(a.set(10, 1.0).is_err());
        a.as_mut_slice()[2] = 4.0;
        assert_eq!(a.clone().into_vec(), vec![9.0, 2.0, 4.0]);
        assert_eq!(Vector::from(vec![1.0]), v(&[1.0]));
    }

    #[test]
    fn suma_resta_hadamard_punto() {
        let a = v(&[1.0, 2.0, 3.0]);
        let b = v(&[4.0, 5.0, 6.0]);
        assert_eq!(a.add(&b).unwrap(), v(&[5.0, 7.0, 9.0]));
        assert_eq!(b.sub(&a).unwrap(), v(&[3.0, 3.0, 3.0]));
        assert_eq!(a.hadamard(&b).unwrap(), v(&[4.0, 10.0, 18.0]));
        assert_eq!(a.dot(&b).unwrap(), 32.0);
        assert_eq!(a.scale(2.0), v(&[2.0, 4.0, 6.0]));
        assert_eq!(a.map(|x| x * x), v(&[1.0, 4.0, 9.0]));
        assert_eq!(a.sum(), 6.0);
        assert!((v(&[3.0, 4.0]).norm() - 5.0).abs() < 1e-12);
    }

    #[test]
    fn errores_de_dimension() {
        let a = v(&[1.0, 2.0]);
        let b = v(&[1.0, 2.0, 3.0]);
        for r in [a.add(&b), a.sub(&b), a.hadamard(&b)] {
            assert!(matches!(r, Err(MathError::DimensionMismatch { .. })));
        }
        assert_eq!(
            a.dot(&b),
            Err(MathError::DimensionMismatch {
                operacion: "producto punto",
                izquierda: (2, 1),
                derecha: (3, 1)
            })
        );
    }

    #[test]
    fn argmax_basico() {
        assert_eq!(v(&[0.1, 0.9, 0.3]).argmax(), Some(1));
        assert_eq!(v(&[0.5, 0.5]).argmax(), Some(0));
        assert_eq!(Vector::default().argmax(), None);
    }
}
