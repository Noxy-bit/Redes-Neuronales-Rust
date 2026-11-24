//! Experimento 2 — Compuerta `XOR`: perceptrón de una capa vs. red multicapa,
//! y comparación de tasas de aprendizaje.

use super::csv::{CsvWriter, num};
use super::{ExperimentResult, SEMILLA_POR_DEFECTO, exactitud_binaria};
use crate::math::{MathResult, Vector};
use crate::nn::{Activation, Network};
use std::path::Path;

/// Tabla de verdad `XOR`: `(x₁, x₂) → y`.
pub const TABLA_XOR: [([f64; 2], f64); 4] = [
    ([0.0, 0.0], 0.0),
    ([0.0, 1.0], 1.0),
    ([1.0, 0.0], 1.0),
    ([1.0, 1.0], 0.0),
];

/// Archivo de comparación perceptrón vs. multicapa.
pub const ARCHIVO: &str = "exp2_xor.csv";
/// Archivo de comparación de tasas de aprendizaje.
pub const ARCHIVO_LR: &str = "exp2_xor_lr.csv";
/// Archivo con la salida de ambos modelos entrenados sobre una malla 2D
/// (frontera de decisión).
pub const ARCHIVO_FRONTERA: &str = "exp2_xor_frontera.csv";
/// Puntos por eje de la malla `[-0.2, 1.2]²` usada para la frontera de decisión.
pub const MALLA_FRONTERA: usize = 71;

/// Hiperparámetros del experimento 2.
#[derive(Debug, Clone)]
pub struct Configuracion {
    /// Épocas de entrenamiento `E`.
    pub epocas: usize,
    /// Tasa de aprendizaje `α` principal (perceptrón y multicapa).
    pub alpha: f64,
    /// Neuronas en la capa oculta (topología `2 → h → 1`).
    pub ocultas: usize,
    /// Semilla del PRNG.
    pub semilla: u64,
    /// Escenarios `(etiqueta, α)` para la comparación de tasas.
    pub alphas: Vec<(String, f64)>,
    /// Frecuencia de registro (cada cuántas épocas se escribe una fila).
    pub registrar_cada: usize,
}

impl Default for Configuracion {
    fn default() -> Self {
        Self {
            epocas: 10_000,
            alpha: 0.5,
            ocultas: 4,
            semilla: SEMILLA_POR_DEFECTO,
            alphas: vec![
                ("baja".into(), 0.01),
                ("optima".into(), 0.5),
                ("alta".into(), 50.0),
            ],
            registrar_cada: 10,
        }
    }
}

/// Métricas finales de un modelo sobre la tabla `XOR`.
#[derive(Debug, Clone)]
pub struct Metricas {
    /// MSE final.
    pub mse: f64,
    /// Exactitud con umbral `0.5`.
    pub exactitud: f64,
    /// Salidas `ŷ` para `00, 01, 10, 11`.
    pub predicciones: [f64; 4],
}

/// Resultado de un escenario de tasa de aprendizaje.
#[derive(Debug, Clone)]
pub struct EscenarioLr {
    /// Etiqueta (`baja`, `optima`, `alta`).
    pub etiqueta: String,
    /// Tasa `α`.
    pub alpha: f64,
    /// Métricas finales.
    pub metricas: Metricas,
    /// Primera época con `MSE < 0.01` (si se alcanzó).
    pub epoca_convergencia: Option<usize>,
}

/// Resumen del experimento 2.
#[derive(Debug, Clone)]
pub struct Resumen {
    /// Perceptrón de una capa `2 → 1` (Sigmoid).
    pub perceptron: Metricas,
    /// Red multicapa `2 → h → 1` (Sigmoid/Sigmoid).
    pub multicapa: Metricas,
    /// Topología de la red multicapa.
    pub topologia: Vec<usize>,
    /// Comparación de tasas de aprendizaje.
    pub escenarios_lr: Vec<EscenarioLr>,
    /// Épocas ejecutadas.
    pub epocas: usize,
}

/// Dataset `XOR` como vectores.
pub fn dataset() -> (Vec<Vector>, Vec<Vector>) {
    TABLA_XOR
        .iter()
        .map(|(x, y)| (Vector::new(x.to_vec()), Vector::new(vec![*y])))
        .unzip()
}

/// Perceptrón de una sola capa `2 → 1` con Sigmoid (frontera lineal).
pub fn crear_perceptron(semilla: u64) -> MathResult<Network> {
    Network::new(&[2, 1], &[Activation::Sigmoid], semilla)
}

/// Red multicapa `2 → h → 1` con Sigmoid en ambas capas.
pub fn crear_multicapa(ocultas: usize, semilla: u64) -> MathResult<Network> {
    Network::new(
        &[2, ocultas, 1],
        &[Activation::Sigmoid, Activation::Sigmoid],
        semilla,
    )
}

fn predicciones(red: &Network, xs: &[Vector]) -> MathResult<[f64; 4]> {
    let mut p = [0.0; 4];
    for (i, x) in xs.iter().enumerate().take(4) {
        p[i] = red.predict(x)?.get(0)?;
    }
    Ok(p)
}

fn metricas(red: &Network, xs: &[Vector], ys: &[Vector]) -> MathResult<Metricas> {
    Ok(Metricas {
        mse: red.evaluate_mse(xs, ys)?,
        exactitud: exactitud_binaria(red, xs, ys)?,
        predicciones: predicciones(red, xs)?,
    })
}

fn debe_registrar(epoca: usize, total: usize, cada: usize) -> bool {
    epoca == 0 || epoca == total || epoca.is_multiple_of(cada.max(1))
}

/// Evalúa ambos modelos entrenados sobre una malla `n × n` en `[-0.2, 1.2]²`
/// y exporta `x1, x2, salida_perceptron, salida_multicapa`. `O(n²·P)`.
fn exportar_frontera(
    perceptron: &Network,
    multicapa: &Network,
    ruta: &Path,
) -> ExperimentResult<()> {
    let n = MALLA_FRONTERA;
    let mut csv = CsvWriter::create(ruta, &["x1", "x2", "salida_perceptron", "salida_multicapa"])?;
    let coord = |i: usize| -0.2 + 1.4 * i as f64 / (n - 1) as f64;
    for i in 0..n {
        for j in 0..n {
            let x = Vector::new(vec![coord(j), coord(i)]);
            csv.write_row(&[
                num(coord(j)),
                num(coord(i)),
                num(perceptron.predict(&x)?.get(0)?),
                num(multicapa.predict(&x)?.get(0)?),
            ])?;
        }
    }
    csv.finish()?;
    Ok(())
}

/// Ejecuta el experimento y exporta `exp2_xor.csv`, `exp2_xor_frontera.csv`
/// y `exp2_xor_lr.csv`.
pub fn ejecutar(cfg: &Configuracion, dir: &Path) -> ExperimentResult<Resumen> {
    let (xs, ys) = dataset();

    // --- Perceptrón de 1 capa vs. red multicapa (misma α y épocas) ---
    let mut perceptron = crear_perceptron(cfg.semilla)?;
    let mut multicapa = crear_multicapa(cfg.ocultas, cfg.semilla)?;
    let mut csv = CsvWriter::create(
        &dir.join(ARCHIVO),
        &[
            "epoca",
            "mse_perceptron",
            "mse_multicapa",
            "exactitud_perceptron",
            "exactitud_multicapa",
            "perceptron_00",
            "perceptron_01",
            "perceptron_10",
            "perceptron_11",
            "multicapa_00",
            "multicapa_01",
            "multicapa_10",
            "multicapa_11",
        ],
    )?;
    for epoca in 0..=cfg.epocas {
        if epoca > 0 {
            for (x, y) in xs.iter().zip(&ys) {
                perceptron.train_step(x, y, cfg.alpha)?;
                multicapa.train_step(x, y, cfg.alpha)?;
            }
        }
        if debe_registrar(epoca, cfg.epocas, cfg.registrar_cada) {
            let mp = metricas(&perceptron, &xs, &ys)?;
            let mm = metricas(&multicapa, &xs, &ys)?;
            let mut fila = vec![
                epoca.to_string(),
                num(mp.mse),
                num(mm.mse),
                num(mp.exactitud),
                num(mm.exactitud),
            ];
            fila.extend(mp.predicciones.iter().map(|&v| num(v)));
            fila.extend(mm.predicciones.iter().map(|&v| num(v)));
            csv.write_row(&fila)?;
        }
    }
    csv.finish()?;
    exportar_frontera(&perceptron, &multicapa, &dir.join(ARCHIVO_FRONTERA))?;

    // --- Comparación de tasas de aprendizaje (misma inicialización) ---
    let mut csv_lr = CsvWriter::create(
        &dir.join(ARCHIVO_LR),
        &["escenario", "alpha", "epoca", "mse", "exactitud"],
    )?;
    let mut escenarios_lr = Vec::new();
    for (etiqueta, alpha) in &cfg.alphas {
        let mut red = crear_multicapa(cfg.ocultas, cfg.semilla)?;
        let mut epoca_convergencia = None;
        for epoca in 0..=cfg.epocas {
            if epoca > 0 {
                for (x, y) in xs.iter().zip(&ys) {
                    red.train_step(x, y, *alpha)?;
                }
            }
            let mse = red.evaluate_mse(&xs, &ys)?;
            if epoca_convergencia.is_none() && mse < 0.01 {
                epoca_convergencia = Some(epoca);
            }
            if debe_registrar(epoca, cfg.epocas, cfg.registrar_cada) {
                csv_lr.write_row(&[
                    etiqueta.clone(),
                    num(*alpha),
                    epoca.to_string(),
                    num(mse),
                    num(exactitud_binaria(&red, &xs, &ys)?),
                ])?;
            }
        }
        escenarios_lr.push(EscenarioLr {
            etiqueta: etiqueta.clone(),
            alpha: *alpha,
            metricas: metricas(&red, &xs, &ys)?,
            epoca_convergencia,
        });
    }
    csv_lr.finish()?;

    Ok(Resumen {
        perceptron: metricas(&perceptron, &xs, &ys)?,
        multicapa: metricas(&multicapa, &xs, &ys)?,
        topologia: multicapa.topology(),
        escenarios_lr,
        epocas: cfg.epocas,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn perceptron_falla_y_multicapa_converge() {
        let dir = crate::experiments::directorio_temporal("exp2");
        let cfg = Configuracion {
            epocas: 5000,
            registrar_cada: 100,
            ..Configuracion::default()
        };
        let r = ejecutar(&cfg, &dir).unwrap();
        // Un perceptrón (frontera lineal) no puede superar 75 % en XOR.
        assert!(r.perceptron.exactitud <= 0.75);
        assert!(
            r.perceptron.mse > 0.15,
            "mse perceptrón = {}",
            r.perceptron.mse
        );
        assert_eq!(r.multicapa.exactitud, 1.0);
        assert!(r.multicapa.mse < 0.01);
        assert_eq!(r.topologia, vec![2, 4, 1]);
        assert_eq!(r.escenarios_lr.len(), 3);
        let opt = &r.escenarios_lr[1];
        assert!(opt.epoca_convergencia.is_some());
        assert!(r.escenarios_lr[0].metricas.mse > opt.metricas.mse);
        let s = std::fs::read_to_string(dir.join(ARCHIVO)).unwrap();
        assert_eq!(s.lines().count(), 1 + 51);
        let s = std::fs::read_to_string(dir.join(ARCHIVO_LR)).unwrap();
        assert_eq!(s.lines().count(), 1 + 3 * 51);
        let s = std::fs::read_to_string(dir.join(ARCHIVO_FRONTERA)).unwrap();
        assert_eq!(s.lines().count(), 1 + MALLA_FRONTERA * MALLA_FRONTERA);
    }
}
