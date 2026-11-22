//! Experimento 1 — Regresión lineal `y = 2x` con una neurona lineal.

use super::csv::{CsvWriter, num};
use super::{ExperimentResult, SEMILLA_POR_DEFECTO};
use crate::math::{MathResult, Vector};
use crate::nn::{Activation, Network};
use std::path::Path;

/// Pares de entrenamiento `(x, y)` del documento base: `y = 2x`.
pub const DATOS: [(f64, f64); 5] = [(1.0, 2.0), (2.0, 4.0), (3.0, 6.0), (4.0, 8.0), (5.0, 10.0)];

/// Nombre del archivo exportado.
pub const ARCHIVO: &str = "exp1_y2x.csv";

/// Hiperparámetros del experimento 1.
#[derive(Debug, Clone)]
pub struct Configuracion {
    /// Número de épocas `E`.
    pub epocas: usize,
    /// Tasa de aprendizaje `α`.
    pub alpha: f64,
    /// Semilla del PRNG.
    pub semilla: u64,
}

impl Default for Configuracion {
    fn default() -> Self {
        Self {
            epocas: 1000,
            alpha: 0.01,
            semilla: SEMILLA_POR_DEFECTO,
        }
    }
}

/// Resumen numérico del experimento 1.
#[derive(Debug, Clone)]
pub struct Resumen {
    /// Peso inicial `w₀`.
    pub peso_inicial: f64,
    /// Sesgo inicial `b₀`.
    pub sesgo_inicial: f64,
    /// MSE antes de entrenar.
    pub mse_inicial: f64,
    /// Peso aprendido `w`.
    pub peso_final: f64,
    /// Sesgo aprendido `b`.
    pub sesgo_final: f64,
    /// MSE tras la última época.
    pub mse_final: f64,
    /// Épocas ejecutadas.
    pub epocas: usize,
    /// Predicciones finales `(x, y, ŷ)`.
    pub predicciones: Vec<(f64, f64, f64)>,
    /// Predicción fuera de la muestra para `x = 6` (valor esperado `12`).
    pub prediccion_x6: f64,
}

/// Dataset como vectores de entrada `x ∈ ℝ¹` y objetivo `y ∈ ℝ¹`.
pub fn dataset() -> (Vec<Vector>, Vec<Vector>) {
    DATOS
        .iter()
        .map(|&(x, y)| (Vector::new(vec![x]), Vector::new(vec![y])))
        .unzip()
}

/// Red `1 → 1` con activación lineal: `ŷ = w·x + b`.
pub fn crear_red(semilla: u64) -> MathResult<Network> {
    Network::new(&[1, 1], &[Activation::Linear], semilla)
}

fn fila(epoca: usize, red: &Network, mse: f64, xs: &[Vector]) -> MathResult<Vec<String>> {
    let capa = &red.layers()[0];
    let mut f = vec![
        epoca.to_string(),
        num(capa.weights().get(0, 0)?),
        num(capa.biases().get(0)?),
        num(mse),
    ];
    for x in xs {
        f.push(num(red.predict(x)?.get(0)?));
    }
    Ok(f)
}

/// Entrena la neurona y exporta `exp1_y2x.csv` con columnas
/// `epoca, peso, sesgo, mse, pred_x1 … pred_x5` (la época `0` es el estado inicial).
pub fn ejecutar(cfg: &Configuracion, dir: &Path) -> ExperimentResult<Resumen> {
    let (xs, ys) = dataset();
    let mut red = crear_red(cfg.semilla)?;
    let peso_inicial = red.layers()[0].weights().get(0, 0)?;
    let sesgo_inicial = red.layers()[0].biases().get(0)?;
    let mse_inicial = red.evaluate_mse(&xs, &ys)?;

    let mut filas = vec![fila(0, &red, mse_inicial, &xs)?];
    let historial = red.train_with_callback(&xs, &ys, cfg.epocas, cfg.alpha, |e, r, mse| {
        filas.push(fila(e, r, mse, &xs)?);
        Ok(())
    })?;

    let mut csv = CsvWriter::create(
        &dir.join(ARCHIVO),
        &[
            "epoca", "peso", "sesgo", "mse", "pred_x1", "pred_x2", "pred_x3", "pred_x4", "pred_x5",
        ],
    )?;
    for f in &filas {
        csv.write_row(f)?;
    }
    csv.finish()?;

    let mut predicciones = Vec::new();
    for (x, y) in xs.iter().zip(&ys) {
        predicciones.push((x.get(0)?, y.get(0)?, red.predict(x)?.get(0)?));
    }
    Ok(Resumen {
        peso_inicial,
        sesgo_inicial,
        mse_inicial,
        peso_final: red.layers()[0].weights().get(0, 0)?,
        sesgo_final: red.layers()[0].biases().get(0)?,
        mse_final: historial.last().copied().unwrap_or(mse_inicial),
        epocas: cfg.epocas,
        predicciones,
        prediccion_x6: red.predict(&Vector::new(vec![6.0]))?.get(0)?,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn converge_y_exporta() {
        let dir = crate::experiments::directorio_temporal("exp1");
        let r = ejecutar(&Configuracion::default(), &dir).unwrap();
        assert!(r.mse_final < 1e-4 && r.mse_final < r.mse_inicial);
        assert!((r.peso_final - 2.0).abs() < 0.01);
        assert!(r.sesgo_final.abs() < 0.05);
        assert!((r.prediccion_x6 - 12.0).abs() < 0.05);
        let s = std::fs::read_to_string(dir.join(ARCHIVO)).unwrap();
        assert_eq!(s.lines().count(), 1 + 1 + 1000);
        assert!(s.starts_with("epoca,peso,sesgo,mse"));
    }

    #[test]
    fn dataset_es_y_igual_2x() {
        let (xs, ys) = dataset();
        assert_eq!(xs.len(), 5);
        for (x, y) in xs.iter().zip(&ys) {
            assert_eq!(y.get(0).unwrap(), 2.0 * x.get(0).unwrap());
        }
    }
}
