//! Tipo de error común para las operaciones algebraicas y de la red.

use std::fmt;

/// Error producido por operaciones con dimensiones incompatibles, accesos fuera
/// de rango o argumentos inválidos.
///
/// Las formas se expresan como `(filas, columnas)`; un vector de longitud `n`
/// se reporta como `(n, 1)` (vector columna).
#[derive(Debug, Clone, PartialEq)]
pub enum MathError {
    /// Los operandos de una operación no tienen dimensiones compatibles.
    DimensionMismatch {
        /// Nombre descriptivo de la operación que falló.
        operacion: &'static str,
        /// Forma del operando izquierdo.
        izquierda: (usize, usize),
        /// Forma del operando derecho.
        derecha: (usize, usize),
    },
    /// Se intentó acceder a una posición inexistente.
    IndexOutOfBounds {
        /// Índice solicitado `(fila, columna)`.
        indice: (usize, usize),
        /// Forma real de la estructura.
        forma: (usize, usize),
    },
    /// La cantidad de datos no coincide con la forma declarada.
    InvalidShape {
        /// Cantidad de elementos esperada (`filas × columnas`).
        esperado: usize,
        /// Cantidad de elementos recibida.
        recibido: usize,
    },
    /// Argumento semánticamente inválido (topología vacía, dataset vacío, etc.).
    InvalidArgument(String),
}

impl fmt::Display for MathError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            MathError::DimensionMismatch {
                operacion,
                izquierda,
                derecha,
            } => write!(
                f,
                "dimensiones incompatibles en {operacion}: {}x{} vs {}x{}",
                izquierda.0, izquierda.1, derecha.0, derecha.1
            ),
            MathError::IndexOutOfBounds { indice, forma } => write!(
                f,
                "índice ({}, {}) fuera de rango para forma {}x{}",
                indice.0, indice.1, forma.0, forma.1
            ),
            MathError::InvalidShape { esperado, recibido } => write!(
                f,
                "forma inválida: se esperaban {esperado} elementos y se recibieron {recibido}"
            ),
            MathError::InvalidArgument(msg) => write!(f, "argumento inválido: {msg}"),
        }
    }
}

impl std::error::Error for MathError {}

/// Alias de resultado para operaciones que pueden fallar por dimensiones.
pub type MathResult<T> = Result<T, MathError>;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn display_es_descriptivo() {
        let e = MathError::DimensionMismatch {
            operacion: "suma",
            izquierda: (2, 3),
            derecha: (3, 2),
        };
        assert_eq!(
            e.to_string(),
            "dimensiones incompatibles en suma: 2x3 vs 3x2"
        );
        let e = MathError::IndexOutOfBounds {
            indice: (5, 0),
            forma: (3, 1),
        };
        assert!(e.to_string().contains("fuera de rango"));
        let e = MathError::InvalidShape {
            esperado: 4,
            recibido: 3,
        };
        assert!(e.to_string().contains("4"));
        let e = MathError::InvalidArgument("x".into());
        assert_eq!(e.to_string(), "argumento inválido: x");
    }
}
