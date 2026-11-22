//! Experimento 3 — Clasificación de vocales `A, E, I, O, U` en matrices 5×5.

use super::csv::{CsvWriter, num};
use super::{ExperimentResult, SEMILLA_POR_DEFECTO, exactitud_argmax};
use crate::math::{MathResult, Rng, Vector};
use crate::nn::{Activation, Network};
use std::path::Path;

/// Etiquetas de las clases en el orden de la salida *one-hot*.
pub const CLASES: [char; 5] = ['A', 'E', 'I', 'O', 'U'];

/// Lado de la matriz binaria de cada vocal.
pub const LADO: usize = 5;

/// Número de píxeles (entradas de la red): `5 × 5 = 25`.
pub const PIXELES: usize = LADO * LADO;

/// Patrones prototipo 5×5 (`1` = píxel encendido), fila por fila.
pub const PATRONES: [[u8; PIXELES]; 5] = [
    // A
    [
        0, 1, 1, 1, 0, //
        1, 0, 0, 0, 1, //
        1, 1, 1, 1, 1, //
        1, 0, 0, 0, 1, //
        1, 0, 0, 0, 1,
    ],
    // E
    [
        1, 1, 1, 1, 1, //
        1, 0, 0, 0, 0, //
        1, 1, 1, 1, 0, //
        1, 0, 0, 0, 0, //
        1, 1, 1, 1, 1,
    ],
    // I
    [
        1, 1, 1, 1, 1, //
        0, 0, 1, 0, 0, //
        0, 0, 1, 0, 0, //
        0, 0, 1, 0, 0, //
        1, 1, 1, 1, 1,
    ],
    // O
    [
        0, 1, 1, 1, 0, //
        1, 0, 0, 0, 1, //
        1, 0, 0, 0, 1, //
        1, 0, 0, 0, 1, //
        0, 1, 1, 1, 0,
    ],
    // U
    [
        1, 0, 0, 0, 1, //
        1, 0, 0, 0, 1, //
        1, 0, 0, 0, 1, //
        1, 0, 0, 0, 1, //
        0, 1, 1, 1, 0,
    ],
];

/// Archivo con la curva de aprendizaje.
pub const ARCHIVO: &str = "exp3_vocales.csv";
/// Archivo con la matriz de confusión del conjunto de prueba.
pub const ARCHIVO_CONFUSION: &str = "exp3_confusion.csv";
/// Archivo con el dataset completo.
pub const ARCHIVO_DATASET: &str = "dataset_vocales.csv";

/// Hiperparámetros del experimento 3.
#[derive(Debug, Clone)]
pub struct Configuracion {
    /// Épocas de entrenamiento.
    pub epocas: usize,
    /// Tasa de aprendizaje `α`.
    pub alpha: f64,
    /// Neuronas ocultas (topología `25 → h → 5`).
    pub ocultas: usize,
    /// Semilla del PRNG (pesos y ruido).
    pub semilla: u64,
    /// Variantes con 1 píxel invertido por vocal añadidas al entrenamiento.
    pub variantes_entrenamiento: usize,
    /// Niveles de ruido (píxeles invertidos) del conjunto de prueba.
    pub niveles_ruido_prueba: Vec<usize>,
    /// Variantes de prueba por vocal y nivel de ruido.
    pub variantes_prueba: usize,
}

impl Default for Configuracion {
    fn default() -> Self {
        Self {
            epocas: 1000,
            alpha: 0.5,
            ocultas: 10,
            semilla: SEMILLA_POR_DEFECTO,
            variantes_entrenamiento: 4,
            niveles_ruido_prueba: vec![1, 2, 3, 4, 5],
            variantes_prueba: 10,
        }
    }
}

/// Una muestra del dataset.
#[derive(Debug, Clone, PartialEq)]
pub struct Muestra {
    /// Índice de clase (`0..5` ↔ `A..U`).
    pub clase: usize,
    /// Píxeles invertidos respecto al prototipo.
    pub ruido: usize,
    /// Vector de 25 píxeles (`0.0` / `1.0`) en orden por filas.
    pub pixeles: Vector,
}

impl Muestra {
    /// Objetivo *one-hot* `e_clase ∈ ℝ⁵`.
    pub fn objetivo(&self) -> Vector {
        let mut v = Vector::zeros(CLASES.len());
        v.as_mut_slice()[self.clase] = 1.0;
        v
    }
}

/// Conjuntos de entrenamiento y prueba.
#[derive(Debug, Clone)]
pub struct Dataset {
    /// Prototipos limpios + variantes con 1 píxel invertido.
    pub entrenamiento: Vec<Muestra>,
    /// Variantes ruidosas distintas a las de entrenamiento.
    pub prueba: Vec<Muestra>,
}

/// Exactitud de prueba para un nivel de ruido.
#[derive(Debug, Clone)]
pub struct ExactitudRuido {
    /// Píxeles invertidos.
    pub ruido: usize,
    /// Exactitud obtenida.
    pub exactitud: f64,
    /// Muestras evaluadas.
    pub muestras: usize,
}

/// Resumen del experimento 3.
#[derive(Debug, Clone)]
pub struct Resumen {
    /// Topología de la red.
    pub topologia: Vec<usize>,
    /// MSE final en entrenamiento.
    pub mse_entrenamiento: f64,
    /// MSE final en prueba.
    pub mse_prueba: f64,
    /// Exactitud final en entrenamiento.
    pub exactitud_entrenamiento: f64,
    /// Exactitud final en prueba.
    pub exactitud_prueba: f64,
    /// Exactitud de los 5 prototipos limpios.
    pub exactitud_prototipos: f64,
    /// Exactitud de prueba desglosada por nivel de ruido.
    pub exactitud_por_ruido: Vec<ExactitudRuido>,
    /// Matriz de confusión de prueba `[real][predicha]`.
    pub confusion: [[usize; 5]; 5],
    /// Tamaño de los conjuntos `(entrenamiento, prueba)`.
    pub tamanos: (usize, usize),
    /// Épocas ejecutadas.
    pub epocas: usize,
}

/// Prototipo de la clase como vector de 25 componentes.
pub fn prototipo(clase: usize) -> Vector {
    Vector::new(PATRONES[clase].iter().map(|&p| p as f64).collect())
}

/// Invierte `k` píxeles distintos elegidos con `rng` (Fisher–Yates parcial).
pub fn con_ruido(base: &Vector, k: usize, rng: &mut Rng) -> Vector {
    let mut idx: Vec<usize> = (0..base.len()).collect();
    rng.shuffle(&mut idx);
    let mut v = base.clone();
    for &i in idx.iter().take(k) {
        v.as_mut_slice()[i] = 1.0 - v.as_slice()[i];
    }
    v
}

/// Construye el dataset de forma determinista. Las variantes no se repiten
/// entre sí ni con los prototipos, y ninguna muestra de prueba aparece en
/// el entrenamiento.
pub fn construir_dataset(cfg: &Configuracion) -> Dataset {
    let mut rng = Rng::new(cfg.semilla ^ 0x005E_ED0F_A51A);
    let mut vistos: Vec<Vector> = (0..CLASES.len()).map(prototipo).collect();
    let mut generar = |base: &Vector, k: usize, rng: &mut Rng| loop {
        let v = con_ruido(base, k, rng);
        if !vistos.contains(&v) {
            vistos.push(v.clone());
            return v;
        }
    };
    let mut entrenamiento = Vec::new();
    for variante in 0..=cfg.variantes_entrenamiento {
        for clase in 0..CLASES.len() {
            let base = prototipo(clase);
            let (pixeles, ruido) = if variante == 0 {
                (base, 0)
            } else {
                (generar(&base, 1, &mut rng), 1)
            };
            entrenamiento.push(Muestra {
                clase,
                ruido,
                pixeles,
            });
        }
    }
    let mut prueba = Vec::new();
    for &k in &cfg.niveles_ruido_prueba {
        for clase in 0..CLASES.len() {
            let base = prototipo(clase);
            for _ in 0..cfg.variantes_prueba {
                prueba.push(Muestra {
                    clase,
                    ruido: k,
                    pixeles: generar(&base, k, &mut rng),
                });
            }
        }
    }
    Dataset {
        entrenamiento,
        prueba,
    }
}

/// Red `25 → h → 5` con Sigmoid en ambas capas.
pub fn crear_red(ocultas: usize, semilla: u64) -> MathResult<Network> {
    Network::new(
        &[PIXELES, ocultas, CLASES.len()],
        &[Activation::Sigmoid, Activation::Sigmoid],
        semilla,
    )
}

/// Separa muestras en `(entradas, objetivos)`.
pub fn a_vectores(muestras: &[Muestra]) -> (Vec<Vector>, Vec<Vector>) {
    muestras
        .iter()
        .map(|m| (m.pixeles.clone(), m.objetivo()))
        .unzip()
}

/// Matriz de confusión `C[real][predicha]` por `argmax`. `O(N·P)`.
pub fn matriz_confusion(red: &Network, muestras: &[Muestra]) -> MathResult<[[usize; 5]; 5]> {
    let mut c = [[0usize; 5]; 5];
    for m in muestras {
        let pred = red.predict(&m.pixeles)?.argmax().unwrap_or(0);
        c[m.clase][pred] += 1;
    }
    Ok(c)
}

fn exportar_dataset(ds: &Dataset, dir: &Path) -> std::io::Result<()> {
    let mut header: Vec<String> = vec![
        "id".into(),
        "conjunto".into(),
        "vocal".into(),
        "ruido_pixeles".into(),
    ];
    for f in 0..LADO {
        for c in 0..LADO {
            header.push(format!("p{f}{c}"));
        }
    }
    let header_ref: Vec<&str> = header.iter().map(String::as_str).collect();
    let mut csv = CsvWriter::create(&dir.join(ARCHIVO_DATASET), &header_ref)?;
    let conjuntos = [("entrenamiento", &ds.entrenamiento), ("prueba", &ds.prueba)];
    let mut id = 0;
    for (nombre, muestras) in conjuntos {
        for m in muestras.iter() {
            id += 1;
            let mut fila = vec![
                id.to_string(),
                nombre.to_string(),
                CLASES[m.clase].to_string(),
                m.ruido.to_string(),
            ];
            fila.extend(m.pixeles.as_slice().iter().map(|&p| (p as u8).to_string()));
            csv.write_row(&fila)?;
        }
    }
    csv.finish()
}

/// Ejecuta el experimento y exporta `exp3_vocales.csv`, `exp3_confusion.csv`
/// y `dataset_vocales.csv`.
pub fn ejecutar(cfg: &Configuracion, dir: &Path) -> ExperimentResult<Resumen> {
    let ds = construir_dataset(cfg);
    exportar_dataset(&ds, dir)?;
    let (xs, ys) = a_vectores(&ds.entrenamiento);
    let (xt, yt) = a_vectores(&ds.prueba);
    let mut red = crear_red(cfg.ocultas, cfg.semilla)?;

    let mut csv = CsvWriter::create(
        &dir.join(ARCHIVO),
        &[
            "epoca",
            "mse_entrenamiento",
            "exactitud_entrenamiento",
            "mse_prueba",
            "exactitud_prueba",
        ],
    )?;
    let fila = |e: usize, r: &Network, mse: f64| -> MathResult<Vec<String>> {
        Ok(vec![
            e.to_string(),
            num(mse),
            num(exactitud_argmax(r, &xs, &ys)?),
            num(r.evaluate_mse(&xt, &yt)?),
            num(exactitud_argmax(r, &xt, &yt)?),
        ])
    };
    let mut filas = vec![fila(0, &red, red.evaluate_mse(&xs, &ys)?)?];
    red.train_with_callback(&xs, &ys, cfg.epocas, cfg.alpha, |e, r, mse| {
        filas.push(fila(e, r, mse)?);
        Ok(())
    })?;
    for f in &filas {
        csv.write_row(f)?;
    }
    csv.finish()?;

    let confusion = matriz_confusion(&red, &ds.prueba)?;
    let mut csv = CsvWriter::create(
        &dir.join(ARCHIVO_CONFUSION),
        &["real", "A", "E", "I", "O", "U"],
    )?;
    for (i, fila) in confusion.iter().enumerate() {
        let mut f = vec![CLASES[i].to_string()];
        f.extend(fila.iter().map(usize::to_string));
        csv.write_row(&f)?;
    }
    csv.finish()?;

    let mut exactitud_por_ruido = Vec::new();
    for &k in &cfg.niveles_ruido_prueba {
        let sub: Vec<Muestra> = ds.prueba.iter().filter(|m| m.ruido == k).cloned().collect();
        let (x, y) = a_vectores(&sub);
        exactitud_por_ruido.push(ExactitudRuido {
            ruido: k,
            exactitud: exactitud_argmax(&red, &x, &y)?,
            muestras: sub.len(),
        });
    }
    let protos: Vec<Muestra> = ds
        .entrenamiento
        .iter()
        .filter(|m| m.ruido == 0)
        .cloned()
        .collect();
    let (xp, yp) = a_vectores(&protos);

    Ok(Resumen {
        topologia: red.topology(),
        mse_entrenamiento: red.evaluate_mse(&xs, &ys)?,
        mse_prueba: red.evaluate_mse(&xt, &yt)?,
        exactitud_entrenamiento: exactitud_argmax(&red, &xs, &ys)?,
        exactitud_prueba: exactitud_argmax(&red, &xt, &yt)?,
        exactitud_prototipos: exactitud_argmax(&red, &xp, &yp)?,
        exactitud_por_ruido,
        confusion,
        tamanos: (ds.entrenamiento.len(), ds.prueba.len()),
        epocas: cfg.epocas,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn prototipos_distintos_y_binarios() {
        for (i, a) in PATRONES.iter().enumerate() {
            assert!(a.iter().all(|&p| p <= 1));
            for b in &PATRONES[i + 1..] {
                assert_ne!(a, b);
            }
        }
        assert_eq!(prototipo(0).len(), 25);
    }

    #[test]
    fn ruido_invierte_k_pixeles() {
        let base = prototipo(2);
        let mut rng = Rng::new(3);
        for k in 0..5 {
            let v = con_ruido(&base, k, &mut rng);
            let dif = v
                .sub(&base)
                .unwrap()
                .as_slice()
                .iter()
                .filter(|d| d.abs() > 0.5)
                .count();
            assert_eq!(dif, k);
        }
    }

    #[test]
    fn dataset_determinista_y_disjunto() {
        let cfg = Configuracion::default();
        let a = construir_dataset(&cfg);
        let b = construir_dataset(&cfg);
        assert_eq!(a.entrenamiento, b.entrenamiento);
        assert_eq!(a.prueba, b.prueba);
        assert_eq!(a.entrenamiento.len(), 25);
        assert_eq!(a.prueba.len(), 250);
        for t in &a.prueba {
            assert!(a.entrenamiento.iter().all(|m| m.pixeles != t.pixeles));
        }
        assert_eq!(
            a.entrenamiento[3].objetivo().as_slice(),
            &[0.0, 0.0, 0.0, 1.0, 0.0]
        );
    }

    #[test]
    fn entrena_clasifica_y_exporta() {
        let dir = crate::experiments::directorio_temporal("exp3");
        let cfg = Configuracion {
            epocas: 300,
            ..Configuracion::default()
        };
        let r = ejecutar(&cfg, &dir).unwrap();
        assert_eq!(r.exactitud_entrenamiento, 1.0);
        assert_eq!(r.exactitud_prototipos, 1.0);
        assert!(
            r.exactitud_prueba > 0.7,
            "exactitud prueba = {}",
            r.exactitud_prueba
        );
        let total: usize = r.confusion.iter().flatten().sum();
        assert_eq!(total, 250);
        let diag: usize = (0..5).map(|i| r.confusion[i][i]).sum();
        assert!((diag as f64 / 250.0 - r.exactitud_prueba).abs() < 1e-12);
        let s = std::fs::read_to_string(dir.join(ARCHIVO)).unwrap();
        assert_eq!(s.lines().count(), 1 + 301);
        let s = std::fs::read_to_string(dir.join(ARCHIVO_CONFUSION)).unwrap();
        assert_eq!(s.lines().count(), 6);
        let s = std::fs::read_to_string(dir.join(ARCHIVO_DATASET)).unwrap();
        assert_eq!(s.lines().count(), 1 + 275);
    }
}
