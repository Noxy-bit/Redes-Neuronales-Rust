#!/usr/bin/env python3
"""Genera las figuras científicas (PNG, 300 DPI) de la tesis en `tesis/figuras/`.

Todas las curvas experimentales se leen exclusivamente de `resultados/*.csv`
(producidos por `cargo run --release -- --all`). La única figura analítica es
`fig01_activaciones.png`, que grafica las fórmulas de Sigmoid y ReLU.

Uso: python3 scripts/generar_graficas.py
"""
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
RES = RAIZ / "resultados"
FIG = RAIZ / "tesis" / "figuras"
DPI = 300

# Paleta sobria científica (documento académico): azul marino, rojo técnico, verde bosque y grises.
MARINO = "#0F2A5F"
AZUL = MARINO
ROJO = "#B91C1C"
VERDE = "#15803D"
GRIS_OSCURO = "#374151"
GRIS = "#6B7280"
CELESTE_GRIS = "#C7D2E0"
CIAN = GRIS_OSCURO
PURPURA = VERDE
NARANJA = ROJO

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "axes.edgecolor": "#334155",
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": "#CBD5E1",
    "grid.linewidth": 0.5,
    "grid.alpha": 0.7,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "legend.frameon": False,
})


def leer(nombre):
    with open(RES / nombre, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def col(filas, clave, tipo=float):
    return np.array([tipo(f[clave]) for f in filas])


def resumen():
    return {(f["experimento"], f["metrica"]): f["valor"] for f in leer("resumen.csv")}


def guardar(fig, nombre):
    fig.savefig(FIG / nombre, dpi=DPI, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print(f"  {nombre}")


def fig01_activaciones():
    z = np.linspace(-6, 6, 601)
    s = 1 / (1 + np.exp(-z))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.0))
    a1.plot(z, s, color=AZUL, lw=2, label=r"$\sigma(z)=1/(1+e^{-z})$")
    a1.plot(z, s * (1 - s), color=CIAN, lw=2, ls="--", label=r"$\sigma'(z)=\sigma(z)(1-\sigma(z))$")
    a1.set(title="(a) Sigmoid", xlabel="$z$", ylabel="Valor", ylim=(-0.05, 1.05))
    a1.legend(loc="upper left", fontsize=8)
    a2.plot(z, np.maximum(0, z), color=PURPURA, lw=2, label=r"$\mathrm{ReLU}(z)=\max(0,z)$")
    a2.plot(z, (z > 0).astype(float), color=NARANJA, lw=2, ls="--", label=r"$\mathrm{ReLU}'(z)=\mathbb{1}[z>0]$")
    a2.set(title="(b) ReLU", xlabel="$z$", ylim=(-0.3, 6.2))
    a2.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    guardar(fig, "fig01_activaciones.png")


def fig02_y2x():
    d = leer("exp1_y2x.csv")
    ep, w, b = col(d, "epoca", int), col(d, "peso"), col(d, "sesgo")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.0))
    a1.plot(ep + 1, w, color=AZUL, lw=1.8, label="Peso $w$")
    a1.plot(ep + 1, b, color=NARANJA, lw=1.8, label="Sesgo $b$")
    a1.axhline(2, color=GRIS, lw=0.8, ls=":")
    a1.axhline(0, color=GRIS, lw=0.8, ls=":")
    a1.set_xscale("log")
    a1.set(title="(a) Evolución de los parámetros", xlabel="Época + 1 (escala log)", ylabel="Valor")
    a1.legend(loc="center right")
    x = np.arange(1, 6)
    y = 2 * x
    xs = np.linspace(0, 6, 50)
    a2.plot(xs, w[0] * xs + b[0], color=GRIS, ls="--", lw=1.2, label=f"Época 0: ŷ = {w[0]:.3f}x + {b[0]:.3f}")
    a2.plot(xs, w[-1] * xs + b[-1], color=AZUL, lw=2, label=f"Época {ep[-1]}: ŷ = {w[-1]:.4f}x + {b[-1]:.1e}")
    a2.scatter(x, y, s=36, color=NARANJA, zorder=3, label="Datos reales (x, 2x)")
    a2.set(title="(b) Recta ajustada vs. datos", xlabel="$x$", ylabel="$y$", xlim=(0, 6), ylim=(0, 14.5))
    a2.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    guardar(fig, "fig02_exp1_convergencia_y2x.png")


def fig03_mse_y2x():
    d = leer("exp1_y2x.csv")
    ep, mse = col(d, "epoca", int), col(d, "mse")
    fig, ax = plt.subplots(figsize=(6.0, 3.2))
    ax.semilogy(ep, mse, color=AZUL, lw=1.8)
    ax.scatter([ep[0], ep[-1]], [mse[0], mse[-1]], color=NARANJA, zorder=3, s=22)
    ax.annotate(f"MSE inicial = {mse[0]:.3f}", (ep[0], mse[0]), xytext=(60, mse[0] / 3), fontsize=8)
    ax.annotate(f"MSE final = {mse[-1]:.2e}", (ep[-1], mse[-1]), xytext=(ep[-1] - 380, mse[-1] * 40), fontsize=8)
    ax.set(xlabel="Época", ylabel="MSE (escala logarítmica)", xlim=(-20, ep[-1] + 20))
    fig.tight_layout()
    guardar(fig, "fig03_exp1_mse_y2x.png")


def fig04_xor():
    d = leer("exp2_xor.csv")
    ep = col(d, "epoca", int)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.0))
    a1.semilogy(ep, col(d, "mse_perceptron"), color=ROJO, lw=1.8, label="Perceptrón 2-1")
    a1.semilogy(ep, col(d, "mse_multicapa"), color=AZUL, lw=1.8, label="Multicapa 2-4-1")
    a1.set(title="(a) MSE por época", xlabel="Época", ylabel="MSE (escala log)")
    a1.legend(loc="lower left")
    a2.plot(ep, col(d, "exactitud_perceptron") * 100, color=ROJO, lw=1.6, label="Perceptrón 2-1")
    a2.plot(ep, col(d, "exactitud_multicapa") * 100, color=AZUL, lw=1.6, label="Multicapa 2-4-1")
    a2.set(title="(b) Exactitud (umbral 0.5)", xlabel="Época", ylabel="Exactitud (%)", ylim=(0, 105))
    a2.legend(loc="lower right")
    fig.tight_layout()
    guardar(fig, "fig04_exp2_xor_convergencia.png")


def fig05_xor_lr():
    d = leer("exp2_xor_lr.csv")
    r = resumen()
    colores = {"baja": NARANJA, "optima": AZUL, "alta": ROJO}
    nombres = {"baja": "baja", "optima": "óptima", "alta": "alta"}
    fig, ax = plt.subplots(figsize=(6.2, 3.3))
    for esc in ["baja", "optima", "alta"]:
        f = [x for x in d if x["escenario"] == esc]
        alpha = float(f[0]["alpha"])
        conv = r[("exp2_xor_lr", f"epoca_convergencia_alpha_{esc}")]
        extra = f", converge en época {conv}" if conv != "NA" else ", no converge"
        ax.semilogy(col(f, "epoca", int), col(f, "mse"), color=colores[esc], lw=1.8,
                    label=f"α {nombres[esc]} = {alpha:g}{extra}")
    ax.axhline(0.01, color=GRIS, lw=0.8, ls=":")
    ax.text(10000, 0.0088, "MSE = 0.01", ha="right", va="top", fontsize=8, color=GRIS)
    ax.set(xlabel="Época", ylabel="MSE (escala log)")
    ax.legend(loc="center right", bbox_to_anchor=(1.0, 0.62), fontsize=8)
    fig.tight_layout()
    guardar(fig, "fig05_exp2_xor_learning_rates.png")


def fig06_xor_frontera():
    d = leer("exp2_xor_frontera.csv")
    x1, x2 = col(d, "x1"), col(d, "x2")
    n = int(round(np.sqrt(len(d))))
    X1, X2 = x1.reshape(n, n), x2.reshape(n, n)
    cmap = LinearSegmentedColormap.from_list("rn", ["#FFFFFF", CELESTE_GRIS, "#5B7299", MARINO])
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.3), sharey=True)
    puntos = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 0)]
    for ax, clave, titulo in [(axs[0], "salida_perceptron", "(a) Perceptrón 2-1"),
                              (axs[1], "salida_multicapa", "(b) Multicapa 2-4-1")]:
        Z = col(d, clave).reshape(n, n)
        cf = ax.contourf(X1, X2, Z, levels=np.linspace(0, 1, 21), cmap=cmap)
        ax.contour(X1, X2, Z, levels=[0.5], colors=MARINO, linewidths=1.6)
        for (a, b), y in puntos:
            ax.scatter(a, b, s=70, marker="o" if y else "X", color=NARANJA if y else MARINO,
                       edgecolor="white", linewidth=1, zorder=3)
            ax.annotate(f"y={y}", (a, b), xytext=(6, 6), textcoords="offset points", fontsize=8, color=MARINO)
        ax.set(title=titulo, xlabel="$x_1$", xlim=(-0.2, 1.2), ylim=(-0.2, 1.2), aspect="equal")
        ax.grid(False)
    axs[0].set_ylabel("$x_2$")
    cb = fig.colorbar(cf, ax=axs, fraction=0.035, pad=0.03)
    cb.set_label("Salida ŷ (línea: ŷ = 0.5)")
    guardar(fig, "fig06_exp2_xor_frontera.png")


def matriz_vocal(fila):
    return np.array([float(fila[f"p{i}{j}"]) for i in range(5) for j in range(5)]).reshape(5, 5)


def fig07_dataset():
    d = leer("dataset_vocales.csv")
    vocales = "AEIOU"
    proto = {f["vocal"]: f for f in d if f["conjunto"] == "entrenamiento" and f["ruido_pixeles"] == "0"}
    ruido = [(2, "prueba"), (5, "prueba")]
    fig, axs = plt.subplots(3, 5, figsize=(6.4, 4.3))
    cmap = LinearSegmentedColormap.from_list("bin", ["#FFFFFF", MARINO])
    for j, v in enumerate(vocales):
        base = matriz_vocal(proto[v])
        filas = [(base, f"{v} (prototipo)")]
        for k, conj in ruido:
            f = next(x for x in d if x["vocal"] == v and x["conjunto"] == conj and x["ruido_pixeles"] == str(k))
            filas.append((matriz_vocal(f), f"{v} (ruido {k} px)"))
        for i, (m, t) in enumerate(filas):
            ax = axs[i, j]
            ax.imshow(m, cmap=cmap, vmin=0, vmax=1)
            dif = (m != base)
            for (r, c) in zip(*np.nonzero(dif)):
                ax.add_patch(plt.Rectangle((c - 0.5, r - 0.5), 1, 1, fill=False, ec=NARANJA, lw=1.6))
            ax.set_xticks(np.arange(-0.5, 5, 1), minor=True)
            ax.set_yticks(np.arange(-0.5, 5, 1), minor=True)
            ax.grid(which="minor", color="#CBD5E1", lw=0.5)
            ax.grid(which="major", visible=False)
            ax.tick_params(which="both", length=0, labelbottom=False, labelleft=False)
            ax.set_title(t, fontsize=8)
    fig.tight_layout(h_pad=0.8)
    guardar(fig, "fig07_exp3_dataset_vocales.png")


def fig08_vocales():
    d = leer("exp3_vocales.csv")
    ep = col(d, "epoca", int)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.0))
    a1.semilogy(ep, col(d, "mse_entrenamiento"), color=AZUL, lw=1.8, label="Entrenamiento")
    a1.semilogy(ep, col(d, "mse_prueba"), color=NARANJA, lw=1.8, label="Prueba (con ruido)")
    a1.set(title="(a) MSE por época", xlabel="Época", ylabel="MSE (escala log)")
    a1.legend(loc="upper right")
    ea, ep_ = col(d, "exactitud_entrenamiento") * 100, col(d, "exactitud_prueba") * 100
    a2.plot(ep, ea, color=AZUL, lw=1.8, label=f"Entrenamiento (final {ea[-1]:.1f} %)")
    a2.plot(ep, ep_, color=NARANJA, lw=1.8, label=f"Prueba (final {ep_[-1]:.1f} %)")
    a2.set(title="(b) Exactitud por época", xlabel="Época", ylabel="Exactitud (%)", ylim=(0, 105))
    a2.legend(loc="lower right")
    fig.tight_layout()
    guardar(fig, "fig08_exp3_vocales_entrenamiento.png")


def fig09_confusion():
    d = leer("exp3_confusion.csv")
    clases = [k for k in d[0].keys() if k != "real"]
    m = np.array([[int(f[c]) for c in clases] for f in d])
    cmap = LinearSegmentedColormap.from_list("cf", ["#FFFFFF", CELESTE_GRIS, "#5B7299", MARINO])
    fig, ax = plt.subplots(figsize=(4.4, 3.8))
    im = ax.imshow(m, cmap=cmap)
    for i in range(len(clases)):
        for j in range(len(clases)):
            ax.text(j, i, m[i, j], ha="center", va="center", fontsize=11,
                    color="white" if m[i, j] > m.max() / 2 else MARINO, fontweight="bold" if i == j else None)
    ax.set_xticks(range(len(clases)), clases)
    ax.set_yticks(range(len(clases)), [f["real"] for f in d])
    ax.set(xlabel="Clase predicha", ylabel="Clase real")
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    total = m.sum()
    ax.set_title(f"Exactitud = {np.trace(m)}/{total} = {np.trace(m) / total * 100:.1f} %", fontsize=10)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04).set_label("Muestras")
    fig.tight_layout()
    guardar(fig, "fig09_exp3_matriz_confusion.png")


def fig10_bench():
    d = leer("benchmarks.csv")
    exps = []
    for f in d:
        if f["experimento"] not in exps:
            exps.append(f["experimento"])
    colores = [ROJO, MARINO, VERDE]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.2), gridspec_kw={"width_ratios": [1.5, 1]})
    inf = []
    for e, c in zip(exps, colores):
        f = [x for x in d if x["experimento"] == e]
        arq = f[0]["arquitectura"]
        a1.loglog(col(f, "epocas", int), col(f, "entrenamiento_ms_media"), "o-", color=c, lw=1.6, ms=4,
                  label=f"{e} ({arq})")
        inf.append((f"{e}\n({arq})", np.mean(col(f, "inferencia_ns_promedio")), c))
    a1.set(title="(a) Tiempo de entrenamiento", xlabel="Épocas (escala log)", ylabel="Tiempo medio (ms, escala log)")
    a1.legend(loc="upper left")
    barras = a2.bar([i[0] for i in inf], [i[1] for i in inf], color=[i[2] for i in inf], width=0.6)
    for b, i in zip(barras, inf):
        a2.text(b.get_x() + b.get_width() / 2, b.get_height(), f"{i[1]:.0f} ns", ha="center", va="bottom", fontsize=8)
    a2.set(title="(b) Inferencia promedio", ylabel="Tiempo por predicción (ns)", ylim=(0, max(i[1] for i in inf) * 1.18))
    a2.grid(axis="x", visible=False)
    kib = float(d[0]["tamano_binario_kib"])
    fig.text(0.5, -0.02, f"Perfil {d[0]['perfil']} · {d[0]['so']} {d[0]['cpu_arch']} · "
             f"tamaño del binario: {kib:.1f} KiB · {d[0]['repeticiones']} repeticiones por medición",
             ha="center", fontsize=8, color=GRIS)
    fig.tight_layout()
    guardar(fig, "fig10_benchmarks_rust.png")


def fig11_escritorio():
    d = leer("prueba_escritorio.csv")
    y2 = [f for f in d if f["escenario"].startswith("y=2x")]
    xo = [f for f in d if f["escenario"].startswith("XOR") and f["capa"] == "2"]
    it = col(y2, "iteracion", int)
    fig, axs = plt.subplots(2, 2, figsize=(7.2, 5.2))
    a = axs[0, 0]
    a.plot(it, col(y2, "z"), "o-", color=AZUL, lw=1.6, ms=4, label="$z = wx + b$ (= $a$, activación lineal)")
    a.plot(it, col(y2, "objetivo_y"), "s--", color=NARANJA, lw=1.2, ms=4, label="Objetivo $y$")
    a.set(title="(a) y = 2x: salida vs. objetivo", xlabel="Iteración", ylabel="Valor", ylim=(0, 13.5))
    a.legend(fontsize=7.5, loc="upper left")
    a = axs[0, 1]
    a.bar(it, col(y2, "error"), color=ROJO, width=0.6)
    a.axhline(0, color=GRIS, lw=0.8)
    a.set(title="(b) y = 2x: error $a - y$", xlabel="Iteración", ylabel="Error")
    a = axs[1, 0]
    w0, w1 = col(y2, "pesos_anteriores"), col(y2, "pesos_nuevos")
    b1 = col(y2, "sesgo_nuevo")
    a.plot(np.r_[0, it], np.r_[w0[0], w1], "o-", color=AZUL, lw=1.6, ms=4, label="Peso $w$")
    a.plot(np.r_[0, it], np.r_[float(y2[0]["sesgo_anterior"]), b1], "o-", color=NARANJA, lw=1.6, ms=4, label="Sesgo $b$")
    a.set(title=f"(c) y = 2x: actualización (α = {y2[0]['alpha']})", xlabel="Iteración", ylabel="Valor tras la iteración")
    a.legend(fontsize=8, loc="center right")
    a = axs[1, 1]
    itx = col(xo, "iteracion", int)
    etiquetas = [f"{f['entrada_x'].replace(';', ',')}" for f in xo]
    a.plot(itx, col(xo, "a"), "o-", color=PURPURA, lw=1.6, ms=4, label="Activación de salida $a$")
    a.plot(itx, col(xo, "objetivo_y"), "s--", color=NARANJA, lw=1.2, ms=4, label="Objetivo $y$")
    a.bar(itx, col(xo, "error"), color=ROJO, alpha=0.35, width=0.5, label="Error $a - y$")
    a.axhline(0, color=GRIS, lw=0.8)
    a.set_xticks(itx, [f"{i}\n({e})" for i, e in zip(itx, etiquetas)], fontsize=7)
    a.set(title="(d) XOR 2-2-1: capa de salida", xlabel="Iteración (entrada $x_1,x_2$)", ylabel="Valor", ylim=(-0.75, 1.7))
    a.legend(fontsize=7, loc="upper left", ncol=2)
    fig.tight_layout()
    guardar(fig, "fig11_prueba_escritorio.png")


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    print(f"Generando figuras en {FIG.relative_to(RAIZ)}/ ({DPI} DPI):")
    for f in (fig01_activaciones, fig02_y2x, fig03_mse_y2x, fig04_xor, fig05_xor_lr, fig06_xor_frontera,
              fig07_dataset, fig08_vocales, fig09_confusion, fig10_bench, fig11_escritorio):
        f()


if __name__ == "__main__":
    main()
