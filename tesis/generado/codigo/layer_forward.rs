/// Propagación hacia adelante con caché de `x`, `z` y `a` para el
/// posterior `backward`. Error si `x.len() ≠ n_in`. `O(n_out·n_in)`.
pub fn forward(&mut self, input: &Vector) -> MathResult<Vector> {
    let z = self.pre_activation(input)?;
    let a = self.activation.activate_vector(&z);
    self.input = input.clone();
    self.z = z;
    self.output = a.clone();
    Ok(a)
}
