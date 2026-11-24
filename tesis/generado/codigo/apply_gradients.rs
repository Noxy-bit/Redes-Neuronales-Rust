/// Paso de descenso de gradiente: `W ← W − α·∂L/∂W`, `b ← b − α·∂L/∂b`.
/// `O(n_out·n_in)`.
pub fn apply_gradients(&mut self, learning_rate: f64) -> MathResult<()> {
    self.weights = self.weights.sub(&self.grad_weights.scale(learning_rate))?;
    self.biases = self.biases.sub(&self.grad_biases.scale(learning_rate))?;
    Ok(())
}
