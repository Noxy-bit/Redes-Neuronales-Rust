/// Selector de activación almacenable en cada capa (`Copy`, sin asignación
/// dinámica). Despacha a [`Sigmoid`], [`ReLU`] o [`Linear`].
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Activation {
    /// `σ(z) = 1 / (1 + e^{−z})`.
    Sigmoid,
    /// `max(0, z)`.
    ReLU,
    /// `f(z) = z`.
    Linear,
}
