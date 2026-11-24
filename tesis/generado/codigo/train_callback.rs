/// Igual que [`Network::train`], pero invoca `callback(época, &red, mse)`
/// al final de cada época (épocas numeradas desde `1`) para registrar la
/// evolución del entrenamiento. `O(E·N·P)` más el costo del callback.
pub fn train_with_callback<F>(
    &mut self,
    inputs: &[Vector],
    targets: &[Vector],
    epochs: usize,
    learning_rate: f64,
    mut callback: F,
) -> MathResult<Vec<f64>>
where
    F: FnMut(usize, &Network, f64) -> MathResult<()>,
{
    validar_dataset(inputs, targets)?;
    let mut history = Vec::with_capacity(epochs);
    for epoch in 1..=epochs {
        for (x, y) in inputs.iter().zip(targets) {
            self.train_step(x, y, learning_rate)?;
        }
        let mse = self.evaluate_mse(inputs, targets)?;
        history.push(mse);
        callback(epoch, self, mse)?;
    }
    Ok(history)
}
