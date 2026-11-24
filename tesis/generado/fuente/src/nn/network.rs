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
