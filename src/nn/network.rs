//! Red neuronal multicapa (perceptrón multicapa, MLP).

use super::activation::Activation;
use super::layer::Layer;
use super::loss::{LossFn, Mse};
use crate::math::{MathError, MathResult, Rng, Vector};

/// Red neuronal *feed-forward* de `L` capas densas entrenada con
/// backpropagation y descenso de gradiente estocástico (*online*).
///
/// Para una topología `[n₀, n₁, …, n_L]`, la capa `l` tiene
/// `W⁽ˡ⁾ ∈ ℝ^{n_l × n_{l−1}}` y `b⁽ˡ⁾ ∈ ℝ^{n_l}`:
///
/// * Forward: `a⁽⁰⁾ = x`, `z⁽ˡ⁾ = W⁽ˡ⁾·a⁽ˡ⁻¹⁾ + b⁽ˡ⁾`, `a⁽ˡ⁾ = f_l(z⁽ˡ⁾)`, `ŷ = a⁽ᴸ⁾`.
/// * Backward: `δ⁽ᴸ⁾ = ∂L/∂ŷ ⊙ f_L'(z⁽ᴸ⁾)`,
///   `δ⁽ˡ⁾ = (W⁽ˡ⁺¹⁾ᵀ·δ⁽ˡ⁺¹⁾) ⊙ f_l'(z⁽ˡ⁾)`.
/// * Actualización: `W⁽ˡ⁾ ← W⁽ˡ⁾ − α·δ⁽ˡ⁾·a⁽ˡ⁻¹⁾ᵀ`, `b⁽ˡ⁾ ← b⁽ˡ⁾ − α·δ⁽ˡ⁾`.
///
/// Sea `P = Σ_l n_l·n_{l−1}` el número de pesos: `forward`, `backward` y
/// `predict` cuestan `O(P)`; `train` cuesta `O(E·N·P)` para `E` épocas y `N`
/// muestras. La función de pérdida es [`Mse`].
#[derive(Debug, Clone, PartialEq)]
pub struct Network {
    layers: Vec<Layer>,
    loss: Mse,
}

impl Network {
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

    /// Crea una red a partir de capas ya construidas, validando que la salida
    /// de cada capa coincida con la entrada de la siguiente. `O(L)`.
    pub fn from_layers(layers: Vec<Layer>) -> MathResult<Self> {
        if layers.is_empty() {
            return Err(MathError::InvalidArgument(
                "la red requiere al menos una capa".into(),
            ));
        }
        for pair in layers.windows(2) {
            if pair[0].n_outputs() != pair[1].n_inputs() {
                return Err(MathError::DimensionMismatch {
                    operacion: "encadenamiento de capas",
                    izquierda: pair[0].weights().shape(),
                    derecha: pair[1].weights().shape(),
                });
            }
        }
        Ok(Self { layers, loss: Mse })
    }

    /// Capas de la red (solo lectura). `O(1)`.
    pub fn layers(&self) -> &[Layer] {
        &self.layers
    }

    /// Capas de la red (mutable). `O(1)`.
    pub fn layers_mut(&mut self) -> &mut [Layer] {
        &mut self.layers
    }

    /// Dimensión de entrada `n₀`. `O(1)`.
    pub fn n_inputs(&self) -> usize {
        self.layers[0].n_inputs()
    }

    /// Dimensión de salida `n_L`. `O(1)`.
    pub fn n_outputs(&self) -> usize {
        self.layers[self.layers.len() - 1].n_outputs()
    }

    /// Topología `[n₀, n₁, …, n_L]`. `O(L)`.
    pub fn topology(&self) -> Vec<usize> {
        std::iter::once(self.n_inputs())
            .chain(self.layers.iter().map(Layer::n_outputs))
            .collect()
    }

    /// Total de parámetros entrenables `Σ_l (n_l·n_{l−1} + n_l)`. `O(L)`.
    pub fn parameter_count(&self) -> usize {
        self.layers.iter().map(Layer::parameter_count).sum()
    }

    /// Propagación hacia adelante guardando la caché de cada capa (necesaria
    /// para `backward`). Error si `x.len() ≠ n₀`. `O(P)`.
    pub fn forward(&mut self, input: &Vector) -> MathResult<Vector> {
        let mut a = input.clone();
        for layer in &mut self.layers {
            a = layer.forward(&a)?;
        }
        Ok(a)
    }

    /// Inferencia `ŷ = f_L(W⁽ᴸ⁾·…f_1(W⁽¹⁾·x + b⁽¹⁾)… + b⁽ᴸ⁾)` sin modificar el
    /// estado de la red. Error si `x.len() ≠ n₀`. `O(P)`.
    pub fn predict(&self, input: &Vector) -> MathResult<Vector> {
        let mut a = input.clone();
        for layer in &self.layers {
            a = layer.compute(&a)?;
        }
        Ok(a)
    }

    /// Pérdida `MSE(ŷ, y)`. `O(n_L)`.
    pub fn loss(&self, prediction: &Vector, target: &Vector) -> MathResult<f64> {
        self.loss.loss(prediction, target)
    }

    /// Backpropagation a partir de la última salida calculada por `forward`:
    /// calcula y guarda `δ⁽ˡ⁾`, `∂L/∂W⁽ˡ⁾` y `∂L/∂b⁽ˡ⁾` en cada capa (de la
    /// última a la primera) y devuelve la pérdida `MSE(ŷ, y)`. `O(P)`.
    pub fn backward(&mut self, target: &Vector) -> MathResult<f64> {
        let output = self.layers[self.layers.len() - 1].output().clone();
        let loss = self.loss.loss(&output, target)?;
        let mut grad = self.loss.derivative(&output, target)?;
        for layer in self.layers.iter_mut().rev() {
            grad = layer.backward(&grad)?;
        }
        Ok(loss)
    }

    /// Aplica `θ ← θ − α·∇θ L` en todas las capas con los gradientes
    /// calculados por el último `backward`. `O(P)`.
    pub fn update(&mut self, learning_rate: f64) -> MathResult<()> {
        for layer in &mut self.layers {
            layer.apply_gradients(learning_rate)?;
        }
        Ok(())
    }

    /// Una iteración completa de aprendizaje sobre una muestra `(x, y)`:
    /// `forward → backward → update`. Devuelve la pérdida **antes** de la
    /// actualización. `O(P)`.
    pub fn train_step(
        &mut self,
        input: &Vector,
        target: &Vector,
        learning_rate: f64,
    ) -> MathResult<f64> {
        self.forward(input)?;
        let loss = self.backward(target)?;
        self.update(learning_rate)?;
        Ok(loss)
    }

    /// MSE promedio sobre un conjunto: `(1/N)·Σₖ MSE(predict(xₖ), yₖ)`. `O(N·P)`.
    pub fn evaluate_mse(&self, inputs: &[Vector], targets: &[Vector]) -> MathResult<f64> {
        validar_dataset(inputs, targets)?;
        let mut total = 0.0;
        for (x, y) in inputs.iter().zip(targets) {
            total += self.loss(&self.predict(x)?, y)?;
        }
        Ok(total / inputs.len() as f64)
    }

    /// Entrena con descenso de gradiente estocástico (una actualización por
    /// muestra, en el orden dado) durante `epochs` épocas con tasa de
    /// aprendizaje `α`. Devuelve el historial del MSE promedio medido al final
    /// de cada época (longitud `epochs`). `O(E·N·P)`.
    pub fn train(
        &mut self,
        inputs: &[Vector],
        targets: &[Vector],
        epochs: usize,
        learning_rate: f64,
    ) -> MathResult<Vec<f64>> {
        self.train_with_callback(inputs, targets, epochs, learning_rate, |_, _, _| Ok(()))
    }

    /// Igual que [`Network::train`], pero invoca `callback(época, &red, mse)`
    /// al final de cada época (épocas numeradas desde `1`) para registrar la
    /// evolución del entrenamiento. `O(E·N·P)` más el costo del callback.
    pub fn train_with_callback<F>(
        &mut self,
        inputs: &[Vector],
        targets: &[Vector],
        epochs: usize,
        learning_rate: f64,
        mut callback: F,
    ) -> MathResult<Vec<f64>>
    where
        F: FnMut(usize, &Network, f64) -> MathResult<()>,
    {
        validar_dataset(inputs, targets)?;
        let mut history = Vec::with_capacity(epochs);
        for epoch in 1..=epochs {
            for (x, y) in inputs.iter().zip(targets) {
                self.train_step(x, y, learning_rate)?;
            }
            let mse = self.evaluate_mse(inputs, targets)?;
            history.push(mse);
            callback(epoch, self, mse)?;
        }
        Ok(history)
    }
}

fn validar_dataset(inputs: &[Vector], targets: &[Vector]) -> MathResult<()> {
    if inputs.is_empty() || inputs.len() != targets.len() {
        return Err(MathError::InvalidArgument(format!(
            "dataset inválido: {} entradas y {} objetivos",
            inputs.len(),
            targets.len()
        )));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::math::Matrix;

    fn xor() -> (Vec<Vector>, Vec<Vector>) {
        let xs = [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
            .iter()
            .map(|p| Vector::new(p.to_vec()))
            .collect();
        let ys = [0.0, 1.0, 1.0, 0.0]
            .iter()
            .map(|&y| Vector::new(vec![y]))
            .collect();
        (xs, ys)
    }

    /// Compara el gradiente analítico (backpropagation) con el numérico por
    /// diferencias centrales `(L(θ+h) − L(θ−h)) / 2h` para todos los parámetros.
    fn gradient_check(topology: &[usize], acts: &[Activation], x: &[f64], y: &[f64], seed: u64) {
        let mut net = Network::new(topology, acts, seed).unwrap();
        // Sesgos no nulos para ejercitar también su gradiente.
        let mut rng = Rng::new(seed ^ 0xABCD);
        for layer in net.layers_mut() {
            for b in layer.biases_mut().as_mut_slice() {
                *b = rng.uniform(-0.5, 0.5);
            }
        }
        let x = Vector::new(x.to_vec());
        let y = Vector::new(y.to_vec());
        net.forward(&x).unwrap();
        net.backward(&y).unwrap();
        let h = 1e-5;
        let mut comprobados = 0;
        for l in 0..net.layers().len() {
            let gw = net.layers()[l].grad_weights().clone();
            let gb = net.layers()[l].grad_biases().clone();
            for i in 0..gw.as_slice().len() {
                let orig = net.layers()[l].weights().as_slice()[i];
                net.layers_mut()[l].weights_mut().as_mut_slice()[i] = orig + h;
                let lp = net.loss(&net.predict(&x).unwrap(), &y).unwrap();
                net.layers_mut()[l].weights_mut().as_mut_slice()[i] = orig - h;
                let lm = net.loss(&net.predict(&x).unwrap(), &y).unwrap();
                net.layers_mut()[l].weights_mut().as_mut_slice()[i] = orig;
                let num = (lp - lm) / (2.0 * h);
                let ana = gw.as_slice()[i];
                let rel = (num - ana).abs() / (num.abs() + ana.abs()).max(1e-8);
                assert!(
                    rel < 1e-6 || (num - ana).abs() < 1e-10,
                    "capa {l} peso {i}: numérico {num} vs analítico {ana}"
                );
                comprobados += 1;
            }
            for i in 0..gb.len() {
                let orig = net.layers()[l].biases().as_slice()[i];
                net.layers_mut()[l].biases_mut().as_mut_slice()[i] = orig + h;
                let lp = net.loss(&net.predict(&x).unwrap(), &y).unwrap();
                net.layers_mut()[l].biases_mut().as_mut_slice()[i] = orig - h;
                let lm = net.loss(&net.predict(&x).unwrap(), &y).unwrap();
                net.layers_mut()[l].biases_mut().as_mut_slice()[i] = orig;
                let num = (lp - lm) / (2.0 * h);
                let ana = gb.as_slice()[i];
                let rel = (num - ana).abs() / (num.abs() + ana.abs()).max(1e-8);
                assert!(
                    rel < 1e-6 || (num - ana).abs() < 1e-10,
                    "capa {l} sesgo {i}: numérico {num} vs analítico {ana}"
                );
                comprobados += 1;
            }
        }
        assert_eq!(comprobados, net.parameter_count());
    }

    #[test]
    fn gradient_checking_sigmoid() {
        gradient_check(
            &[2, 4, 1],
            &[Activation::Sigmoid, Activation::Sigmoid],
            &[0.3, -0.8],
            &[1.0],
            11,
        );
    }

    #[test]
    fn gradient_checking_relu_lineal_profunda() {
        gradient_check(
            &[3, 5, 4, 2],
            &[Activation::ReLU, Activation::Sigmoid, Activation::Linear],
            &[0.5, -1.2, 2.0],
            &[0.7, -0.3],
            3,
        );
    }

    #[test]
    fn gradient_checking_vocales_25_10_5() {
        let x: Vec<f64> = (0..25).map(|i| (i % 3 == 0) as u8 as f64).collect();
        gradient_check(
            &[25, 10, 5],
            &[Activation::Sigmoid, Activation::Sigmoid],
            &x,
            &[0.0, 0.0, 1.0, 0.0, 0.0],
            42,
        );
    }

    #[test]
    fn construccion_y_validaciones() {
        let net = Network::new(&[2, 3, 1], &[Activation::ReLU, Activation::Sigmoid], 1).unwrap();
        assert_eq!(net.topology(), vec![2, 3, 1]);
        assert_eq!(net.parameter_count(), 2 * 3 + 3 + 3 + 1);
        assert_eq!((net.n_inputs(), net.n_outputs()), (2, 1));
        assert!(Network::new(&[2], &[], 1).is_err());
        assert!(Network::new(&[2, 1], &[], 1).is_err());
        assert!(Network::new(&[2, 0, 1], &[Activation::ReLU, Activation::ReLU], 1).is_err());
        assert!(net.predict(&Vector::zeros(3)).is_err());
        let a = Layer::from_parameters(Matrix::zeros(3, 2), Vector::zeros(3), Activation::ReLU)
            .unwrap();
        let b = Layer::from_parameters(Matrix::zeros(1, 2), Vector::zeros(1), Activation::ReLU)
            .unwrap();
        assert!(Network::from_layers(vec![a.clone(), b]).is_err());
        assert!(Network::from_layers(vec![]).is_err());
        assert!(Network::from_layers(vec![a]).is_ok());
    }

    #[test]
    fn inicializacion_reproducible() {
        let acts = [Activation::Sigmoid, Activation::Sigmoid];
        let a = Network::new(&[2, 4, 1], &acts, 42).unwrap();
        let b = Network::new(&[2, 4, 1], &acts, 42).unwrap();
        let c = Network::new(&[2, 4, 1], &acts, 43).unwrap();
        assert_eq!(a, b);
        assert_ne!(a, c);
    }

    #[test]
    fn forward_y_predict_coinciden() {
        let mut net =
            Network::new(&[2, 3, 2], &[Activation::ReLU, Activation::Sigmoid], 9).unwrap();
        let x = Vector::new(vec![0.4, -0.6]);
        let p = net.predict(&x).unwrap();
        assert_eq!(net.forward(&x).unwrap(), p);
        assert_eq!(p.len(), 2);
    }

    #[test]
    fn backward_sin_forward_es_error() {
        let mut net = Network::new(&[1, 1], &[Activation::Linear], 1).unwrap();
        assert!(net.backward(&Vector::new(vec![1.0])).is_err());
    }

    #[test]
    fn train_step_reduce_error_en_la_muestra() {
        let mut net = Network::new(&[1, 1], &[Activation::Linear], 1).unwrap();
        let x = Vector::new(vec![2.0]);
        let y = Vector::new(vec![4.0]);
        let antes = net.train_step(&x, &y, 0.05).unwrap();
        let despues = net.loss(&net.predict(&x).unwrap(), &y).unwrap();
        assert!(despues < antes);
    }

    #[test]
    fn train_regresion_lineal_converge() {
        let xs: Vec<Vector> = (1..=5).map(|i| Vector::new(vec![i as f64])).collect();
        let ys: Vec<Vector> = (1..=5).map(|i| Vector::new(vec![2.0 * i as f64])).collect();
        let mut net = Network::new(&[1, 1], &[Activation::Linear], 42).unwrap();
        let hist = net.train(&xs, &ys, 1000, 0.01).unwrap();
        assert_eq!(hist.len(), 1000);
        assert!(hist[999] < 1e-4, "mse final = {}", hist[999]);
        assert!(hist[999] < hist[0]);
        let w = net.layers()[0].weights().get(0, 0).unwrap();
        assert!((w - 2.0).abs() < 0.01);
    }

    #[test]
    fn train_xor_multicapa_converge() {
        let (xs, ys) = xor();
        let mut net =
            Network::new(&[2, 4, 1], &[Activation::Sigmoid, Activation::Sigmoid], 42).unwrap();
        let hist = net.train(&xs, &ys, 5000, 0.5).unwrap();
        assert!(
            *hist.last().unwrap() < 0.01,
            "mse = {}",
            hist.last().unwrap()
        );
        for (x, y) in xs.iter().zip(&ys) {
            let p = net.predict(x).unwrap().as_slice()[0];
            assert_eq!((p > 0.5) as u8 as f64, y.as_slice()[0]);
        }
    }

    #[test]
    fn train_callback_y_errores() {
        let (xs, ys) = xor();
        let mut net = Network::new(&[2, 1], &[Activation::Sigmoid], 1).unwrap();
        let mut epocas = Vec::new();
        net.train_with_callback(&xs, &ys, 3, 0.1, |e, _, _| {
            epocas.push(e);
            Ok(())
        })
        .unwrap();
        assert_eq!(epocas, vec![1, 2, 3]);
        assert!(net.train(&xs, &ys[..2], 1, 0.1).is_err());
        assert!(net.train(&[], &[], 1, 0.1).is_err());
        let r = net.train_with_callback(&xs, &ys, 2, 0.1, |_, _, _| {
            Err(MathError::InvalidArgument("parada".into()))
        });
        assert!(r.is_err());
    }
}
