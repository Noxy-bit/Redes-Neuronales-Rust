for &(input, target) in &samples {
    let logit = neuron.forward(&Vector::new(vec![input]));
    let probability = Activacion::sigmoid(logit);
    let error = (probability - target) / samples.len() as f32;
    weight_gradient += error * input;
    bias_gradient += error;
}
