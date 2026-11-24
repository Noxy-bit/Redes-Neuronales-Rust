/// Crea una capa con inicialización reproducible a partir de `rng`:
///
/// * `Sigmoid` / `Linear`: Xavier/Glorot uniforme, `l = √(6/(n_in+n_out))`.
/// * `ReLU`: He uniforme, `l = √(6/n_in)`.
///
/// Pesos `wᵢⱼ ~ U[−l, l)`, sesgos `b = 0`. `O(n_out·n_in)`.
pub fn new(n_inputs: usize, n_outputs: usize, activation: Activation, rng: &mut Rng) -> Self {
    let limit = match activation {
        Activation::ReLU => (6.0 / n_inputs.max(1) as f64).sqrt(),
        Activation::Sigmoid | Activation::Linear => {
            (6.0 / (n_inputs + n_outputs).max(1) as f64).sqrt()
        }
    };
    let weights = Matrix::random_uniform(n_outputs, n_inputs, -limit, limit, rng);
    Self::build(weights, Vector::zeros(n_outputs), activation)
}
