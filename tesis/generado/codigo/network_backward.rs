/// Backpropagation a partir de la última salida calculada por `forward`:
/// calcula y guarda `δ⁽ˡ⁾`, `∂L/∂W⁽ˡ⁾` y `∂L/∂b⁽ˡ⁾` en cada capa (de la
/// última a la primera) y devuelve la pérdida `MSE(ŷ, y)`. `O(P)`.
pub fn backward(&mut self, target: &Vector) -> MathResult<f64> {
    let output = self.layers[self.layers.len() - 1].output().clone();
    let loss = self.loss.loss(&output, target)?;
    let mut grad = self.loss.derivative(&output, target)?;
    for layer in self.layers.iter_mut().rev() {
        grad = layer.backward(&grad)?;
    }
    Ok(loss)
}
