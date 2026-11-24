/// Crea una red con topología `[n₀, …, n_L]` (`L ≥ 1`), una activación por
/// capa (`activations.len() = L`) e inicialización reproducible con un
/// PRNG SplitMix64 sembrado con `seed`. `O(P)`.
pub fn new(topology: &[usize], activations: &[Activation], seed: u64) -> MathResult<Self> {
    if topology.len() < 2 {
        return Err(MathError::InvalidArgument(
            "la topología requiere al menos capa de entrada y de salida".into(),
        ));
    }
    if activations.len() != topology.len() - 1 {
        return Err(MathError::InvalidArgument(format!(
            "se esperaban {} activaciones y se recibieron {}",
            topology.len() - 1,
            activations.len()
        )));
    }
    if topology.contains(&0) {
        return Err(MathError::InvalidArgument(
            "ninguna capa puede tener 0 neuronas".into(),
        ));
    }
    let mut rng = Rng::new(seed);
    let layers = topology
        .windows(2)
        .zip(activations)
        .map(|(w, &act)| Layer::new(w[0], w[1], act, &mut rng))
        .collect();
    Ok(Self { layers, loss: Mse })
}
