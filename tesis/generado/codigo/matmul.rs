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
