fn encode(pattern: &[&str; 5]) -> Vector<f32> {
    let pixels = pattern
        .iter()
        .flat_map(|row| {
            row.chars()
                .map(|pixel| if pixel == '#' { 1.0 } else { 0.0 })
        })
        .collect();
    Vector::new(pixels)
}
