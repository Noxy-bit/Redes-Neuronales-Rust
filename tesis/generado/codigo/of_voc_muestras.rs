for (sample_index, sample) in samples.iter().enumerate() {
    let logits = layer.forward(sample);
    let probabilities = softmax(&logits);

    for output in 0..VOCALS.len() {
        let target = if output == sample_index { 1.0 } else { 0.0 };
        let error = (probabilities.as_slice()[output] - target) / samples.len() as f32;
        let sample_weight_gradients = Gradient::weights(error, sample.as_slice());

        for (total, sample_gradient) in weight_gradients[output]
            .iter_mut()
            .zip(sample_weight_gradients)
        {
            *total += sample_gradient;
        }
        bias_gradients[output] += Gradient::bias(error);
    }
}
