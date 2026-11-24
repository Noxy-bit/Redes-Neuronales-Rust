pub fn forward(&self, inputs: &Vector<f32>) -> Vector<f32> {
    let mut outputs = Vec::new();

    for neuron in &self.neurons {
        outputs.push(neuron.forward(inputs));
    }

    Vector::new(outputs)
}
