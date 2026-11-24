pub fn forward(&self, inputs: &Vector<f32>) -> Vector<f32> {
    assert!(
        !self.layers.is_empty(),
        "Network must contain at least one layer"
    );

    let mut outputs = self.layers[0].forward(inputs);

    for layer in self.layers.iter().skip(1) {
        outputs = layer.forward(&outputs);
    }

    outputs
}
