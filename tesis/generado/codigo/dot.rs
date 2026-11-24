/// Producto punto: `u · v = Σᵢ uᵢ·vᵢ`. Requiere `n` igual. `O(n)`.
pub fn dot(&self, other: &Vector) -> MathResult<f64> {
    self.check_same_len(other, "producto punto")?;
    Ok(self.data.iter().zip(&other.data).map(|(a, b)| a * b).sum())
}
