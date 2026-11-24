#!/usr/bin/env python3
"""Genera los diagramas editables `diagramas/*.drawio` y los exporta a PNG 300 DPI.

Los `.drawio` son XML estándar de diagrams.net: pueden abrirse y editarse en
https://app.diagrams.net o en draw.io Desktop. La exportación usa la CLI de
draw.io Desktop (`drawio -x`); si no está instalada, solo se escriben los XML.

Uso: python3 diagramas/generar_diagramas.py
"""
import shutil
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape

RAIZ = Path(__file__).resolve().parent.parent
DIR = RAIZ / "diagramas"
FIG = RAIZ / "tesis" / "figuras"
ESCALA = 300 / 96  # draw.io rasteriza a 96 px/pulgada

MARINO = "#0F1736"
AZUL = "#1D4ED8"
CIAN = "#0891B2"
PURPURA = "#7B2FF7"
NARANJA = "#F97316"
ROJO = "#B91C1C"
VERDE = "#047857"
GRIS = "#475569"
FUENTE = "fontFamily=Helvetica;fontSize=13;fontColor=#0F172A;"


class Diagrama:
    def __init__(self, nombre):
        self.nombre = nombre
        self.celdas = []
        self.n = 2

    def _id(self):
        self.n += 1
        return f"c{self.n}"

    def caja(self, texto, x, y, w, h, estilo="", borde=MARINO, relleno="#FFFFFF"):
        i = self._id()
        base = (f"rounded=1;arcSize=8;whiteSpace=wrap;html=1;{FUENTE}strokeColor={borde};"
                f"fillColor={relleno};strokeWidth=1.5;spacing=6;")
        self.celdas.append(
            f'<mxCell id="{i}" value="{escape(texto, {chr(34): "&quot;"})}" style="{base}{estilo}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return i

    def texto(self, texto, x, y, w, h, estilo=""):
        return self.caja(texto, x, y, w, h, "strokeColor=none;fillColor=none;" + estilo)

    def flecha(self, a, b, etiqueta="", estilo="", puntos=()):
        i = self._id()
        base = (f"edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;{FUENTE}fontSize=12;"
                f"strokeColor={GRIS};strokeWidth=1.6;endArrow=block;endFill=1;labelBackgroundColor=#FFFFFF;")
        pts = ""
        if puntos:
            pts = '<Array as="points">' + "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in puntos) + "</Array>"
        self.celdas.append(
            f'<mxCell id="{i}" value="{escape(etiqueta)}" style="{base}{estilo}" edge="1" parent="1" source="{a}" target="{b}">'
            f'<mxGeometry relative="1" as="geometry">{pts}</mxGeometry></mxCell>')
        return i

    def xml(self):
        return ('<mxfile host="app.diagrams.net"><diagram name="' + escape(self.nombre) + '">'
                '<mxGraphModel grid="1" gridSize="10" guides="1" page="0" background="#FFFFFF"><root>'
                '<mxCell id="0"/><mxCell id="1" parent="0"/>' + "".join(self.celdas) +
                "</root></mxGraphModel></diagram></mxfile>\n")


def ent(x0, w, xc):
    """Fracción horizontal de `xc` dentro de una caja que empieza en `x0` con ancho `w`."""
    return round((xc - x0) / w, 4)


def uml(nombre, campos, metodos, estereotipo=""):
    cab = f"<i>«{estereotipo}»</i><br>" if estereotipo else ""
    s = f'<div style="text-align:center">{cab}<b>{nombre}</b></div><hr style="margin:3px 0">'
    s += "<br>".join(campos)
    if metodos:
        s += '<hr style="margin:3px 0">' + "<br>".join(metodos)
    return s


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# --------------------------------------------------------------------------
def d01_arbol():
    d = Diagrama("Árbol de problemas")
    X0, W = 170, 1120
    cols = [X0 + k * 290 for k in range(4)]
    cw = 250
    etiqueta = "fontStyle=1;fontSize=12;fontColor=#FFFFFF;rounded=1;"
    for y, h, t, c in [(20, 70, "EFECTO<br>FINAL", MARINO), (130, 110, "EFECTOS", PURPURA),
                       (300, 100, "PROBLEMA<br>CENTRAL", ROJO), (460, 130, "CAUSAS", CIAN)]:
        d.caja(t, 0, y, 140, h, etiqueta, borde=c, relleno=c)
    final = d.caja("<b>Profesionales que usan la IA como usuarios de herramientas, no como constructores "
                   "capaces de explicarla, adaptarla y optimizarla</b>", X0, 20, W, 70, borde=MARINO, relleno="#E2E8F0")
    efectos = [
        "Comprensión superficial de la propagación hacia adelante, la retropropagación y el descenso de gradiente",
        "Dificultad para depurar modelos, elegir hiperparámetros (α, épocas, capas) e interpretar la pérdida",
        "Dependencia de librerías externas, servicios en la nube y hardware costoso para experimentar",
        "Escasa producción de investigación y software propio de IA en el entorno local",
    ]
    causas = [
        "Los frameworks de alto nivel (TensorFlow, PyTorch) ocultan el álgebra lineal y el cálculo detrás de llamadas de una línea",
        "La enseñanza se centra en el uso de herramientas y no en la derivación matemática ni en su implementación",
        "Pocos materiales didácticos abiertos, en español, que construyan una red neuronal paso a paso desde cero",
        "Poca exposición temprana a lenguajes de sistemas seguros y eficientes como Rust (ownership, tipos, rendimiento)",
    ]
    problema = d.caja("<b>La formación inicial en redes neuronales se apoya en frameworks de «caja negra»: "
                      "los estudiantes entrenan modelos sin comprender sus fundamentos matemáticos ni computacionales</b>",
                      X0, 300, W, 100, "fontSize=14;", borde=ROJO, relleno="#FEE2E2")
    for k, (e, c) in enumerate(zip(efectos, causas)):
        xc = cols[k] + cw / 2
        ie = d.caja(e, cols[k], 130, cw, 110, borde=PURPURA, relleno="#F3E8FF")
        ic = d.caja(c, cols[k], 460, cw, 130, borde=CIAN, relleno="#E0F2FE")
        d.flecha(ic, problema, estilo=f"exitX=0.5;exitY=0;entryX={ent(X0, W, xc)};entryY=1;")
        d.flecha(problema, ie, estilo=f"exitX={ent(X0, W, xc)};exitY=0;entryX=0.5;entryY=1;")
        d.flecha(ie, final, estilo=f"exitX=0.5;exitY=0;entryX={ent(X0, W, xc)};entryY=1;")
    return d


# --------------------------------------------------------------------------
def d02_arquitectura():
    d = Diagrama("Arquitectura de módulos Rust")
    paquete = "align=left;verticalAlign=top;spacingLeft=12;spacingTop=4;fontStyle=1;fontSize=14;dashed=0;"
    clase = "align=left;verticalAlign=top;spacingLeft=8;spacingTop=4;fontSize=11;arcSize=3;"
    W = 1420
    pk_exp = d.caja("experiments  (src/experiments/)", 0, 170, W, 210, paquete, borde=NARANJA, relleno="#FFF7ED")
    pk_nn = d.caja("nn  (src/nn/)", 0, 440, W, 350, paquete, borde=PURPURA, relleno="#FAF5FF")
    pk_math = d.caja("math  (src/math/)", 0, 850, W, 250, paquete, borde=CIAN, relleno="#ECFEFF")
    main = d.caja(uml("main.rs — CLI", ["flags: --all · --exp1 · --exp2 · --exp3 · --escritorio · --bench",
                                        "--export &lt;DIR&gt; · --seed &lt;N&gt; (por defecto 42)"],
                      ["+ parsear(args) → Opciones", "+ ejecutar(&amp;Opciones) → resultados/*.csv"]),
                  470, 0, 480, 120, clase, borde=MARINO, relleno="#F1F5F9")
    exps = [
        ("exp1_y2x", ["Regresión y = 2x", "red 1-1 · Linear · α = 0.01"], ["→ exp1_y2x.csv"]),
        ("exp2_xor", ["Perceptrón 2-1 vs. 2-4-1", "α ∈ {0.01, 0.5, 50}"], ["→ exp2_xor.csv", "→ exp2_xor_lr.csv", "→ exp2_xor_frontera.csv"]),
        ("exp3_vocales", ["Vocales A-E-I-O-U 5×5", "red 25-10-5 · Sigmoid"], ["→ exp3_vocales.csv", "→ exp3_confusion.csv", "→ dataset_vocales.csv"]),
        ("prueba_escritorio", ["Traza paso a paso", "y = 2x y XOR 2-2-1"], ["→ prueba_escritorio.csv"]),
        ("benchmarks", ["std::time::Instant", "perfil --release"], ["→ benchmarks.csv"]),
        ("csv::CsvWriter", ["- writer: BufWriter&lt;File&gt;"], ["+ create(ruta, encabezados)", "+ write_row(campos)", "+ finish()"]),
    ]
    for k, (n, c, m) in enumerate(exps):
        d.caja(uml(n, c, m), 20 + k * 233, 205, 215, 160, clase, borde=NARANJA)
    network = d.caja(uml("Network", ["- layers: Vec&lt;Layer&gt;", "- loss: Mse"],
                         ["+ new(topología, activaciones, semilla)", "+ forward(&amp;mut self, x) → ŷ",
                          "+ backward(&amp;mut self, y) → pérdida", "+ update(&amp;mut self, α)",
                          "+ train_step(&amp;mut self, x, y, α)", "+ train(&amp;mut self, X, Y, E, α)",
                          "+ predict(&amp;self, x) → ŷ", "+ evaluate_mse(&amp;self, X, Y)"]),
                     20, 480, 290, 260, clase, borde=PURPURA)
    layer = d.caja(uml("Layer", ["- weights: Matrix  (n_out × n_in)", "- biases: Vector  (n_out)",
                                 "- activation: Activation", "- input, z, output, delta: Vector",
                                 "- grad_weights: Matrix", "- grad_biases: Vector"],
                       ["+ new(n_in, n_out, act, &amp;mut Rng)", "+ forward(&amp;mut self, x) → a",
                        "+ backward(&amp;mut self, ∂L/∂a) → ∂L/∂x", "+ apply_gradients(&amp;mut self, α)",
                        "+ neuron(i) → Neuron"]),
                   370, 480, 300, 280, clase, borde=PURPURA)
    neuron = d.caja(uml("Neuron", ["+ weights: Vector", "+ bias: f64", "+ activation: Activation"],
                        ["+ weighted_sum(x) → z", "+ forward(x) → a"]),
                    730, 480, 220, 150, clase, borde=PURPURA)
    activation = d.caja(uml("Activation", ["Sigmoid · ReLU · Linear"], ["(Copy, sin asignación dinámica)"], "enum"),
                        730, 660, 220, 100, clase, borde=PURPURA)
    act_fn = d.caja(uml("ActivationFn", [], ["+ activate(z) → f(z)", "+ derivative(z) → f'(z)", "+ name()"], "trait"),
                    1000, 480, 190, 120, clase, borde=PURPURA, relleno="#EDE9FE")
    structs = d.caja(uml("Sigmoid · ReLU · Linear", ["σ(z) · max(0, z) · z"], [], "struct"),
                     1000, 660, 190, 100, clase, borde=PURPURA)
    loss_fn = d.caja(uml("LossFn", [], ["+ loss(ŷ, y)", "+ derivative(ŷ, y)"], "trait"),
                     1230, 480, 170, 120, clase, borde=PURPURA, relleno="#EDE9FE")
    mse = d.caja(uml("Mse", ["(1/n)·Σ(ŷᵢ − yᵢ)²", "∂/∂ŷ = (2/n)(ŷ − y)"], [], "struct"),
                 1230, 660, 170, 100, clase, borde=PURPURA)
    vector = d.caja(uml("Vector", ["- data: Vec&lt;f64&gt;"],
                        ["+ dot, add, sub, hadamard, scale", "+ get(i) → Result&lt;f64&gt;", "+ argmax()"]),
                    20, 890, 290, 190, clase, borde=CIAN)
    matrix = d.caja(uml("Matrix", ["- rows, cols: usize", "- data: Vec&lt;f64&gt;  (orden por filas)"],
                        ["+ new(rows, cols, data) → Result", "+ get(i, j) / set(i, j, v) → Result",
                         "+ matmul, mul_vector, transpose", "+ add, sub, hadamard, scale, outer"]),
                    370, 890, 300, 190, clase, borde=CIAN)
    rng = d.caja(uml("Rng", ["- state: u64  (SplitMix64)"], ["+ new(semilla)", "+ next_f64() · uniform(a, b)", "+ shuffle(&amp;mut [T])"]),
                 730, 890, 220, 190, clase, borde=CIAN)
    error = d.caja(uml("MathError", ["DimensionMismatch", "IndexOutOfBounds", "InvalidShape", "InvalidArgument"],
                       ["MathResult&lt;T&gt; = Result&lt;T, MathError&gt;"], "enum"),
                   1000, 890, 400, 190, clase, borde=CIAN)
    dep = "dashed=1;endArrow=open;endFill=0;strokeColor=#334155;"
    d.flecha(main, pk_exp, "«usa»", dep + "exitX=0.5;exitY=1;entryX=0.5;entryY=0;")
    d.flecha(pk_exp, pk_nn, "«usa»", dep + "exitX=0.97;exitY=1;entryX=0.97;entryY=0;")
    d.flecha(pk_nn, pk_math, "«usa»", dep + "exitX=0.97;exitY=1;entryX=0.97;entryY=0;")
    comp = "endArrow=none;startArrow=diamondThin;startFill=1;startSize=14;strokeColor=#334155;"
    d.flecha(network, layer, "1..*", comp + "exitX=1;exitY=0.25;entryX=0;entryY=0.23;")
    d.flecha(layer, matrix, "pesos y gradientes", comp + "exitX=0.5;exitY=1;entryX=0.5;entryY=0;")
    d.flecha(layer, neuron, "fila i ≡ Neuron", dep + "exitX=1;exitY=0.2;entryX=0;entryY=0.37;")
    d.flecha(layer, activation, "", "endArrow=open;strokeColor=#334155;exitX=1;exitY=0.85;entryX=0;entryY=0.5;")
    real = "dashed=1;endArrow=block;endFill=0;endSize=12;strokeColor=#334155;"
    d.flecha(activation, act_fn, "", real + "exitX=1;exitY=0.3;entryX=0;entryY=0.75;")
    d.flecha(structs, act_fn, "", real + "exitX=0.5;exitY=0;entryX=0.5;entryY=1;")
    d.flecha(mse, loss_fn, "", real + "exitX=0.5;exitY=0;entryX=0.5;entryY=1;")
    d.texto("◆ composición   - - -▷ implementa trait   - - -&gt; dependencia «usa»", 470, 1110, 480, 26,
            "fontSize=11;fontColor=#475569;")
    return d


# --------------------------------------------------------------------------
def d03_flujo():
    d = Diagrama("Flujo de entrenamiento")
    cx, w = 430, 460
    x = cx - w / 2
    inicio_fin = "ellipse;fontStyle=1;"
    paso = "align=center;"
    y = 0
    nodos = {}

    def nodo(clave, texto, h, estilo="", borde=MARINO, relleno="#FFFFFF", ancho=w):
        nonlocal y
        nodos[clave] = (d.caja(texto, cx - ancho / 2, y, ancho, h, estilo, borde, relleno), y, h)
        y += h + 38

    nodo("ini", "Inicio", 46, inicio_fin, relleno="#E2E8F0", ancho=180)
    nodo("init", "<b>Inicializar la red</b><br>Network::new(topología, activaciones, semilla = 42)<br>"
         "pesos Xavier/He con SplitMix64 · sesgos b = 0", 78)
    nodo("epoca", "<b>Para cada época</b> e = 1, …, E", 44, relleno="#F1F5F9")
    nodo("muestra", "<b>Para cada muestra</b> (x, y) del conjunto de entrenamiento", 44, relleno="#F1F5F9")
    y_grupo = y - 16
    nodo("fwd", "<b>1. forward</b>  (propagación hacia adelante)<br>a⁽⁰⁾ = x<br>"
         "z⁽ˡ⁾ = W⁽ˡ⁾·a⁽ˡ⁻¹⁾ + b⁽ˡ⁾,   a⁽ˡ⁾ = f(z⁽ˡ⁾),   l = 1, …, L<br>ŷ = a⁽ᴸ⁾", 98, borde=AZUL, relleno="#DBEAFE")
    nodo("loss", "<b>2. Pérdida</b><br>L = MSE(ŷ, y) = (1/n)·Σᵢ (ŷᵢ − yᵢ)²", 58, borde=NARANJA, relleno="#FFEDD5")
    nodo("bwd", "<b>3. backward</b>  (retropropagación)<br>δ⁽ᴸ⁾ = (2/n)(ŷ − y) ⊙ f′(z⁽ᴸ⁾)<br>"
         "δ⁽ˡ⁾ = (W⁽ˡ⁺¹⁾)ᵀ·δ⁽ˡ⁺¹⁾ ⊙ f′(z⁽ˡ⁾)<br>∇W⁽ˡ⁾ = δ⁽ˡ⁾·(a⁽ˡ⁻¹⁾)ᵀ,   ∇b⁽ˡ⁾ = δ⁽ˡ⁾", 112,
         borde=PURPURA, relleno="#EDE9FE")
    nodo("upd", "<b>4. update</b>  (descenso de gradiente)<br>W⁽ˡ⁾ ← W⁽ˡ⁾ − α·∇W⁽ˡ⁾,   b⁽ˡ⁾ ← b⁽ˡ⁾ − α·∇b⁽ˡ⁾",
         64, borde=VERDE, relleno="#D1FAE5")
    y_fin_grupo = y - 38 + 16
    nodo("q1", "¿Quedan<br>muestras?", 92, "rhombus;fontStyle=1;", relleno="#FEF9C3", ancho=200)
    nodo("log", "<b>Registrar la época</b>: MSE, exactitud, pesos → resultados/*.csv", 50, relleno="#F1F5F9")
    nodo("q2", "¿e &lt; E?", 92, "rhombus;fontStyle=1;", relleno="#FEF9C3", ancho=200)
    nodo("eval", "<b>Evaluación final</b> con predict(&amp;self, x): exactitud, matriz de confusión", 50)
    nodo("fin", "Fin", 46, inicio_fin, relleno="#E2E8F0", ancho=180)
    grupo = d.caja("", x - 30, y_grupo, w + 60, y_fin_grupo - y_grupo, "dashed=1;dashPattern=6 4;", borde=GRIS, relleno="none")
    d.celdas.insert(0, d.celdas.pop())  # el recuadro va al fondo
    d.texto("<b>train_step(&amp;mut self, x, y, α)</b><br>costo O(P) por muestra", x + w + 40, y_grupo, 240, 50,
            "align=left;fontSize=12;fontColor=#475569;")
    orden = ["ini", "init", "epoca", "muestra", "fwd", "loss", "bwd", "upd", "q1", "log", "q2", "eval", "fin"]
    for a, b in zip(orden, orden[1:]):
        etiqueta = "no" if a in ("q1", "q2") else ""
        d.flecha(nodos[a][0], nodos[b][0], etiqueta, "exitX=0.5;exitY=1;entryX=0.5;entryY=0;")

    def yc(k):
        return nodos[k][1] + nodos[k][2] / 2

    d.flecha(nodos["q1"][0], nodos["muestra"][0], "sí", "exitX=0;exitY=0.5;entryX=0;entryY=0.5;",
             puntos=[(x - 70, yc("q1")), (x - 70, yc("muestra"))])
    d.flecha(nodos["q2"][0], nodos["epoca"][0], "sí", "exitX=0;exitY=0.5;entryX=0;entryY=0.5;",
             puntos=[(x - 120, yc("q2")), (x - 120, yc("epoca"))])
    d.caja("<b>Notación</b><br>L: número de capas · l: índice de capa<br>α: tasa de aprendizaje<br>"
           "⊙: producto de Hadamard (elemento a elemento)<br>f′: derivada analítica de Sigmoid, ReLU o Linear<br><br>"
           "<b>Costo</b> (P = número de pesos)<br>forward, backward, predict: O(P)<br>entrenamiento: O(E·N·P)",
           x + w + 40, nodos["bwd"][1] - 10, 300, 190, "align=left;verticalAlign=top;fontSize=12;", borde=GRIS, relleno="#F8FAFC")
    return d


# --------------------------------------------------------------------------
def d04_memoria():
    d = Diagrama("Memoria y ownership en Rust")
    zona = "align=left;verticalAlign=top;spacingLeft=12;spacingTop=6;fontStyle=1;fontSize=14;"
    fila = "align=left;spacingLeft=8;fontSize=12;rounded=0;"
    d.caja("STACK  (marco de ejecutar(): tamaño fijo)", 0, 0, 430, 470, zona,
           borde=AZUL, relleno="#EFF6FF")
    d.caja("HEAP  (buffers de Vec&lt;T&gt;: tamaño dinámico, liberados por Drop)", 500, 0, 820, 470, zona,
           borde=PURPURA, relleno="#FAF5FF")
    d.texto("<b>red: Network</b>  (XOR 2-4-1, propietaria de sus capas)", 20, 50, 390, 26, "align=left;")
    red_layers = d.caja("layers: Vec&lt;Layer&gt;  { ptr ●, len = 2, cap = 2 }", 20, 78, 390, 34, fila, borde=AZUL)
    d.caja("loss: Mse  (struct de tamaño 0)", 20, 112, 390, 34, fila, borde=AZUL)
    d.texto("<b>x: Vector</b>  (entrada de una muestra)", 20, 175, 390, 26, "align=left;")
    x_data = d.caja("data: Vec&lt;f64&gt;  { ptr ●, len = 2, cap = 2 }", 20, 203, 390, 34, fila, borde=AZUL)
    d.texto("<b>alpha: f64 = 0.5</b>  (Copy: vive completo en el stack)", 20, 265, 390, 26, "align=left;")
    d.caja("Un Vec&lt;T&gt; ocupa 24 B en el stack (puntero, longitud y capacidad); "
           "sus elementos viven contiguos en el heap.", 20, 320, 390, 70, "fontSize=12;align=left;", borde=GRIS, relleno="#FFFFFF")
    d.texto("<b>Buffer de Vec&lt;Layer&gt;</b>  (2 capas contiguas)", 520, 40, 500, 26, "align=left;")
    l0 = d.caja("<b>Layer 0</b>  (2 → 4, Sigmoid)", 520, 68, 380, 30, fila + "fillColor=#EDE9FE;", borde=PURPURA)
    l0w = d.caja("weights: Matrix { rows = 4, cols = 2, data: ptr ● }", 520, 98, 380, 30, fila, borde=PURPURA)
    d.caja("biases, input, z, output, delta: Vector · grad_weights: Matrix", 520, 128, 380, 30, fila + "fontSize=11;", borde=PURPURA)
    d.caja("<b>Layer 1</b>  (4 → 1, Sigmoid)", 520, 158, 380, 30, fila + "fillColor=#EDE9FE;", borde=PURPURA)
    d.caja("weights: Matrix { rows = 1, cols = 4, data: ptr ● } · …", 520, 188, 380, 30, fila + "fontSize=11;", borde=PURPURA)
    d.texto("<b>Datos de weights de Layer 0</b> (W⁽¹⁾): 4 × 2 = 8 valores f64 en orden por filas (64 B contiguos)", 520, 255, 780, 26, "align=left;")
    celdas = []
    for k in range(8):
        i, j = divmod(k, 2)
        relleno = "#E0F2FE" if i % 2 == 0 else "#CFFAFE"
        celdas.append(d.caja(f"w<sub>{i}{j}</sub><br><font style=\"font-size:10px\">[{k}]</font>", 520 + k * 72, 285, 72, 54,
                             "rounded=0;", borde=CIAN, relleno=relleno))
    d.texto("idx(i, j) = i·cols + j   →   W[i][j] = data[i·2 + j]   ·   recorrido secuencial amigable con la caché",
            520, 345, 780, 26, "align=left;fontSize=12;fontColor=#475569;")
    d.texto("<b>Datos de x</b>", 1120, 40, 180, 26, "align=left;")
    xb = [d.caja(f"x<sub>{k + 1}</sub>", 1120 + k * 80, 68, 80, 44, "rounded=0;", borde=CIAN, relleno="#E0F2FE") for k in range(2)]
    puntero = "strokeColor=#B91C1C;endArrow=classic;endFill=1;strokeWidth=1.6;"
    d.flecha(red_layers, l0, "", puntero + "exitX=1;exitY=0.5;entryX=0;entryY=0.5;")
    d.flecha(x_data, xb[0], "", puntero + "exitX=1;exitY=0.5;entryX=0.5;entryY=1;",
             puntos=[(460, 220), (460, 420), (1160, 420)])
    d.flecha(l0w, celdas[0], "", puntero + "exitX=1;exitY=0.5;entryX=0.5;entryY=0;", puntos=[(940, 113), (940, 240), (556, 240)])
    reglas = [
        ("Ownership", "Network posee su Vec&lt;Layer&gt;; cada Layer posee sus Matrix y Vector. "
         "Cuando red sale de ámbito, Drop libera todo el heap en cascada: sin recolector de basura y sin fugas.", AZUL, "#DBEAFE"),
        ("Préstamo inmutable  &amp;T", "predict(&amp;self, x: &amp;Vector) y evaluate_mse(&amp;self, …) solo leen: "
         "admiten varios lectores a la vez y no copian los datos.", VERDE, "#D1FAE5"),
        ("Préstamo mutable  &amp;mut T", "forward, backward, update y train_step(&amp;mut self, …) modifican pesos y cachés: "
         "un único escritor; el compilador impide alias con mutación.", PURPURA, "#EDE9FE"),
        ("Result&lt;T, MathError&gt;", "get(i, j), matmul o add validan índices y dimensiones y devuelven Err "
         "en lugar de acceder fuera de rango o entrar en pánico.", NARANJA, "#FFEDD5"),
    ]
    for k, (t, cuerpo, b, r) in enumerate(reglas):
        d.caja(f"<b>{t}</b><br>{cuerpo}", k * 335, 500, 315, 120, "align=left;verticalAlign=top;fontSize=12;", borde=b, relleno=r)
    d.texto("● puntero (ptr) del Vec hacia su buffer en el heap", 0, 630, 420, 24, "align=left;fontSize=11;fontColor=#B91C1C;")
    return d


# --------------------------------------------------------------------------
def d05_fases():
    d = Diagrama("Fases de la metodología")
    fases = [
        ("Matemática", "Vector y Matrix: acceso seguro, suma, resta, producto punto, Hadamard, matmul y transpuesta",
         "Base de álgebra lineal probada", CIAN),
        ("Neurona", "Neuron con pesos, sesgo y forward: z = w·x + b, a = f(z)", "Una neurona calcula su salida", CIAN),
        ("Activaciones", "Sigmoid, ReLU y Linear con derivadas analíticas", "Activaciones verificadas", CIAN),
        ("Error", "MSE y su gradiente ∂L/∂ŷ", "Medida de la diferencia salida–objetivo", CIAN),
        ("Primer aprendizaje", "Gradientes y descenso de gradiente sobre y = 2x", "El error disminuye: w → 2", AZUL),
        ("Capas y red", "Layer y Network: forward, backward, predict y train; gradient checking", "Red multicapa operativa", AZUL),
        ("XOR", "Perceptrón 2-1 vs. red 2-4-1 y tres tasas de aprendizaje", "Aprendizaje no lineal demostrado", PURPURA),
        ("Vocales", "Matrices 5×5 de A, E, I, O, U con ruido; red 25-10-5", "Clasificación, exactitud y matriz de confusión", PURPURA),
        ("Documentación", "Documentación ///, prueba de escritorio, benchmarks, tesis APA 7 y kit de feria",
         "Proyecto educativo abierto", NARANJA),
    ]
    bloques = [("Fundamentos matemáticos", 0, 4, CIAN, "#ECFEFF"), ("Aprendizaje", 4, 6, AZUL, "#EFF6FF"),
               ("Experimentación", 6, 8, PURPURA, "#FAF5FF"), ("Difusión", 8, 9, NARANJA, "#FFF7ED")]
    W, H, G = 230, 190, 56
    pos = [(k * (W + G), 40) for k in range(4)] + [(k * (W + G), 330) for k in range(5)]
    for nombre, a, b, borde, relleno in bloques:
        xs = [pos[i][0] for i in range(a, b)]
        y = pos[a][1]
        d.caja(f"<b>{nombre}</b>", min(xs) - 12, y - 34, max(xs) + W - min(xs) + 24, H + 46,
               "verticalAlign=top;align=left;spacingLeft=10;spacingTop=2;fontSize=12;dashed=1;", borde=borde, relleno=relleno)
    ids = []
    for k, ((t, act, res, c), (x, y)) in enumerate(zip(fases, pos)):
        ids.append(d.caja(f'<div style="background:{c};color:#FFFFFF;padding:4px;border-radius:4px"><b>Fase {k + 1} · {t}</b></div>'
                          f'<div style="text-align:left;margin-top:6px">{act}</div>'
                          f'<div style="text-align:left;margin-top:6px;color:{c}"><b>Resultado:</b> {res}</div>',
                          x, y, W, H, "verticalAlign=top;fontSize=12;", borde=c))
    for k in range(8):
        if k == 3:
            continue
        d.flecha(ids[k], ids[k + 1], "", "exitX=1;exitY=0.5;entryX=0;entryY=0.5;")
    d.flecha(ids[3], ids[4], "", "exitX=0.5;exitY=1;entryX=0.5;entryY=0;",
             puntos=[(pos[3][0] + W / 2, 266), (pos[4][0] + W / 2, 266)])
    d.texto("Cada flecha es una compuerta de calidad: la fase siguiente solo inicia con <b>cargo test</b> al 100 % en verde.",
            0, 560, 1200, 26, "align=left;fontSize=12;fontColor=#475569;")
    ciclo = ["Diseñar<br>(ecuaciones y dimensiones)", "Implementar<br>(Rust std, sin crates de ML)",
             "Probar<br>(cargo test + gradient checking)", "Documentar<br>(/// con fórmulas y Big-O)",
             "Exportar evidencia<br>(resultados/*.csv)"]
    d.texto("<b>Ciclo aplicado dentro de cada fase</b>", 0, 600, 400, 26, "align=left;")
    prev = None
    for k, t in enumerate(ciclo):
        i = d.caja(t, k * 280, 632, 230, 58, "fontSize=12;arcSize=40;", borde=GRIS, relleno="#F1F5F9")
        if prev:
            d.flecha(prev, i, "", "exitX=1;exitY=0.5;entryX=0;entryY=0.5;")
        prev = i
    return d


DIAGRAMAS = [
    ("01_arbol_problemas", "diag01_arbol_problemas", d01_arbol),
    ("02_arquitectura_modulos_rust", "diag02_arquitectura_rust", d02_arquitectura),
    ("03_flujo_forward_backprop", "diag03_flujo_entrenamiento", d03_flujo),
    ("04_memoria_ownership_rust", "diag04_memoria_rust", d04_memoria),
    ("05_fases_metodologia", "diag05_fases_metodologia", d05_fases),
]


def exportar(fuente, destino):
    drawio = shutil.which("drawio") or shutil.which("draw.io")
    if not drawio:
        print(f"  (sin draw.io CLI: no se exporta {destino.name})")
        return
    subprocess.run([drawio, "--no-sandbox", "-x", "-f", "png", "-s", f"{ESCALA:.4f}", "-b", "24",
                    "-o", str(destino), str(fuente)], check=True, capture_output=True)
    try:
        from PIL import Image
        with Image.open(destino) as im:
            im.load()
            im.save(destino, dpi=(300, 300))
    except ImportError:
        pass


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    for archivo, png, fn in DIAGRAMAS:
        ruta = DIR / f"{archivo}.drawio"
        ruta.write_text(fn().xml(), encoding="utf-8")
        exportar(ruta, FIG / f"{png}.png")
        print(f"  {ruta.relative_to(RAIZ)} → tesis/figuras/{png}.png")


if __name__ == "__main__":
    main()
