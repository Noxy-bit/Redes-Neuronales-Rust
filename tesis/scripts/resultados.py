#!/usr/bin/env python3
"""Lee resultados/*.csv (generados por el binario Rust) y produce:
  - tesis/generado/resultados.tex : macros y tablas LaTeX con valores reales
  - tesis/figuras/*.png           : gráficas a 300 DPI
No se inventa ningún valor: todo proviene de los CSV.
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parents[2]
RES = RAIZ / "resultados"
FIG = RAIZ / "tesis/figuras"
GEN = RAIZ / "tesis/generado"
FIG.mkdir(parents=True, exist_ok=True)
GEN.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "serif", "font.size": 10, "axes.grid": True, "grid.alpha": 0.3})


def leer(n):
    with open(RES / n, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def f(x, d=6):
    return f"{float(x):.{d}f}"


def sci(x, d=3):
    m, e = f"{float(x):.{d}e}".split("e")
    return f"\\num{{{m}e{int(e)}}}"


def pct(x):
    return f"{100*float(x):.2f}\\,\\%"


resumen = {(r["experimento"], r["metrica"]): r["valor"] for r in leer("resumen.csv")}
M = []


def macro(nombre, valor):
    M.append(f"\\newcommand{{\\{nombre}}}{{{valor}}}")


# ---------- Experimento 1 ----------
e1 = leer("exp1_y2x.csv")
macro("EunoEpocas", resumen[("exp1_y2x", "epocas")])
macro("EunoAlpha", resumen[("exp1_y2x", "alpha")])
macro("EunoMseIni", f(e1[0]["mse"]))
macro("EunoMseFin", sci(e1[-1]["mse"]))
macro("EunoPesoIni", f(e1[0]["peso"]))
macro("EunoPesoFin", f(e1[-1]["peso"], 9))
macro("EunoSesgoFin", sci(e1[-1]["sesgo"]))
macro("EunoPredSeis", f(resumen[("exp1_y2x", "prediccion_x6")], 9))
filas = []
for r in e1:
    if int(r["epoca"]) in (0, 1, 2, 5, 10, 50, 100, 250, 500, 750, 1000):
        filas.append(f"{r['epoca']} & {f(r['peso'])} & {f(r['sesgo'])} & {sci(r['mse'])} & {f(r['pred_x5'])} \\\\")
T1 = "\n".join(filas)
ep = [int(r["epoca"]) for r in e1]
fig, ax = plt.subplots(1, 2, figsize=(7, 2.8))
ax[0].semilogy(ep, [max(float(r["mse"]), 1e-30) for r in e1], color="#070B1E")
ax[0].set_xlabel("Época"); ax[0].set_ylabel("MSE (escala log)"); ax[0].set_title("Pérdida")
ax[1].plot(ep, [float(r["peso"]) for r in e1], label="peso $w$", color="#00A3C4")
ax[1].plot(ep, [float(r["sesgo"]) for r in e1], label="sesgo $b$", color="#7B2FF7")
ax[1].axhline(2, ls="--", lw=0.8, color="gray"); ax[1].set_xlabel("Época"); ax[1].legend(); ax[1].set_title("Parámetros")
fig.tight_layout(); fig.savefig(FIG / "exp1_y2x.png", dpi=300); plt.close(fig)

# ---------- Experimento 2 ----------
e2 = leer("exp2_xor.csv")
fin = e2[-1]
macro("EdosEpocas", resumen[("exp2_xor", "epocas")])
macro("EdosAlpha", resumen[("exp2_xor", "alpha")])
macro("EdosMsePer", f(fin["mse_perceptron"]))
macro("EdosAccPer", pct(fin["exactitud_perceptron"]))
macro("EdosMseMul", sci(fin["mse_multicapa"]))
macro("EdosAccMul", pct(fin["exactitud_multicapa"]))
T2 = "\n".join(
    f"$({a},{b})$ & {y} & {f(fin['perceptron_'+a+b],4)} & {f(fin['multicapa_'+a+b],4)} \\\\"
    for a, b, y in (("0", "0", 0), ("0", "1", 1), ("1", "0", 1), ("1", "1", 0)))
lr = leer("exp2_xor_lr.csv")
esc = {}
for r in lr:
    esc.setdefault(r["escenario"], []).append(r)
T3 = []
for e in ("baja", "optima", "alta"):
    u = esc[e][-1]
    conv = resumen[("exp2_xor_lr", f"epoca_convergencia_alpha_{e}")]
    conv = "no alcanzada" if conv == "NA" else conv
    nombre = {"baja": "Baja", "optima": "Óptima", "alta": "Alta"}[e]
    T3.append(f"{nombre} & {u['alpha']} & {f(u['mse'])} & {pct(u['exactitud'])} & {conv} \\\\")
    macro("EdosMse" + {"baja": "Baja", "optima": "Optima", "alta": "Alta"}[e], f(u["mse"]))
    macro("EdosConv" + {"baja": "Baja", "optima": "Optima", "alta": "Alta"}[e], conv)
T3 = "\n".join(T3)
fig, ax = plt.subplots(1, 2, figsize=(7, 2.8))
x = [int(r["epoca"]) for r in e2]
ax[0].plot(x, [float(r["mse_perceptron"]) for r in e2], label="Perceptrón 2-1", color="#7B2FF7")
ax[0].plot(x, [float(r["mse_multicapa"]) for r in e2], label="Multicapa 2-4-1", color="#00A3C4")
ax[0].set_xlabel("Época"); ax[0].set_ylabel("MSE"); ax[0].set_title("Perceptrón vs. multicapa"); ax[0].legend()
for e, c in (("baja", "#888888"), ("optima", "#00A3C4"), ("alta", "#C0392B")):
    ax[1].plot([int(r["epoca"]) for r in esc[e]], [float(r["mse"]) for r in esc[e]], label=f"α = {esc[e][0]['alpha']}", color=c)
ax[1].set_xlabel("Época"); ax[1].set_title("Tasas de aprendizaje"); ax[1].legend()
fig.tight_layout(); fig.savefig(FIG / "exp2_xor.png", dpi=300); plt.close(fig)

# ---------- Experimento 3 ----------
e3 = leer("exp3_vocales.csv")
macro("EtresEpocas", resumen[("exp3_vocales", "epocas")])
macro("EtresAlpha", resumen[("exp3_vocales", "alpha")])
macro("EtresMseEnt", sci(resumen[("exp3_vocales", "mse_final_entrenamiento")]))
macro("EtresMsePru", f(resumen[("exp3_vocales", "mse_final_prueba")]))
macro("EtresAccEnt", pct(resumen[("exp3_vocales", "exactitud_entrenamiento")]))
macro("EtresAccPru", pct(resumen[("exp3_vocales", "exactitud_prueba")]))
ds = leer("dataset_vocales.csv")
macro("EtresNEnt", sum(r["conjunto"] == "entrenamiento" for r in ds))
macro("EtresNPru", sum(r["conjunto"] == "prueba" for r in ds))
ruido = sorted((k[1], v) for k, v in resumen.items() if k[1].startswith("exactitud_prueba_ruido"))
T4 = "\n".join(f"{k.split('_')[-1].replace('px','')} & 50 & {pct(v)} \\\\" for k, v in ruido)
conf = leer("exp3_confusion.csv")
T5 = "\n".join(f"\\textbf{{{r['real']}}} & " + " & ".join(r[c] for c in "AEIOU") + " \\\\" for r in conf)
fig, ax = plt.subplots(1, 2, figsize=(7, 2.8))
x = [int(r["epoca"]) for r in e3]
ax[0].semilogy(x, [float(r["mse_entrenamiento"]) for r in e3], label="Entrenamiento", color="#070B1E")
ax[0].semilogy(x, [float(r["mse_prueba"]) for r in e3], label="Prueba (ruido)", color="#00A3C4")
ax[0].set_xlabel("Época"); ax[0].set_ylabel("MSE (escala log)"); ax[0].legend(); ax[0].set_title("Pérdida")
mat = [[int(r[c]) for c in "AEIOU"] for r in conf]
ax[1].imshow(mat, cmap="Blues"); ax[1].grid(False)
ax[1].set_xticks(range(5), list("AEIOU")); ax[1].set_yticks(range(5), list("AEIOU"))
ax[1].set_xlabel("Predicha"); ax[1].set_ylabel("Real"); ax[1].set_title("Matriz de confusión")
for i in range(5):
    for j in range(5):
        ax[1].text(j, i, mat[i][j], ha="center", va="center", color="white" if mat[i][j] > 25 else "black", fontsize=8)
fig.tight_layout(); fig.savefig(FIG / "exp3_vocales.png", dpi=300); plt.close(fig)
# prototipos
proto = [r for r in ds if r["conjunto"] == "entrenamiento" and r["ruido_pixeles"] == "0"]
fig, ax = plt.subplots(1, 5, figsize=(6, 1.5))
for k, r in enumerate(proto):
    ax[k].imshow([[int(r[f"p{i}{j}"]) for j in range(5)] for i in range(5)], cmap="Greys", vmin=0, vmax=1)
    ax[k].set_title(r["vocal"]); ax[k].axis("off")
fig.tight_layout(); fig.savefig(FIG / "vocales_prototipos.png", dpi=300); plt.close(fig)

# ---------- Prueba de escritorio ----------
pe = leer("prueba_escritorio.csv")
T6 = "\n".join(
    f"{r['iteracion']} & {r['entrada_x']} & {r['objetivo_y']} & {f(r['pesos_anteriores'],4)} & {f(r['sesgo_anterior'],4)} & {f(r['z'],4)} & {f(r['error'],4)} & {f(r['grad_pesos'],4)} & {f(r['pesos_nuevos'],4)} & {f(r['sesgo_nuevo'],4)} \\\\"
    for r in pe if r["escenario"].startswith("y=2x"))
macro("PeFilas", len(pe))
px = [r for r in pe if r["escenario"].startswith("XOR") and int(r["iteracion"]) <= 2]
T8 = "\n".join(
    f"{r['iteracion']} & ({r['entrada_x'].replace(';', ', ')}) & {r['objetivo_y']} & {r['capa']} & {r['neurona']} & "
    f"{float(r['z']):.4f} & {float(r['a']):.4f} & {float(r['delta']):.4f} & {float(r['sesgo_anterior']):.4f} & {float(r['sesgo_nuevo']):.4f} \\\\"
    for r in px)
macro("PeXorEsc", px[0]["escenario"])

# ---------- Distancias de Hamming entre prototipos de vocales ----------
dv = leer("dataset_vocales.csv")
proto = {r["vocal"]: [int(r[k]) for k in r if k.startswith("p") and k[1:].isdigit()]
         for r in dv if r["ruido_pixeles"] == "0" and r["conjunto"] == "entrenamiento"}
T9 = "\n".join(f"{a} & " + " & ".join(str(sum(x != y for x, y in zip(proto[a], proto[b]))) for b in "AEIOU") + " \\\\"
               for a in "AEIOU")

# ---------- Benchmarks ----------
bm = leer("benchmarks.csv")
T7 = "\n".join(
    f"{r['experimento'].replace('=', '$=$')} & {r['arquitectura']} & {r['parametros']} & {r['epocas']} & {float(r['entrenamiento_ms_media']):.3f} & {float(r['us_por_epoca']):.3f} & {float(r['inferencia_ns_promedio']):.1f} \\\\"
    for r in bm)
macro("BinKiB", bm[0]["tamano_binario_kib"])
macro("BenchSO", bm[0]["so"])
macro("BenchArch", bm[0]["cpu_arch"].replace("_", "\\_"))

out = "% Generado por tesis/scripts/resultados.py desde resultados/*.csv — no editar a mano.\n"
out += "\n".join(M) + "\n"
for n, t in (("TablaEuno", T1), ("TablaEdos", T2), ("TablaEdosLr", T3), ("TablaEtresRuido", T4),
             ("TablaConfusion", T5), ("TablaEscritorio", T6), ("TablaBench", T7), ("TablaEscritorioXor", T8), ("TablaHamming", T9)):
    out += f"\\newcommand{{\\{n}}}{{%\n{t}\n}}\n"
(GEN / "resultados.tex").write_text(out, encoding="utf-8")
print("resultados.tex y figuras generadas")
