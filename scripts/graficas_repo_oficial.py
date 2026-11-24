#!/usr/bin/env python3
"""Figuras 300 DPI de los experimentos del repositorio oficial (lanorrron/neural-network).

Lee exclusivamente `resultados/oficial/*.csv`, producidos por `scripts/auditar_repo_oficial.py`
a partir de la salida real del binario oficial. Misma paleta sobria que `generar_graficas.py`.

Uso: python3 scripts/graficas_repo_oficial.py
"""
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
RES = RAIZ / "resultados/oficial"
FIG = RAIZ / "tesis/figuras"
MARINO, ROJO, VERDE, GRIS_OSCURO, GRIS = "#0F2A5F", "#B91C1C", "#15803D", "#374151", "#6B7280"
VOCALES = "AEIOU"
COLORES = [MARINO, ROJO, VERDE, GRIS_OSCURO, "#7C8AA5"]
PATRONES = [  # copiados literalmente de src/experiments/vowels.rs (repositorio oficial)
    [".###.", "#...#", "#####", "#...#", "#...#"], ["#####", "#....", "####.", "#....", "#####"],
    ["#####", "..#..", "..#..", "..#..", "#####"], [".###.", "#...#", "#...#", "#...#", ".###."],
    ["#...#", "#...#", "#...#", "#...#", ".###."],
]
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10,
    "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 8.5, "axes.edgecolor": "#334155",
    "axes.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.color": "#CBD5E1", "grid.linewidth": 0.5, "grid.alpha": 0.7, "legend.frameon": False,
})


def leer(nombre):
    with open(RES / nombre, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def col(filas, k, t=float):
    return np.array([t(f[k]) for f in filas])


def guardar(fig, nombre):
    fig.savefig(FIG / nombre, dpi=300, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print(f"  tesis/figuras/{nombre}")


def fig_lineal():
    d = leer("lineal.csv")
    ep, w, b, mse = col(d, "epoca", int), col(d, "peso"), col(d, "bias"), col(d, "mse")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.9))
    a1.semilogy(ep, mse, color=MARINO, lw=1.8, marker="o", ms=2.5)
    a1.axhline(1e-12, color=ROJO, lw=0.9, ls="--", label="Meta: MSE ≤ 10⁻¹²")
    a1.set(title="(a) Pérdida MSE (f32)", xlabel="Época", ylabel="MSE (escala log)")
    a1.legend(loc="upper right")
    a2.plot(ep, w, color=MARINO, lw=1.8, label="Peso $w$")
    a2.plot(ep, b, color=ROJO, lw=1.8, label="Bias $b$")
    a2.axhline(2, color=GRIS, lw=0.8, ls=":")
    a2.axhline(0, color=GRIS, lw=0.8, ls=":")
    a2.set(title="(b) Parámetros de la neurona", xlabel="Época", ylabel="Valor")
    a2.legend(loc="center right")
    fig.tight_layout()
    guardar(fig, "fig12_oficial_lineal.png")


def fig_booleano():
    d = leer("booleano.csv")
    ep = col(d, "epoca", int)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.9))
    a1.plot(ep, col(d, "w"), color=MARINO, lw=1.8, label="Peso $w$")
    a1.plot(ep, col(d, "b"), color=ROJO, lw=1.8, label="Bias $b$")
    a1.axhline(0, color=GRIS, lw=0.8, ls=":")
    a1.set(title="(a) Parámetros por época", xlabel="Época", ylabel="Valor")
    a1.legend(loc="center right")
    a2.plot(ep, col(d, "p_verdadero_x1"), color=VERDE, lw=1.8, label="Entrada 1 (verdadero)")
    a2.plot(ep, col(d, "p_verdadero_x0"), color=ROJO, lw=1.8, label="Entrada 0 (falso)")
    a2.axhline(0.5, color=GRIS, lw=0.9, ls="--", label="Umbral 0.5")
    a2.set(title="(b) σ(w·x + b) = P(verdadero)", xlabel="Época", ylabel="Probabilidad", ylim=(0, 1))
    a2.legend(loc="center right", bbox_to_anchor=(1, 0.3))
    fig.tight_layout()
    guardar(fig, "fig13_oficial_booleano.png")


def fig_vocales():
    d = leer("vocales.csv")
    ep = col(d, "epoca", int)
    fig = plt.figure(figsize=(7.2, 4.4))
    arriba, abajo = fig.subfigures(2, 1, height_ratios=[1, 1.55], hspace=0.04)
    ejes = arriba.subplots(1, 5)
    for k, (ax, v, p) in enumerate(zip(ejes, VOCALES, PATRONES)):
        m = np.array([[1 if c == "#" else 0 for c in fila] for fila in p])
        ax.imshow(m, cmap="Greys", vmin=0, vmax=1.25)
        ax.set_xticks(np.arange(-.5, 5), minor=True)
        ax.set_yticks(np.arange(-.5, 5), minor=True)
        ax.grid(which="minor", color="#CBD5E1", lw=0.6)
        ax.grid(which="major", visible=False)
        ax.tick_params(which="both", length=0, labelbottom=False, labelleft=False)
        ax.set_title(f"{v}  →  one-hot e$_{k + 1}$", fontsize=9)
    arriba.suptitle("(a) Patrones binarios 5×5 definidos en vowels.rs", fontsize=11, y=1.04)
    a1, a2 = abajo.subplots(1, 2, gridspec_kw={"width_ratios": [1.5, 1], "wspace": 0.38})
    for v, c in zip(VOCALES, COLORES):
        a1.plot(ep, col(d, f"p_{v}"), color=c, lw=1.5, label=v)
    a1.set(title="(b) Probabilidad softmax de la clase correcta", xlabel="Época", ylabel="Probabilidad", ylim=(0, 1.02))
    a1.legend(ncol=5, loc="lower right", handlelength=1.2, columnspacing=0.8)
    a2.semilogy(ep, col(d, "cambio_maximo"), color=MARINO, lw=1.6)
    a2.set(title="(c) Cambio máximo |α·∇|", xlabel="Época", ylabel="Escala log")
    abajo.subplots_adjust(bottom=0.17, top=0.88)
    guardar(fig, "fig14_oficial_vocales.png")


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    fig_lineal()
    fig_booleano()
    fig_vocales()
