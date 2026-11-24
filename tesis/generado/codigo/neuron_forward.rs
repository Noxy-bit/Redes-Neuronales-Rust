/// Propagación hacia adelante `a = f(w·x + b)`. Error si `x.len() ≠ n`. `O(n)`.
pub fn forward(&self, inputs: &Vector) -> MathResult<f64> {
    Ok(self.activation.activate(self.weighted_sum(inputs)?))
}
