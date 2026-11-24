//! Capa densa (totalmente conectada) con caché para backpropagation.

use super::activation::Activation;
use super::neuron::Neuron;
use crate::math::{MathError, MathResult, Matrix, Rng, Vector};

/// Capa densa con `n_in` entradas y `n_out` neuronas:
///
/// `z = W·x + b`,  `a = f(z)`
///
/// con `W ∈ ℝ^{n_out×n_in}`, `b ∈ ℝ^{n_out}`, `x ∈ ℝ^{n_in}`.
///
/// Durante [`Layer::forward`] se almacenan `x`, `z` y `a`; durante
/// [`Layer::backward`] se calculan:
///
/// * `δ = ∂L/∂a ⊙ f'(z)` (error local, `∂L/∂z`),
/// * `∂L/∂W = δ·xᵀ` y `∂L/∂b = δ`,
/// * `∂L/∂x = Wᵀ·δ` (se devuelve para la capa anterior).
///
/// Complejidad de `forward` y `backward`: `O(n_out·n_in)` tiempo y memoria.
#[derive(Debug, Clone, PartialEq)]
pub struct Layer {
    weights: Matrix,
    biases: Vector,
    activation: Activation,
    input: Vector,
    z: Vector,
    output: Vector,
    delta: Vector,
    grad_weights: Matrix,
    grad_biases: Vector,
}

impl Layer {
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

    /// Crea una capa con parámetros explícitos. Error si `b.len() ≠ W.rows`. `O(n_out·n_in)`.
    pub fn from_parameters(
        weights: Matrix,
        biases: Vector,
        activation: Activation,
    ) -> MathResult<Self> {
        if weights.rows() != biases.len() {
            return Err(MathError::DimensionMismatch {
                operacion: "creación de capa (W, b)",
                izquierda: weights.shape(),
                derecha: (biases.len(), 1),
            });
        }
        Ok(Self::build(weights, biases, activation))
    }

    fn build(weights: Matrix, biases: Vector, activation: Activation) -> Self {
        let (rows, cols) = weights.shape();
        Self {
            weights,
            biases,
            activation,
            input: Vector::default(),
            z: Vector::default(),
            output: Vector::default(),
            delta: Vector::default(),
            grad_weights: Matrix::zeros(rows, cols),
            grad_biases: Vector::zeros(rows),
        }
    }

    /// Número de entradas `n_in`. `O(1)`.
    pub fn n_inputs(&self) -> usize {
        self.weights.cols()
    }

    /// Número de neuronas `n_out`. `O(1)`.
    pub fn n_outputs(&self) -> usize {
        self.weights.rows()
    }

    /// Cantidad de parámetros entrenables `n_out·n_in + n_out`. `O(1)`.
    pub fn parameter_count(&self) -> usize {
        self.weights.rows() * self.weights.cols() + self.biases.len()
    }

    /// Función de activación de la capa. `O(1)`.
    pub fn activation(&self) -> Activation {
        self.activation
    }

    /// Matriz de pesos `W` (`n_out × n_in`). `O(1)`.
    pub fn weights(&self) -> &Matrix {
        &self.weights
    }

    /// Acceso mutable a `W` (usado en *gradient checking*). `O(1)`.
    pub fn weights_mut(&mut self) -> &mut Matrix {
        &mut self.weights
    }

    /// Vector de sesgos `b` (`n_out`). `O(1)`.
    pub fn biases(&self) -> &Vector {
        &self.biases
    }

    /// Acceso mutable a `b`. `O(1)`.
    pub fn biases_mut(&mut self) -> &mut Vector {
        &mut self.biases
    }

    /// Última entrada `x` almacenada por `forward`. `O(1)`.
    pub fn input(&self) -> &Vector {
        &self.input
    }

    /// Última suma ponderada `z = W·x + b`. `O(1)`.
    pub fn z(&self) -> &Vector {
        &self.z
    }

    /// Última activación `a = f(z)`. `O(1)`.
    pub fn output(&self) -> &Vector {
        &self.output
    }

    /// Último error local `δ = ∂L/∂z` calculado por `backward`. `O(1)`.
    pub fn delta(&self) -> &Vector {
        &self.delta
    }

    /// Último gradiente `∂L/∂W = δ·xᵀ`. `O(1)`.
    pub fn grad_weights(&self) -> &Matrix {
        &self.grad_weights
    }

    /// Último gradiente `∂L/∂b = δ`. `O(1)`.
    pub fn grad_biases(&self) -> &Vector {
        &self.grad_biases
    }

    /// Extrae la neurona `i` (fila `i` de `W` y `bᵢ`). `O(n_in)`.
    pub fn neuron(&self, index: usize) -> MathResult<Neuron> {
        Ok(Neuron::new(
            self.weights.row(index)?,
            self.biases.get(index)?,
            self.activation,
        ))
    }

    fn pre_activation(&self, input: &Vector) -> MathResult<Vector> {
        self.weights.mul_vector(input)?.add(&self.biases)
    }

    /// Calcula `a = f(W·x + b)` **sin** modificar la caché (inferencia pura).
    /// Error si `x.len() ≠ n_in`. `O(n_out·n_in)`.
    pub fn compute(&self, input: &Vector) -> MathResult<Vector> {
        Ok(self
            .activation
            .activate_vector(&self.pre_activation(input)?))
    }

    /// Propagación hacia adelante con caché de `x`, `z` y `a` para el
    /// posterior `backward`. Error si `x.len() ≠ n_in`. `O(n_out·n_in)`.
    pub fn forward(&mut self, input: &Vector) -> MathResult<Vector> {
        let z = self.pre_activation(input)?;
        let a = self.activation.activate_vector(&z);
        self.input = input.clone();
        self.z = z;
        self.output = a.clone();
        Ok(a)
    }

    /// Retropropagación: recibe `∂L/∂a` (longitud `n_out`), guarda
    /// `δ = ∂L/∂a ⊙ f'(z)`, `∂L/∂W = δ·xᵀ`, `∂L/∂b = δ` y devuelve
    /// `∂L/∂x = Wᵀ·δ` (longitud `n_in`). Requiere un `forward` previo.
    /// `O(n_out·n_in)`.
    pub fn backward(&mut self, grad_output: &Vector) -> MathResult<Vector> {
        let delta = grad_output.hadamard(&self.activation.derivative_vector(&self.z))?;
        self.grad_weights = Matrix::outer(&delta, &self.input);
        self.grad_biases = delta.clone();
        let grad_input = self.weights.transpose_mul_vector(&delta)?;
        self.delta = delta;
        Ok(grad_input)
    }

    /// Paso de descenso de gradiente: `W ← W − α·∂L/∂W`, `b ← b − α·∂L/∂b`.
    /// `O(n_out·n_in)`.
    pub fn apply_gradients(&mut self, learning_rate: f64) -> MathResult<()> {
        self.weights = self.weights.sub(&self.grad_weights.scale(learning_rate))?;
        self.biases = self.biases.sub(&self.grad_biases.scale(learning_rate))?;
        Ok(())
    }
}
