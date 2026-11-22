//! Prueba de escritorio: traza numérica paso a paso de las primeras
//! iteraciones de entrenamiento, generada por el mismo código de la red.

use super::csv::{CsvWriter, lista, num};
use super::{ExperimentResult, SEMILLA_POR_DEFECTO, exp1_y2x, exp2_xor};
use crate::math::{Matrix, Vector};
use crate::nn::Network;
use std::path::Path;

/// Archivo exportado.
pub const ARCHIVO: &str = "prueba_escritorio.csv";

/// Encabezados del CSV de la traza.
pub const ENCABEZADOS: [&str; 20] = [
    "escenario",
    "iteracion",
    "epoca",
    "entrada_x",
    "objetivo_y",
    "capa",
    "neurona",
    "entradas_capa",
    "pesos_anteriores",
    "sesgo_anterior",
    "z",
    "a",
    "error",
    "perdida_mse",
    "delta",
    "grad_pesos",
    "grad_sesgo",
    "alpha",
    "pesos_nuevos",
    "sesgo_nuevo",
];

/// Configuración de la prueba de escritorio.
#[derive(Debug, Clone)]
pub struct Configuracion {
    /// Iteraciones (actualizaciones por muestra) a trazar en `y = 2x`.
    pub iteraciones_y2x: usize,
    /// Tasa de aprendizaje para `y = 2x`.
    pub alpha_y2x: f64,
    /// Iteraciones a trazar en `XOR 2-2-1`.
    pub iteraciones_xor: usize,
    /// Tasa de aprendizaje para `XOR`.
    pub alpha_xor: f64,
    /// Semilla del PRNG.
    pub semilla: u64,
}

impl Default for Configuracion {
    fn default() -> Self {
        Self {
            iteraciones_y2x: 10,
            alpha_y2x: 0.01,
            iteraciones_xor: 8,
            alpha_xor: 0.5,
            semilla: SEMILLA_POR_DEFECTO,
        }
    }
}

/// Fila de la traza para una neurona en una iteración.
#[derive(Debug, Clone, PartialEq)]
pub struct PasoNeurona {
    /// Nombre del escenario.
    pub escenario: String,
    /// Iteración global (desde 1).
    pub iteracion: usize,
    /// Época a la que pertenece la iteración (desde 1).
    pub epoca: usize,
    /// Entrada `x` de la red.
    pub entrada: Vec<f64>,
    /// Objetivo `y`.
    pub objetivo: Vec<f64>,
    /// Índice de capa (desde 1).
    pub capa: usize,
    /// Índice de neurona dentro de la capa (desde 1).
    pub neurona: usize,
    /// Entradas que recibe la capa (`a⁽ˡ⁻¹⁾`).
    pub entradas_capa: Vec<f64>,
    /// Pesos `w` antes de actualizar.
    pub pesos_anteriores: Vec<f64>,
    /// Sesgo `b` antes de actualizar.
    pub sesgo_anterior: f64,
    /// Suma ponderada `z = w·x + b`.
    pub z: f64,
    /// Activación `a = f(z)`.
    pub a: f64,
    /// Error `ŷ − y` (solo neuronas de salida).
    pub error: Option<f64>,
    /// Pérdida MSE de la iteración.
    pub perdida: f64,
    /// Error local `δ = ∂L/∂z`.
    pub delta: f64,
    /// Gradiente `∂L/∂w = δ·x`.
    pub grad_pesos: Vec<f64>,
    /// Gradiente `∂L/∂b = δ`.
    pub grad_sesgo: f64,
    /// Tasa de aprendizaje `α`.
    pub alpha: f64,
    /// Pesos tras `w ← w − α·∂L/∂w`.
    pub pesos_nuevos: Vec<f64>,
    /// Sesgo tras `b ← b − α·∂L/∂b`.
    pub sesgo_nuevo: f64,
}

fn fila_matriz(m: &Matrix, i: usize) -> Vec<f64> {
    m.as_slice()[i * m.cols()..(i + 1) * m.cols()].to_vec()
}

/// Traza `iteraciones` pasos de descenso de gradiente estocástico recorriendo
/// cíclicamente el dataset, usando `forward`, `backward` y `update` reales.
pub fn trazar(
    escenario: &str,
    red: &mut Network,
    xs: &[Vector],
    ys: &[Vector],
    iteraciones: usize,
    alpha: f64,
) -> ExperimentResult<Vec<PasoNeurona>> {
    let mut pasos = Vec::new();
    for it in 0..iteraciones {
        let k = it % xs.len();
        let (x, y) = (&xs[k], &ys[k]);
        let antes: Vec<(Matrix, Vector)> = red
            .layers()
            .iter()
            .map(|l| (l.weights().clone(), l.biases().clone()))
            .collect();
        let salida = red.forward(x)?;
        let perdida = red.backward(y)?;
        let capturas: Vec<_> = red
            .layers()
            .iter()
            .map(|l| {
                (
                    l.input().clone(),
                    l.z().clone(),
                    l.output().clone(),
                    l.delta().clone(),
                    l.grad_weights().clone(),
                    l.grad_biases().clone(),
                )
            })
            .collect();
        red.update(alpha)?;
        let n_capas = red.layers().len();
        for (li, layer) in red.layers().iter().enumerate() {
            let (input, z, a, delta, gw, gb) = &capturas[li];
            for j in 0..layer.n_outputs() {
                let error = if li + 1 == n_capas {
                    Some(salida.get(j)? - y.get(j)?)
                } else {
                    None
                };
                pasos.push(PasoNeurona {
                    escenario: escenario.to_string(),
                    iteracion: it + 1,
                    epoca: it / xs.len() + 1,
                    entrada: x.as_slice().to_vec(),
                    objetivo: y.as_slice().to_vec(),
                    capa: li + 1,
                    neurona: j + 1,
                    entradas_capa: input.as_slice().to_vec(),
                    pesos_anteriores: fila_matriz(&antes[li].0, j),
                    sesgo_anterior: antes[li].1.get(j)?,
                    z: z.get(j)?,
                    a: a.get(j)?,
                    error,
                    perdida,
                    delta: delta.get(j)?,
                    grad_pesos: fila_matriz(gw, j),
                    grad_sesgo: gb.get(j)?,
                    alpha,
                    pesos_nuevos: fila_matriz(layer.weights(), j),
                    sesgo_nuevo: layer.biases().get(j)?,
                });
            }
        }
    }
    Ok(pasos)
}

/// Genera las trazas de `y = 2x` (neurona lineal `1-1`) y `XOR` (`2-2-1`
/// Sigmoid) y exporta `prueba_escritorio.csv`.
pub fn ejecutar(cfg: &Configuracion, dir: &Path) -> ExperimentResult<Vec<PasoNeurona>> {
    let (xs, ys) = exp1_y2x::dataset();
    let mut red = exp1_y2x::crear_red(cfg.semilla)?;
    let mut pasos = trazar(
        "y=2x (1-1 lineal)",
        &mut red,
        &xs,
        &ys,
        cfg.iteraciones_y2x,
        cfg.alpha_y2x,
    )?;

    let (xs, ys) = exp2_xor::dataset();
    let mut red = exp2_xor::crear_multicapa(2, cfg.semilla)?;
    pasos.extend(trazar(
        "XOR (2-2-1 sigmoid)",
        &mut red,
        &xs,
        &ys,
        cfg.iteraciones_xor,
        cfg.alpha_xor,
    )?);

    let mut csv = CsvWriter::create(&dir.join(ARCHIVO), &ENCABEZADOS)?;
    for p in &pasos {
        csv.write_row(&[
            p.escenario.clone(),
            p.iteracion.to_string(),
            p.epoca.to_string(),
            lista(&p.entrada),
            lista(&p.objetivo),
            p.capa.to_string(),
            p.neurona.to_string(),
            lista(&p.entradas_capa),
            lista(&p.pesos_anteriores),
            num(p.sesgo_anterior),
            num(p.z),
            num(p.a),
            p.error.map(num).unwrap_or_default(),
            num(p.perdida),
            num(p.delta),
            lista(&p.grad_pesos),
            num(p.grad_sesgo),
            num(p.alpha),
            lista(&p.pesos_nuevos),
            num(p.sesgo_nuevo),
        ])?;
    }
    csv.finish()?;
    Ok(pasos)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn traza_consistente_con_formulas() {
        let dir = crate::experiments::directorio_temporal("escritorio");
        let pasos = ejecutar(&Configuracion::default(), &dir).unwrap();
        // 10 iteraciones × 1 neurona + 8 iteraciones × (2 + 1) neuronas.
        assert_eq!(pasos.len(), 10 + 8 * 3);
        for p in &pasos {
            let z: f64 = p
                .pesos_anteriores
                .iter()
                .zip(&p.entradas_capa)
                .map(|(w, x)| w * x)
                .sum::<f64>()
                + p.sesgo_anterior;
            assert!((z - p.z).abs() < 1e-12);
            for ((w0, g), w1) in p
                .pesos_anteriores
                .iter()
                .zip(&p.grad_pesos)
                .zip(&p.pesos_nuevos)
            {
                assert!((w0 - p.alpha * g - w1).abs() < 1e-12);
            }
            assert!((p.sesgo_anterior - p.alpha * p.grad_sesgo - p.sesgo_nuevo).abs() < 1e-12);
            assert_eq!(p.grad_sesgo, p.delta);
        }
        // Neurona lineal: δ = 2(ŷ − y), z = a.
        let p = &pasos[0];
        assert_eq!(p.z, p.a);
        assert!((p.delta - 2.0 * p.error.unwrap()).abs() < 1e-12);
        assert!((p.perdida - p.error.unwrap().powi(2)).abs() < 1e-12);
        // La iteración 2 parte de los pesos nuevos de la iteración 1.
        assert_eq!(pasos[1].pesos_anteriores, pasos[0].pesos_nuevos);
        let s = std::fs::read_to_string(dir.join(ARCHIVO)).unwrap();
        assert_eq!(s.lines().count(), 1 + 34);
    }
}
