//! Fases 2 a 6 — Componentes de la red neuronal.
//!
//! * [`activation`]: funciones de activación `Sigmoid`, `ReLU`, `Linear` y derivadas.
//! * [`loss`]: función de pérdida `MSE` y su derivada.
//! * [`neuron`]: neurona individual `a = f(w·x + b)`.
//! * [`layer`]: capa densa con caché para backpropagation.
//! * [`network`]: red multicapa con `forward`, `backward`, `predict` y `train`.

pub mod activation;
pub mod layer;
pub mod loss;
pub mod network;
pub mod neuron;

pub use activation::{Activation, ActivationFn, Linear, ReLU, Sigmoid};
pub use layer::Layer;
pub use loss::{LossFn, Mse};
pub use network::Network;
pub use neuron::Neuron;
