pub fn forward(&self, inputs: &Vector<f32>) -> f32 {
    assert_eq!(
        inputs.len(),
        self.weights.len(),
        "Input and weights dimensions must match"
    );

    inputs.dot(&self.weights) + self.bias
}
