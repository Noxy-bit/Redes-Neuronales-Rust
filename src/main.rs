//! CLI reproducible de los experimentos de la red neuronal en Rust puro.
//!
//! Uso: `cargo run --release -- --all [--export resultados] [--seed 42]`.

use redes_neuronales_rust::experiments::csv::{CsvWriter, num};
use redes_neuronales_rust::experiments::{
    ExperimentResult, SEMILLA_POR_DEFECTO, benchmarks, exp1_y2x, exp2_xor, exp3_vocales,
    prueba_escritorio,
};
use std::path::{Path, PathBuf};
use std::process::ExitCode;

const AYUDA: &str = "\
Red Neuronal desde Cero en Rust — FICCT-UAGRM 2-2026

USO:
    redes_neuronales_rust [OPCIONES]

OPCIONES:
    --all                 Ejecuta todo (experimentos, prueba de escritorio y benchmarks)
    --exp1                Experimento 1: regresión y = 2x
    --exp2                Experimento 2: XOR (perceptrón vs. multicapa y tasas de aprendizaje)
    --exp3                Experimento 3: clasificación de vocales A, E, I, O, U
    --escritorio          Prueba de escritorio paso a paso
    --bench               Benchmarks de entrenamiento e inferencia
    --experiment <X>      Alternativa: all | 1 | 2 | 3 | escritorio | bench
    --export <DIR>        Directorio de salida de los CSV (por defecto: resultados)
    --seed <N>            Semilla del PRNG (por defecto: 42)
    -h, --help            Muestra esta ayuda
";

#[derive(Default)]
struct Opciones {
    exp1: bool,
    exp2: bool,
    exp3: bool,
    escritorio: bool,
    bench: bool,
    todo: bool,
    dir: Option<PathBuf>,
    semilla: Option<u64>,
}

fn activar(op: &mut Opciones, nombre: &str) -> Result<(), String> {
    match nombre {
        "all" => op.todo = true,
        "1" | "exp1" => op.exp1 = true,
        "2" | "exp2" => op.exp2 = true,
        "3" | "exp3" => op.exp3 = true,
        "escritorio" => op.escritorio = true,
        "bench" => op.bench = true,
        otro => return Err(format!("experimento desconocido: {otro}")),
    }
    Ok(())
}

fn parsear(args: &[String]) -> Result<Option<Opciones>, String> {
    let mut op = Opciones::default();
    let mut it = args.iter();
    while let Some(a) = it.next() {
        match a.as_str() {
            "-h" | "--help" => return Ok(None),
            "--all" => op.todo = true,
            "--exp1" | "--exp2" | "--exp3" | "--escritorio" | "--bench" => {
                activar(&mut op, &a[2..])?
            }
            "--experiment" => activar(&mut op, it.next().ok_or("falta valor para --experiment")?)?,
            "--export" => {
                op.dir = Some(PathBuf::from(it.next().ok_or("falta valor para --export")?))
            }
            "--seed" => {
                let v = it.next().ok_or("falta valor para --seed")?;
                op.semilla = Some(v.parse().map_err(|_| format!("semilla inválida: {v}"))?);
            }
            otro => return Err(format!("opción desconocida: {otro}")),
        }
    }
    if op.todo {
        op.exp1 = true;
        op.exp2 = true;
        op.exp3 = true;
        op.escritorio = true;
        op.bench = true;
    }
    if !(op.exp1 || op.exp2 || op.exp3 || op.escritorio || op.bench) {
        return Ok(None);
    }
    Ok(Some(op))
}

fn pct(x: f64) -> String {
    format!("{:.2} %", 100.0 * x)
}

fn ejecutar(op: &Opciones) -> ExperimentResult<()> {
    let dir: &Path = op.dir.as_deref().unwrap_or(Path::new("resultados"));
    let semilla = op.semilla.unwrap_or(SEMILLA_POR_DEFECTO);
    let mut resumen: Vec<[String; 3]> = Vec::new();
    let mut r = |e: &str, m: &str, v: String| resumen.push([e.into(), m.into(), v]);
    println!(
        "Directorio de salida: {} | semilla = {semilla} | perfil = {}",
        dir.display(),
        benchmarks::perfil()
    );

    if op.exp1 {
        let cfg = exp1_y2x::Configuracion {
            semilla,
            ..Default::default()
        };
        let s = exp1_y2x::ejecutar(&cfg, dir)?;
        println!(
            "\n=== Experimento 1: y = 2x (neurona lineal 1-1, α = {}, {} épocas) ===",
            cfg.alpha, s.epocas
        );
        println!(
            "  inicial: w = {:.6}, b = {:.6}, MSE = {:.6}",
            s.peso_inicial, s.sesgo_inicial, s.mse_inicial
        );
        println!(
            "  final:   w = {:.6}, b = {:.6}, MSE = {:.3e}",
            s.peso_final, s.sesgo_final, s.mse_final
        );
        for (x, y, p) in &s.predicciones {
            println!("    x = {x}  y = {y}  ŷ = {p:.6}");
        }
        println!(
            "  predicción fuera de muestra x = 6 → ŷ = {:.6} (esperado 12)",
            s.prediccion_x6
        );
        r("exp1_y2x", "epocas", s.epocas.to_string());
        r("exp1_y2x", "alpha", num(cfg.alpha));
        r("exp1_y2x", "mse_inicial", num(s.mse_inicial));
        r("exp1_y2x", "mse_final", num(s.mse_final));
        r("exp1_y2x", "peso_final", num(s.peso_final));
        r("exp1_y2x", "sesgo_final", num(s.sesgo_final));
        r("exp1_y2x", "prediccion_x6", num(s.prediccion_x6));
    }

    if op.exp2 {
        let cfg = exp2_xor::Configuracion {
            semilla,
            ..Default::default()
        };
        let s = exp2_xor::ejecutar(&cfg, dir)?;
        println!(
            "\n=== Experimento 2: XOR ({} épocas, α = {}) ===",
            s.epocas, cfg.alpha
        );
        let mostrar = |n: &str, m: &exp2_xor::Metricas| {
            println!(
                "  {n:<24} MSE = {:.6}  exactitud = {}  ŷ(00,01,10,11) = [{:.4}, {:.4}, {:.4}, {:.4}]",
                m.mse,
                pct(m.exactitud),
                m.predicciones[0],
                m.predicciones[1],
                m.predicciones[2],
                m.predicciones[3]
            )
        };
        mostrar("Perceptrón 1 capa (2-1)", &s.perceptron);
        mostrar(&format!("Multicapa ({:?})", s.topologia), &s.multicapa);
        println!(
            "  Comparación de tasas de aprendizaje (red 2-{}-1):",
            cfg.ocultas
        );
        for e in &s.escenarios_lr {
            println!(
                "    α {:<7} = {:<6} MSE = {:.6}  exactitud = {}  convergencia (MSE<0.01) = {}",
                e.etiqueta,
                e.alpha,
                e.metricas.mse,
                pct(e.metricas.exactitud),
                e.epoca_convergencia
                    .map_or("no alcanzada".into(), |x| format!("época {x}"))
            );
            r(
                "exp2_xor_lr",
                &format!("mse_final_alpha_{}", e.etiqueta),
                num(e.metricas.mse),
            );
            r(
                "exp2_xor_lr",
                &format!("exactitud_alpha_{}", e.etiqueta),
                num(e.metricas.exactitud),
            );
            r(
                "exp2_xor_lr",
                &format!("epoca_convergencia_alpha_{}", e.etiqueta),
                e.epoca_convergencia.map_or("NA".into(), |x| x.to_string()),
            );
        }
        r("exp2_xor", "epocas", s.epocas.to_string());
        r("exp2_xor", "alpha", num(cfg.alpha));
        r("exp2_xor", "mse_final_perceptron", num(s.perceptron.mse));
        r(
            "exp2_xor",
            "exactitud_perceptron",
            num(s.perceptron.exactitud),
        );
        r("exp2_xor", "mse_final_multicapa", num(s.multicapa.mse));
        r(
            "exp2_xor",
            "exactitud_multicapa",
            num(s.multicapa.exactitud),
        );
    }

    if op.exp3 {
        let cfg = exp3_vocales::Configuracion {
            semilla,
            ..Default::default()
        };
        let s = exp3_vocales::ejecutar(&cfg, dir)?;
        println!(
            "\n=== Experimento 3: vocales A-E-I-O-U (red {:?}, α = {}, {} épocas) ===",
            s.topologia, cfg.alpha, s.epocas
        );
        println!(
            "  muestras: entrenamiento = {}, prueba = {}",
            s.tamanos.0, s.tamanos.1
        );
        println!(
            "  entrenamiento: MSE = {:.3e}  exactitud = {}",
            s.mse_entrenamiento,
            pct(s.exactitud_entrenamiento)
        );
        println!(
            "  prueba:        MSE = {:.6}  exactitud = {}",
            s.mse_prueba,
            pct(s.exactitud_prueba)
        );
        for e in &s.exactitud_por_ruido {
            println!(
                "    ruido {} px: exactitud = {} ({} muestras)",
                e.ruido,
                pct(e.exactitud),
                e.muestras
            );
            r(
                "exp3_vocales",
                &format!("exactitud_prueba_ruido_{}px", e.ruido),
                num(e.exactitud),
            );
        }
        println!("  matriz de confusión (filas = real, columnas = predicha):");
        println!("        A   E   I   O   U");
        for (i, f) in s.confusion.iter().enumerate() {
            println!(
                "    {}  {:>3} {:>3} {:>3} {:>3} {:>3}",
                exp3_vocales::CLASES[i],
                f[0],
                f[1],
                f[2],
                f[3],
                f[4]
            );
        }
        r("exp3_vocales", "epocas", s.epocas.to_string());
        r("exp3_vocales", "alpha", num(cfg.alpha));
        r(
            "exp3_vocales",
            "mse_final_entrenamiento",
            num(s.mse_entrenamiento),
        );
        r("exp3_vocales", "mse_final_prueba", num(s.mse_prueba));
        r(
            "exp3_vocales",
            "exactitud_entrenamiento",
            num(s.exactitud_entrenamiento),
        );
        r(
            "exp3_vocales",
            "exactitud_prototipos",
            num(s.exactitud_prototipos),
        );
        r("exp3_vocales", "exactitud_prueba", num(s.exactitud_prueba));
    }

    if op.escritorio {
        let cfg = prueba_escritorio::Configuracion {
            semilla,
            ..Default::default()
        };
        let pasos = prueba_escritorio::ejecutar(&cfg, dir)?;
        println!(
            "\n=== Prueba de escritorio: {} filas de traza exportadas ===",
            pasos.len()
        );
        for p in pasos.iter().filter(|p| p.iteracion == 1) {
            println!(
                "  [{}] capa {} neurona {}: z = {:.6}, a = {:.6}, δ = {:.6}, w' = {:?}, b' = {:.6}",
                p.escenario, p.capa, p.neurona, p.z, p.a, p.delta, p.pesos_nuevos, p.sesgo_nuevo
            );
        }
        r("prueba_escritorio", "filas", pasos.len().to_string());
    }

    if op.bench {
        let cfg = benchmarks::Configuracion {
            semilla,
            ..Default::default()
        };
        let m = benchmarks::ejecutar(&cfg, dir)?;
        println!(
            "\n=== Benchmarks ({}, binario = {:.1} KiB) ===",
            benchmarks::perfil(),
            benchmarks::tamano_binario() as f64 / 1024.0
        );
        for b in &m {
            println!(
                "  {:<8} {:<8} épocas = {:>6}  entrenamiento = {:>10.3} ms  ({:.3} µs/época)  inferencia = {:.1} ns",
                b.experimento,
                b.arquitectura,
                b.epocas,
                b.entrenamiento_ms_media,
                b.us_por_epoca,
                b.inferencia_ns
            );
        }
        r(
            "benchmarks",
            "tamano_binario_bytes",
            benchmarks::tamano_binario().to_string(),
        );
    }

    if op.todo {
        let mut csv = CsvWriter::create(
            &dir.join("resumen.csv"),
            &["experimento", "metrica", "valor"],
        )?;
        for f in &resumen {
            csv.write_row(f)?;
        }
        csv.finish()?;
    }
    println!("\nArchivos CSV escritos en {}", dir.display());
    Ok(())
}

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().skip(1).collect();
    match parsear(&args) {
        Ok(None) => {
            print!("{AYUDA}");
            ExitCode::SUCCESS
        }
        Ok(Some(op)) => match ejecutar(&op) {
            Ok(()) => ExitCode::SUCCESS,
            Err(e) => {
                eprintln!("Error: {e}");
                ExitCode::FAILURE
            }
        },
        Err(e) => {
            eprintln!("Error: {e}\n\n{AYUDA}");
            ExitCode::from(2)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn args(s: &[&str]) -> Vec<String> {
        s.iter().map(|x| x.to_string()).collect()
    }

    #[test]
    fn parsea_opciones() {
        let op = parsear(&args(&["--all", "--export", "out", "--seed", "7"]))
            .unwrap()
            .unwrap();
        assert!(op.exp1 && op.exp2 && op.exp3 && op.escritorio && op.bench);
        assert_eq!(op.dir, Some(PathBuf::from("out")));
        assert_eq!(op.semilla, Some(7));
        let op = parsear(&args(&["--experiment", "2"])).unwrap().unwrap();
        assert!(op.exp2 && !op.exp1);
        assert!(parsear(&args(&[])).unwrap().is_none());
        assert!(parsear(&args(&["--help"])).unwrap().is_none());
        assert!(parsear(&args(&["--xyz"])).is_err());
        assert!(parsear(&args(&["--seed", "abc"])).is_err());
        assert!(parsear(&args(&["--experiment", "9"])).is_err());
        assert!(parsear(&args(&["--export"])).is_err());
    }
}
