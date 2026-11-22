/// Retropropagación: recibe `∂L/∂a` (longitud `n_out`), guarda
/// `δ = ∂L/∂a ⊙ f'(z)`, `∂L/∂W = δ·xᵀ`, `∂L/∂b = δ` y devuelve
/// `∂L/∂x = Wᵀ·δ` (longitud `n_in`). Requiere un `forward` previo.
/// `O(n_out·n_in)`.
pub fn backward(&mut self, grad_output: &Vector) -> MathResult<Vector> {
    let delta = grad_output.hadamard(&self.activation.derivative_vector(&self.z))?;
    self.grad_weights = Matrix::outer(&delta, &self.input);
    self.grad_biases = delta.clone();
    let grad_input = self.weights.transpose_mul_vector(&delta)?;
    self.delta = delta;
    Ok(grad_input)
}
