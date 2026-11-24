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
