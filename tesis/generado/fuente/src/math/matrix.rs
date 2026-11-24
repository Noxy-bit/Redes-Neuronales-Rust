//! Matriz densa de números reales en orden por filas (*row-major*).

use super::error::{MathError, MathResult};
use super::rng::Rng;
use super::vector::Vector;

/// Matriz densa **A ∈ ℝ^{m×n}** (`m` filas, `n` columnas) almacenada en un único
/// `Vec<f64>` contiguo en orden por filas: el elemento `aᵢⱼ` vive en la
/// posición `i·n + j`.
///
/// En la red, la matriz de pesos de una capa con `n_in` entradas y `n_out`
/// neuronas tiene forma `n_out × n_in`, de modo que `z = W·x + b`.
/// Todas las operaciones validan dimensiones y devuelven [`MathError`].
#[derive(Debug, Clone, PartialEq)]
pub struct Matrix {
    rows: usize,
    cols: usize,
    data: Vec<f64>,
}

impl Matrix {
    /// Crea una matriz `rows × cols` desde datos en orden por filas.
    /// Error [`MathError::InvalidShape`] si `data.len() ≠ rows·cols`. `O(1)`.
    pub fn new(rows: usize, cols: usize, data: Vec<f64>) -> MathResult<Self> {
        if data.len() != rows * cols {
            return Err(MathError::InvalidShape {
                esperado: rows * cols,
                recibido: data.len(),
            });
        }
        Ok(Self { rows, cols, data })
    }

    /// Matriz nula `0 ∈ ℝ^{m×n}`. `O(m·n)`.
    pub fn zeros(rows: usize, cols: usize) -> Self {
        Self {
            rows,
            cols,
            data: vec![0.0; rows * cols],
        }
    }

    /// Matriz identidad `Iₙ` (`aᵢᵢ = 1`, resto `0`). `O(n²)`.
    pub fn identity(n: usize) -> Self {
        let mut m = Self::zeros(n, n);
        for i in 0..n {
            m.data[i * n + i] = 1.0;
        }
        m
    }

    /// Construye la matriz a partir de un slice de filas; todas deben tener la
    /// misma longitud. `O(m·n)`.
    pub fn from_rows(rows: &[Vec<f64>]) -> MathResult<Self> {
        let cols = rows.first().map_or(0, Vec::len);
        let mut data = Vec::with_capacity(rows.len() * cols);
        for row in rows {
            if row.len() != cols {
                return Err(MathError::DimensionMismatch {
                    operacion: "construcción desde filas",
                    izquierda: (1, cols),
                    derecha: (1, row.len()),
                });
            }
            data.extend_from_slice(row);
        }
        Ok(Self {
            rows: rows.len(),
            cols,
            data,
        })
    }

    /// Matriz con elementos `aᵢⱼ ~ U[low, high)` generados con un [`Rng`]
    /// determinista (reproducible con la misma semilla). `O(m·n)`.
    pub fn random_uniform(rows: usize, cols: usize, low: f64, high: f64, rng: &mut Rng) -> Self {
        let data = (0..rows * cols).map(|_| rng.uniform(low, high)).collect();
        Self { rows, cols, data }
    }

    /// Número de filas `m`. `O(1)`.
    pub fn rows(&self) -> usize {
        self.rows
    }

    /// Número de columnas `n`. `O(1)`.
    pub fn cols(&self) -> usize {
        self.cols
    }

    /// Forma `(m, n)`. `O(1)`.
    pub fn shape(&self) -> (usize, usize) {
        (self.rows, self.cols)
    }

    /// Datos en orden por filas (solo lectura). `O(1)`.
    pub fn as_slice(&self) -> &[f64] {
        &self.data
    }

    /// Datos en orden por filas (mutable). `O(1)`.
    pub fn as_mut_slice(&mut self) -> &mut [f64] {
        &mut self.data
    }

    fn index_of(&self, row: usize, col: usize) -> MathResult<usize> {
        if row < self.rows && col < self.cols {
            Ok(row * self.cols + col)
        } else {
            Err(MathError::IndexOutOfBounds {
                indice: (row, col),
                forma: self.shape(),
            })
        }
    }

    /// Acceso seguro a `aᵢⱼ`. Error si `i ≥ m` o `j ≥ n`. `O(1)`.
    pub fn get(&self, row: usize, col: usize) -> MathResult<f64> {
        Ok(self.data[self.index_of(row, col)?])
    }

    /// Asignación segura `aᵢⱼ ← value`. `O(1)`.
    pub fn set(&mut self, row: usize, col: usize, value: f64) -> MathResult<()> {
        let idx = self.index_of(row, col)?;
        self.data[idx] = value;
        Ok(())
    }

    /// Copia la fila `i` como [`Vector`] de longitud `n`. `O(n)`.
    pub fn row(&self, row: usize) -> MathResult<Vector> {
        if row >= self.rows {
            return Err(MathError::IndexOutOfBounds {
                indice: (row, 0),
                forma: self.shape(),
            });
        }
        let start = row * self.cols;
        Ok(Vector::new(self.data[start..start + self.cols].to_vec()))
    }

    fn zip_with(
        &self,
        other: &Matrix,
        operacion: &'static str,
        f: impl Fn(f64, f64) -> f64,
    ) -> MathResult<Matrix> {
        if self.shape() != other.shape() {
            return Err(MathError::DimensionMismatch {
                operacion,
                izquierda: self.shape(),
                derecha: other.shape(),
            });
        }
        Ok(Matrix {
            rows: self.rows,
            cols: self.cols,
            data: self
                .data
                .iter()
                .zip(&other.data)
                .map(|(&a, &b)| f(a, b))
                .collect(),
        })
    }

    /// Suma `(A + B)ᵢⱼ = aᵢⱼ + bᵢⱼ`. Requiere misma forma `m×n`. `O(m·n)`.
    pub fn add(&self, other: &Matrix) -> MathResult<Matrix> {
        self.zip_with(other, "suma de matrices", |a, b| a + b)
    }

    /// Resta `(A − B)ᵢⱼ = aᵢⱼ − bᵢⱼ`. Requiere misma forma `m×n`. `O(m·n)`.
    pub fn sub(&self, other: &Matrix) -> MathResult<Matrix> {
        self.zip_with(other, "resta de matrices", |a, b| a - b)
    }

    /// Producto de Hadamard `(A ⊙ B)ᵢⱼ = aᵢⱼ·bᵢⱼ`. Requiere misma forma. `O(m·n)`.
    pub fn hadamard(&self, other: &Matrix) -> MathResult<Matrix> {
        self.zip_with(other, "producto de Hadamard (matrices)", |a, b| a * b)
    }

    /// Multiplicación por escalar `(k·A)ᵢⱼ = k·aᵢⱼ`. `O(m·n)`.
    pub fn scale(&self, k: f64) -> Matrix {
        self.map(|x| k * x)
    }

    /// Aplica `f` elemento a elemento. `O(m·n)`.
    pub fn map(&self, f: impl Fn(f64) -> f64) -> Matrix {
        Matrix {
            rows: self.rows,
            cols: self.cols,
            data: self.data.iter().map(|&x| f(x)).collect(),
        }
    }

    /// Producto matricial `C = A·B`, con `A ∈ ℝ^{m×k}`, `B ∈ ℝ^{k×n}`,
    /// `cᵢⱼ = Σₗ aᵢₗ·bₗⱼ`. Error si `A.cols ≠ B.rows`.
    ///
    /// Bucle `i-l-j` (amigable con la caché en orden por filas). `O(m·k·n)`.
    pub fn matmul(&self, other: &Matrix) -> MathResult<Matrix> {
        if self.cols != other.rows {
            return Err(MathError::DimensionMismatch {
                operacion: "multiplicación matricial",
                izquierda: self.shape(),
                derecha: other.shape(),
            });
        }
        let (m, k, n) = (self.rows, self.cols, other.cols);
        let mut out = Matrix::zeros(m, n);
        for i in 0..m {
            for l in 0..k {
                let a = self.data[i * k + l];
                if a == 0.0 {
                    continue;
                }
                let b_row = &other.data[l * n..(l + 1) * n];
                let c_row = &mut out.data[i * n..(i + 1) * n];
                for (c, &b) in c_row.iter_mut().zip(b_row) {
                    *c += a * b;
                }
            }
        }
        Ok(out)
    }

    /// Producto matriz–vector `y = A·x`, `yᵢ = Σⱼ aᵢⱼ·xⱼ`, con `A ∈ ℝ^{m×n}` y
    /// `x ∈ ℝⁿ` → `y ∈ ℝᵐ`. Error si `n ≠ x.len()`. `O(m·n)`.
    pub fn mul_vector(&self, v: &Vector) -> MathResult<Vector> {
        if self.cols != v.len() {
            return Err(MathError::DimensionMismatch {
                operacion: "producto matriz-vector",
                izquierda: self.shape(),
                derecha: (v.len(), 1),
            });
        }
        let x = v.as_slice();
        Ok(Vector::new(
            (0..self.rows)
                .map(|i| {
                    let row = &self.data[i * self.cols..(i + 1) * self.cols];
                    row.iter().zip(x).map(|(a, b)| a * b).sum()
                })
                .collect(),
        ))
    }

    /// Producto `y = Aᵀ·v` sin materializar la transpuesta, con `A ∈ ℝ^{m×n}`,
    /// `v ∈ ℝᵐ` → `y ∈ ℝⁿ`, `yⱼ = Σᵢ aᵢⱼ·vᵢ`. Se usa para propagar el error
    /// hacia la capa anterior (`Wᵀ·δ`). `O(m·n)`.
    pub fn transpose_mul_vector(&self, v: &Vector) -> MathResult<Vector> {
        if self.rows != v.len() {
            return Err(MathError::DimensionMismatch {
                operacion: "producto transpuesta-vector",
                izquierda: (self.cols, self.rows),
                derecha: (v.len(), 1),
            });
        }
        let mut out = vec![0.0; self.cols];
        for (i, &vi) in v.as_slice().iter().enumerate() {
            let row = &self.data[i * self.cols..(i + 1) * self.cols];
            for (o, &a) in out.iter_mut().zip(row) {
                *o += a * vi;
            }
        }
        Ok(Vector::new(out))
    }

    /// Transpuesta `(Aᵀ)ⱼᵢ = aᵢⱼ`; de `m×n` a `n×m`. `O(m·n)`.
    pub fn transpose(&self) -> Matrix {
        let mut out = Matrix::zeros(self.cols, self.rows);
        for i in 0..self.rows {
            for j in 0..self.cols {
                out.data[j * self.rows + i] = self.data[i * self.cols + j];
            }
        }
        out
    }

    /// Producto exterior `u·vᵀ`, con `u ∈ ℝᵐ`, `v ∈ ℝⁿ` → matriz `m×n`
    /// (`cᵢⱼ = uᵢ·vⱼ`). Gradiente de pesos: `∂L/∂W = δ·xᵀ`. `O(m·n)`.
    pub fn outer(u: &Vector, v: &Vector) -> Matrix {
        let mut data = Vec::with_capacity(u.len() * v.len());
        for &a in u.as_slice() {
            data.extend(v.as_slice().iter().map(|&b| a * b));
        }
        Matrix {
            rows: u.len(),
            cols: v.len(),
            data,
        }
    }
}
