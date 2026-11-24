#!/usr/bin/env python3
"""Audita y ejecuta el repositorio oficial del equipo (lanorrron/neural-network).

Compila la instantánea de `repo_oficial/neural-network/`, ejecuta `cargo test`, `cargo clippy`
y sus tres experimentos (`lineal`, `booleano`, `vocal`, más `vocal a`), guarda las salidas
completas en `resultados/oficial/*.txt` y las convierte en CSV para las tablas y gráficas
de la tesis. Mide dos tiempos: el de pared del binario oficial (incluye las pausas
`thread::sleep` que el programa usa para la demostración en vivo) y el de cómputo, con una
copia temporal idéntica a la que solo se le quitan esas pausas.

Uso: python3 scripts/auditar_repo_oficial.py
"""
import csv, math, os, re, shutil, statistics, subprocess, tempfile, time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
REPO = RAIZ / "repo_oficial/neural-network"
SAL = RAIZ / "resultados/oficial"
TARGET = RAIZ / "target/oficial"
REPETICIONES = 5
EXPERIMENTOS = {"lineal": ["lineal"], "booleano": ["booleano"], "vocales": ["vocal"], "vocal_a": ["vocal", "a"]}


def cargo(args, cwd, target, **kw):
    env = {**os.environ, "CARGO_TARGET_DIR": str(target), "CARGO_TERM_COLOR": "never"}
    return subprocess.run(["cargo", *args], cwd=cwd, env=env, capture_output=True, text=True, **kw)


def limpiar(txt):
    txt = txt.replace(str(REPO), "neural-network").replace(str(Path.home()), "~")
    return re.sub(r"in \d+(\.\d+)?s", "in <t>", txt)


def escribir_csv(nombre, cabecera, filas):
    with open(SAL / nombre, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cabecera)
        w.writerows(filas)


def main():
    SAL.mkdir(parents=True, exist_ok=True)
    resumen = {}
    commit = (REPO / "COMMIT").read_text().split()[0] if (REPO / "COMMIT").exists() else "desconocido"
    resumen["commit"] = commit[:7]
    resumen["rustc"] = subprocess.run(["rustc", "--version"], capture_output=True, text=True).stdout.split()[1]

    b = cargo(["build", "--release"], REPO, TARGET)
    assert b.returncode == 0, b.stderr
    resumen["advertencias_compilacion"] = len(re.findall(r"^warning: (?!`)", b.stderr, re.M))
    binario = TARGET / "release/neural-network"
    resumen["binario_bytes"] = binario.stat().st_size
    resumen["binario_kib"] = f"{binario.stat().st_size / 1024:.1f}"

    t = cargo(["test"], REPO, TARGET)
    (SAL / "cargo_test.txt").write_text(limpiar(t.stdout + t.stderr), encoding="utf-8")
    resumen["pruebas"] = sum(int(n) for n in re.findall(r"(\d+) passed", t.stdout))
    subprocess.run(["touch", str(REPO / "src/main.rs")])
    c = cargo(["clippy", "--release"], REPO, TARGET)
    (SAL / "cargo_clippy.txt").write_text(limpiar(c.stderr), encoding="utf-8")
    resumen["clippy_errores"] = len(re.findall(r"^error(\[\w+\])?: (?!could not compile)", c.stderr, re.M))
    resumen["clippy_advertencias"] = len(re.findall(r"^warning: (?!`)", c.stderr, re.M))

    # Ejecuciones reales del binario oficial (con las pausas de demostración).
    for nombre, args in EXPERIMENTOS.items():
        ini = time.perf_counter()
        r = subprocess.run([str(binario), *args], capture_output=True, text=True, check=True)
        resumen[f"pared_s_{nombre}"] = f"{time.perf_counter() - ini:.2f}"
        (SAL / f"{nombre}.txt").write_text(r.stdout, encoding="utf-8")

    # Tiempo de cómputo: copia idéntica sin thread::sleep.
    with tempfile.TemporaryDirectory() as tmp:
        copia = Path(tmp) / "neural-network"
        shutil.copytree(REPO, copia, ignore=shutil.ignore_patterns("target"))
        for rs in copia.rglob("*.rs"):
            rs.write_text(re.sub(r"^\s*thread::sleep\([^;]*\);\s*$", "", rs.read_text(), flags=re.M))
        b2 = cargo(["build", "--release"], copia, Path(tmp) / "target")
        assert b2.returncode == 0, b2.stderr
        bin2 = Path(tmp) / "target/release/neural-network"
        for nombre, args in EXPERIMENTOS.items():
            tiempos = []
            for _ in range(REPETICIONES):
                ini = time.perf_counter()
                subprocess.run([str(bin2), *args], stdout=subprocess.DEVNULL, check=True)
                tiempos.append((time.perf_counter() - ini) * 1000)
            resumen[f"computo_ms_{nombre}"] = f"{statistics.median(tiempos):.2f}"

    # ----- Lineal: y = 2x -----
    txt = (SAL / "lineal.txt").read_text()
    filas = [(int(e), float(w), float(bb), float(m)) for e, w, bb, m in
             re.findall(r"Época\s+(\d+) \| peso = ([-\d.]+) \| bias = ([-\d.]+) \| MSE = ([-\d.e]+)", txt)]
    escribir_csv("lineal.csv", ["epoca", "peso", "bias", "mse"], filas)
    bloques = txt.strip().split("\n\n")
    final = [b for b in bloques if b.startswith("Época")][-1]
    preds = re.findall(r"^\s*(\d+) \|\s+([-\d.]+) \|\s+([-\d.]+) \|\s+([-+\d.]+)", final, re.M)
    escribir_csv("lineal_predicciones.csv", ["x", "esperado", "prediccion", "error"], preds)
    resumen["lineal_epocas"] = int(re.search(r"terminado en (\d+) épocas", txt).group(1))
    resumen["lineal_mse_final"] = re.search(r"MSE = ([\d.]+)\)", txt).group(1)
    resumen["lineal_mse_inicial"] = filas[0][3]
    resumen["lineal_peso"] = filas[-1][1]
    resumen["lineal_bias"] = filas[-1][2]
    resumen["lineal_alpha"] = 0.02
    resumen["lineal_muestras"] = len(preds)

    # ----- Booleano: 0 → falso, 1 → verdadero -----
    txt = (SAL / "booleano.txt").read_text()
    pat = r"Época\s+(\d+) \| ∇w=([-+\d.]+) ∇b=([-+\d.]+) \| w: [-+\d.]+ → ([-+\d.]+) .*?\| b: [-+\d.]+ → ([-+\d.]+)"
    filas = []
    for e, gw, gb, w, bb in re.findall(pat, txt):
        w, bb = float(w), float(bb)
        filas.append((int(e), float(gw), float(gb), w, bb, 1 / (1 + math.exp(-bb)), 1 / (1 + math.exp(-(w + bb)))))
    escribir_csv("booleano.csv", ["epoca", "grad_w", "grad_b", "w", "b", "p_verdadero_x0", "p_verdadero_x1"], filas)
    finales = re.findall(r"Entrada: (\d) \| esperado: (\w+) \| probabilidad de verdadero: ([\d.]+) \| clasificado: (\w+)", txt)
    escribir_csv("booleano_predicciones.csv", ["entrada", "esperado", "probabilidad_verdadero", "clasificado"], finales)
    resumen["booleano_epocas"] = len(filas)
    resumen["booleano_alpha"] = 0.5
    resumen["booleano_w"] = filas[-1][3]
    resumen["booleano_b"] = filas[-1][4]
    resumen["booleano_p0"] = finales[0][2]
    resumen["booleano_p1"] = finales[1][2]
    resumen["booleano_exactitud"] = sum(f[1] == f[3] for f in finales) / len(finales)

    # ----- Vocales: capa 25 → 5 con softmax -----
    txt = (SAL / "vocales.txt").read_text()
    filas = []
    for m in re.finditer(r"Época\s+(\d+)/\d+ \| cambio máximo en pesos/bias: ([\d.]+)\n((?:  .*\n?){5})", txt):
        probs, aciertos = [], 0
        for linea in m.group(3).strip("\n").split("\n"):
            esp, pred = re.search(r"(\w) → (\w)", linea).groups()
            p = dict(re.findall(r"(\w):([\d.]+)", linea.split("[")[1]))
            probs.append(float(p[esp]))
            aciertos += esp == pred
        filas.append((int(m.group(1)), float(m.group(2)), *probs, aciertos))
    escribir_csv("vocales.csv", ["epoca", "cambio_maximo", "p_A", "p_E", "p_I", "p_O", "p_U", "aciertos"], filas)
    finales = re.findall(r"Esperada: (\w) \| reconocida: (\w) \| confianza: ([\d.]+)%", txt)
    escribir_csv("vocales_predicciones.csv", ["esperada", "reconocida", "confianza_pct"], finales)
    resumen["vocales_epocas"] = len(filas)
    resumen["vocales_alpha"] = 0.3
    resumen["vocales_exactitud"] = sum(e == r for e, r, _ in finales) / len(finales)
    resumen["vocales_confianza_min"] = min(float(c) for _, _, c in finales)
    resumen["vocales_confianza_max"] = max(float(c) for _, _, c in finales)
    resumen["vocales_cambio_final"] = filas[-1][1]
    resumen["vocales_epoca_100"] = next(f[0] for f in filas if f[-1] == 5)
    txt = (SAL / "vocal_a.txt").read_text()
    pa = re.findall(r"^\s+(\w): ([\d.]+)%", txt, re.M)
    escribir_csv("vocal_a.csv", ["vocal", "probabilidad_pct"], pa)
    resumen["vocal_a_reconocida"] = re.search(r"reconoce la vocal: (\w)", txt).group(1)
    resumen["vocal_a_prob"] = dict(pa)["A"]

    escribir_csv("resumen.csv", ["metrica", "valor"], resumen.items())
    for k, v in resumen.items():
        print(f"{k:28s} {v}")


if __name__ == "__main__":
    main()
