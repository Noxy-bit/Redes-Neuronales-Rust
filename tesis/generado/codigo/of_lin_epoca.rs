for epoch in 1..=max_epochs {
    trained_epochs = epoch;
    let mut weight_gradients = vec![0.0; 1];
    let mut bias_gradient = 0.0;

    for (&x, &target) in inputs.iter().zip(&targets) {
        let input = Vector::new(vec![x]);
        let prediction = neuron.forward(&input);
        let loss_gradient = MSE::derivate(&[prediction], &[target])[0]
            / inputs.len() as f32;
        let sample_weight_gradients = Gradient::weights(loss_gradient, &[x]);

        for (total, sample) in weight_gradients.iter_mut().zip(sample_weight_gradients) {
            *total += sample;
        }
        bias_gradient += Gradient::bias(loss_gradient);
    }

    optimizer.update_weights(neuron.weights_mut().as_mut_slice(), &weight_gradients);
    optimizer.update_bias(neuron.bias_mut(), bias_gradient);

    let loss = calculate_loss(&neuron, &inputs, &targets);
    let reached_target = loss <= target_loss;
    if epoch % REPORT_EVERY == 0 || reached_target {
        print_snapshot(epoch, &neuron, &inputs, &targets);
        thread::sleep(REPORT_DELAY);
    }
    if reached_target {
        break;
    }
}
