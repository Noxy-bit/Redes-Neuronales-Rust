//! Benchmarks reales de entrenamiento e inferencia con `std::time::Instant`.

use super::csv::{CsvWriter, num};
use super::{ExperimentResult, SEMILLA_POR_DEFECTO, exp1_y2x, exp2_xor, exp3_vocales};
use crate::math::{MathResult, Vector};
use crate::nn::Network;
use std::hint::black_box;
use std::path::Path;
use std::time::Instant;

/// Archivo exportado.
pub const ARCHIVO: &str = "benchmarks.csv";

/// Configuración de los benchmarks.
#[derive(Debug, Clone)]
pub struct Configuracion {
    /// Épocas a medir para `y = 2x`.
    pub epocas_y2x: Vec<usize>,
    /// Épocas a medir para `XOR`.
    pub epocas_xor: Vec<usize>,
    /// Épocas a medir para vocales.
    pub epocas_vocales: Vec<usize>,
    /// Repeticiones por configuración (se reporta media y mínimo).
    pub repeticiones: usize,
    /// Inferencias (`predict`) a cronometrar por configuración.
    pub inferencias: usize,
    /// Semilla del PRNG.
    pub semilla: u64,
}

impl Default for Configuracion {
    fn default() -> Self {
        Self {
            epocas_y2x: vec![100, 1_000, 10_000],
            epocas_xor: vec![100, 1_000, 10_000, 100_000],
            epocas_vocales: vec![10, 100, 1_000],
            repeticiones: 3,
            inferencias: 100_000,
            semilla: SEMILLA_POR_DEFECTO,
        }
    }
}

/// Fila de resultados de un benchmark.
#[derive(Debug, Clone)]
pub struct Medicion {
    /// Nombre del experimento.
    pub experimento: String,
    /// Topología como texto (`2-4-1`).
    pub arquitectura: String,
    /// Parámetros entrenables.
    pub parametros: usize,
    /// Muestras por época.
    pub muestras: usize,
    /// Épocas de entrenamiento.
    pub epocas: usize,
    /// Tiempo medio de entrenamiento (ms).
    pub entrenamiento_ms_media: f64,
    /// Tiempo mínimo de entrenamiento (ms).
    pub entrenamiento_ms_min: f64,
    /// Tiempo medio por época (µs).
    pub us_por_epoca: f64,
    /// Tiempo medio de una inferencia (ns).
    pub inferencia_ns: f64,
    /// MSE final alcanzado.
    pub mse_final: f64,
}

/// Perfil de compilación del binario en ejecución.
pub fn perfil() -> &'static str {
    if cfg!(debug_assertions) {
        "debug"
    } else {
        "release"
    }
}

/// Tamaño en bytes del ejecutable en curso (`std::env::current_exe`).
pub fn tamano_binario() -> u64 {
    std::env::current_exe()
        .and_then(std::fs::metadata)
        .map(|m| m.len())
        .unwrap_or(0)
}

fn medir(
    experimento: &str,
    crear: &dyn Fn() -> MathResult<Network>,
    xs: &[Vector],
    ys: &[Vector],
    epocas: usize,
    alpha: f64,
    cfg: &Configuracion,
) -> MathResult<Medicion> {
    let reps = cfg.repeticiones.max(1);
    let mut tiempos = Vec::with_capacity(reps);
    let mut red = crear()?;
    let mut mse_final = 0.0;
    for _ in 0..reps {
        red = crear()?;
        let t0 = Instant::now();
        let hist = red.train(xs, ys, epocas, alpha)?;
        tiempos.push(t0.elapsed().as_secs_f64() * 1e3);
        mse_final = hist.last().copied().unwrap_or(f64::NAN);
    }
    let t0 = Instant::now();
    for i in 0..cfg.inferencias {
        black_box(red.predict(black_box(&xs[i % xs.len()]))?);
    }
    let inferencia_ns = t0.elapsed().as_secs_f64() * 1e9 / cfg.inferencias.max(1) as f64;
    let media = tiempos.iter().sum::<f64>() / reps as f64;
    let minimo = tiempos.iter().copied().fold(f64::INFINITY, f64::min);
    Ok(Medicion {
        experimento: experimento.to_string(),
        arquitectura: red
            .topology()
            .iter()
            .map(usize::to_string)
            .collect::<Vec<_>>()
            .join("-"),
        parametros: red.parameter_count(),
        muestras: xs.len(),
        epocas,
        entrenamiento_ms_media: media,
        entrenamiento_ms_min: minimo,
        us_por_epoca: media * 1e3 / epocas.max(1) as f64,
        inferencia_ns,
        mse_final,
    })
}

/// Ejecuta todos los benchmarks y exporta `benchmarks.csv`.
pub fn ejecutar(cfg: &Configuracion, dir: &Path) -> ExperimentResult<Vec<Medicion>> {
    let mut mediciones = Vec::new();
    let semilla = cfg.semilla;

    let (xs, ys) = exp1_y2x::dataset();
    let c1 = exp1_y2x::Configuracion::default();
    for &e in &cfg.epocas_y2x {
        mediciones.push(medir(
            "y=2x",
            &|| exp1_y2x::crear_red(semilla),
            &xs,
            &ys,
            e,
            c1.alpha,
            cfg,
        )?);
    }

    let (xs, ys) = exp2_xor::dataset();
    let c2 = exp2_xor::Configuracion::default();
    for &e in &cfg.epocas_xor {
        mediciones.push(medir(
            "XOR",
            &|| exp2_xor::crear_multicapa(c2.ocultas, semilla),
            &xs,
            &ys,
            e,
            c2.alpha,
            cfg,
        )?);
    }

    let c3 = exp3_vocales::Configuracion::default();
    let ds = exp3_vocales::construir_dataset(&c3);
    let (xs, ys) = exp3_vocales::a_vectores(&ds.entrenamiento);
    for &e in &cfg.epocas_vocales {
        mediciones.push(medir(
            "vocales",
            &|| exp3_vocales::crear_red(c3.ocultas, semilla),
            &xs,
            &ys,
            e,
            c3.alpha,
            cfg,
        )?);
    }

    let bytes = tamano_binario();
    let mut csv = CsvWriter::create(
        &dir.join(ARCHIVO),
        &[
            "experimento",
            "arquitectura",
            "parametros",
            "muestras",
            "epocas",
            "repeticiones",
            "entrenamiento_ms_media",
            "entrenamiento_ms_min",
            "us_por_epoca",
            "inferencias",
            "inferencia_ns_promedio",
            "mse_final",
            "perfil",
            "so",
            "cpu_arch",
            "tamano_binario_bytes",
            "tamano_binario_kib",
        ],
    )?;
    for m in &mediciones {
        csv.write_row(&[
            m.experimento.clone(),
            m.arquitectura.clone(),
            m.parametros.to_string(),
            m.muestras.to_string(),
            m.epocas.to_string(),
            cfg.repeticiones.max(1).to_string(),
            format!("{:.4}", m.entrenamiento_ms_media),
            format!("{:.4}", m.entrenamiento_ms_min),
            format!("{:.4}", m.us_por_epoca),
            cfg.inferencias.to_string(),
            format!("{:.2}", m.inferencia_ns),
            num(m.mse_final),
            perfil().to_string(),
            std::env::consts::OS.to_string(),
            std::env::consts::ARCH.to_string(),
            bytes.to_string(),
            format!("{:.1}", bytes as f64 / 1024.0),
        ])?;
    }
    csv.finish()?;
    Ok(mediciones)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn mide_y_exporta() {
        let dir = crate::experiments::directorio_temporal("bench");
        let cfg = Configuracion {
            epocas_y2x: vec![10],
            epocas_xor: vec![10, 20],
            epocas_vocales: vec![2],
            repeticiones: 2,
            inferencias: 100,
            ..Configuracion::default()
        };
        let m = ejecutar(&cfg, &dir).unwrap();
        assert_eq!(m.len(), 4);
        assert!(
            m.iter()
                .all(|x| x.entrenamiento_ms_media >= 0.0 && x.inferencia_ns > 0.0)
        );
        assert!(
            m.iter()
                .all(|x| x.entrenamiento_ms_min <= x.entrenamiento_ms_media + 1e-12)
        );
        assert_eq!(m[1].arquitectura, "2-4-1");
        assert_eq!(m[3].arquitectura, "25-10-5");
        assert_eq!(m[3].parametros, 25 * 10 + 10 + 10 * 5 + 5);
        assert!(tamano_binario() > 0);
        assert!(["debug", "release"].contains(&perfil()));
        let s = std::fs::read_to_string(dir.join(ARCHIVO)).unwrap();
        assert_eq!(s.lines().count(), 5);
    }
}
