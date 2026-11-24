fn argmax(values: &Vector<f32>) -> usize {
    values
        .as_slice()
        .iter()
        .enumerate()
        .max_by(|(_, left), (_, right)| left.total_cmp(right))
        .map(|(index, _)| index)
        .unwrap_or(0)
}
