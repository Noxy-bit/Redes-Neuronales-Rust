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
