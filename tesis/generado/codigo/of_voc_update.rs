for (output, neuron) in layer.neurons_mut().iter_mut().enumerate() {
    for gradient in &weight_gradients[output] {
        largest_change = largest_change.max((LEARNING_RATE * gradient).abs());
    }
    largest_change = largest_change.max((LEARNING_RATE * bias_gradients[output]).abs());
    optimizer.update_weights(
        neuron.weights_mut().as_mut_slice(),
        &weight_gradients[output],
    );
    optimizer.update_bias(neuron.bias_mut(), bias_gradients[output]);
}
