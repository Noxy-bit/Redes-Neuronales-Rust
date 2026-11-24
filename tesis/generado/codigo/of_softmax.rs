fn softmax(logits: &Vector<f32>) -> Vector<f32> {
    let max_logit = logits
        .as_slice()
        .iter()
        .copied()
        .fold(f32::NEG_INFINITY, f32::max);
    let exponentials: Vec<f32> = logits
        .as_slice()
        .iter()
        .map(|value| (*value - max_logit).exp())
        .collect();
    let sum: f32 = exponentials.iter().sum();
    Vector::new(exponentials.iter().map(|value| value / sum).collect())
}
