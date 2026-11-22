/// Una iteración completa de aprendizaje sobre una muestra `(x, y)`:
/// `forward → backward → update`. Devuelve la pérdida **antes** de la
/// actualización. `O(P)`.
pub fn train_step(
    &mut self,
    input: &Vector,
    target: &Vector,
    learning_rate: f64,
) -> MathResult<f64> {
    self.forward(input)?;
    let loss = self.backward(target)?;
    self.update(learning_rate)?;
    Ok(loss)
}
