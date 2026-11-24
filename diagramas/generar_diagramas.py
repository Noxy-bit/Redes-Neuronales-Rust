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

# Paleta sobria institucional: azul marino, gris pizarra, rojo técnico y verde bosque.
MARINO = "#0F2A5F"
AZUL = "#1E3A8A"
CIAN = "#334155"
PURPURA = "#0F2A5F"
NARANJA = "#374151"
ROJO = "#B91C1C"
VERDE = "#15803D"
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
        ie = d.caja(e, cols[k], 130, cw, 110, borde=PURPURA, relleno="#EEF2F7")
        ic = d.caja(c, cols[k], 460, cw, 130, borde=CIAN, relleno="#F1F5F9")
        d.flecha(ic, problema, estilo=f"exitX=0.5;exitY=0;entryX={ent(X0, W, xc)};entryY=1;")
        d.flecha(problema, ie, estilo=f"exitX={ent(X0, W, xc)};exitY=0;entryX=0.5;entryY=1;")
        d.flecha(ie, final, estilo=f"exitX=0.5;exitY=0;entryX={ent(X0, W, xc)};entryY=1;")
    return d


# --------------------------------------------------------------------------
def d02_arquitectura():
    d = Diagrama("Arquitectura del repositorio oficial lanorrron/neural-network")
    paquete = "align=left;verticalAlign=top;spacingLeft=12;spacingTop=4;fontStyle=1;fontSize=14;dashed=0;"
    clase = "align=left;verticalAlign=top;spacingLeft=8;spacingTop=4;fontSize=11;arcSize=3;"
    W = 1420
    main = d.caja(uml("main.rs — CLI", ["cargo run [-- lineal | booleano | vocal &lt;letra&gt;]",
                                        "sin argumento: experimento de vocales"],
                      ["+ main(): match args.first() → experiments::*::run()"]),
                  420, 0, 500, 110, clase, borde=MARINO, relleno="#F1F5F9")
    comp = d.caja(uml("Motor de validación complementario", ["Noxy-bit/Redes-Neuronales-Rust (f64, std)"],
                      ["XOR 2-4-1 con retropropagación multicapa", "52 pruebas · gradient checking · benchmarks"]),
                  1000, 0, 420, 110, clase + "dashed=1;", borde=GRIS, relleno="#FFFFFF")
    pk_exp = d.caja("experiments  (src/experiments/)", 0, 160, W, 200, paquete, borde=NARANJA, relleno="#F8FAFC")
    pk_neu = d.caja("neural  (src/neural/)", 0, 420, 900, 290, paquete, borde=PURPURA, relleno="#F8FAFC")
    pk_lea = d.caja("learning  (src/learning/)", 940, 420, 480, 290, paquete, borde=PURPURA, relleno="#F8FAFC")
    pk_math = d.caja("math  (src/math/)", 0, 770, W, 200, paquete, borde=CIAN, relleno="#F8FAFC")
    exps = [
        ("linear.rs · run()", ["Aprender y = 2x · 1 neurona lineal", "6 muestras · α = 0.02 · meta MSE ≤ 10⁻¹²"],
         ["gradiente de lote completo (MSE)", "informe cada 20 épocas"]),
        ("true_false.rs · run()", ["0 → falso · 1 → verdadero", "Sigmoid · umbral 0.5 · α = 0.5 · 250 épocas"],
         ["gradiente (p − y) / N", "traza ∇w, ∇b, Δw, Δb por época"]),
        ("vowels.rs · run(Option&lt;&amp;str&gt;)", ["Vocales A·E·I·O·U en 5×5 → 25 entradas",
                                                   "Layer 25 → 5 · softmax · α = 0.3 · 500 épocas"],
         ["encode · softmax · argmax · parse_vowel", "gradiente (p − y) / N por salida"]),
    ]
    for k, (n, c, m) in enumerate(exps):
        d.caja(uml(n, c, m), 20 + k * 467, 195, 445, 145, clase, borde=NARANJA)
    network = d.caja(uml("Network", ["- layers: Vec&lt;Layer&gt;"], ["+ new(layers)", "+ forward(&amp;self, x) → Vector"]),
                     20, 460, 260, 120, clase, borde=PURPURA)
    layer = d.caja(uml("Layer", ["- neurons: Vec&lt;Neuron&gt;"],
                       ["+ new(neurons)", "+ forward(&amp;self, x) → Vector", "+ neurons_mut() → &amp;mut [Neuron]"]),
                   320, 460, 270, 130, clase, borde=PURPURA)
    neuron = d.caja(uml("Neuron", ["- weights: Vector&lt;f32&gt;", "- bias: f32"],
                        ["+ forward(x) = x · w + b", "+ weights(_mut), bias(_mut)"]),
                    630, 460, 250, 130, clase, borde=PURPURA)
    act = d.caja(uml("Activacion", ["relu(v) = max(0, v)", "sigmoid(v) = 1 / (1 + e⁻ᵛ)"], []),
                 630, 600, 250, 76, clase, borde=PURPURA, relleno="#E8EDF5")
    mse = d.caja(uml("MSE", ["calculate(ŷ, y) = (1/n)·Σ(ŷ − y)²"], ["derivate(ŷ, y) = 2(ŷ − y)/n"]),
                 960, 460, 440, 76, clase, borde=PURPURA)
    grad = d.caja(uml("Gradient", ["weights(δ, x) = δ·xᵢ  ·  bias(δ) = δ"], []),
                  960, 548, 440, 56, clase, borde=PURPURA)
    gd = d.caja(uml("GradientDescent", ["- learning_rate: f32"], ["update_weights(w, ∇) · update_bias(b, ∇)  →  θ ← θ − α∇"]),
                960, 614, 440, 84, clase, borde=PURPURA)
    vector = d.caja(uml("Vector&lt;T&gt;", ["- data: Vec&lt;T&gt;"],
                        ["+ new, zeros, len, get, set, as_slice(_mut)", "+ add, sub, multiply_scalar, dot, map",
                         "+ random(n)  (rand 0.9)"]),
                    20, 810, 560, 140, clase, borde=CIAN)
    matrix = d.caja(uml("Matrix&lt;T&gt;", ["- rows, columns: usize · data: Vec&lt;T&gt;"],
                        ["+ new, get, set, transpose, print, zeros, random", "+ add, sub, multiply_scalar, multiply",
                         "+ add_bias, map, multiply_elementwise",
                         "<i>definida; los experimentos actuales no la utilizan</i>"]),
                    620, 810, 780, 140, clase, borde=CIAN)
    dep = "dashed=1;endArrow=open;endFill=0;strokeColor=#334155;"
    d.flecha(main, pk_exp, "«usa»", dep + "exitX=0.5;exitY=1;entryX=0.475;entryY=0;")
    d.flecha(pk_exp, pk_neu, "«usa»", dep + "exitX=0.3;exitY=1;entryX=0.47;entryY=0;")
    d.flecha(pk_exp, pk_lea, "«usa»", dep + "exitX=0.83;exitY=1;entryX=0.5;entryY=0;")
    d.flecha(pk_neu, pk_math, "«usa»", dep + "exitX=0.5;exitY=1;entryX=0.317;entryY=0;")
    d.flecha(comp, main, "valida", "dashed=1;endArrow=open;strokeColor=#64748B;exitX=0;exitY=0.5;entryX=1;entryY=0.5;")
    rombo = "endArrow=none;startArrow=diamondThin;startFill=1;startSize=14;strokeColor=#334155;"
    d.flecha(network, layer, "1..*", rombo + "exitX=1;exitY=0.4;entryX=0;entryY=0.4;")
    d.flecha(layer, neuron, "1..*", rombo + "exitX=1;exitY=0.4;entryX=0;entryY=0.4;")
    d.texto("◆ composición   - - -&gt; dependencia «usa»   ·   aritmética f32   ·   única dependencia: rand 0.9",
            300, 980, 820, 26, "fontSize=11;fontColor=#475569;")
    return d


# --------------------------------------------------------------------------
def d03_flujo():
    d = Diagrama("Flujo de entrenamiento del repositorio oficial")
    cx, w = 430, 500
    x = cx - w / 2
    inicio_fin = "ellipse;fontStyle=1;"
    y = 0
    nodos = {}

    def nodo(clave, texto, h, estilo="", borde=MARINO, relleno="#FFFFFF", ancho=w):
        nonlocal y
        nodos[clave] = (d.caja(texto, cx - ancho / 2, y, ancho, h, estilo, borde, relleno), y, h)
        y += h + 36

    nodo("ini", "Inicio  ·  cargo run -- &lt;experimento&gt;", 46, inicio_fin, relleno="#E2E8F0", ancho=300)
    nodo("init", "<b>Inicializar</b><br>Neuron::new(Vector::zeros(n), 0.0)  ·  pesos y bias en cero<br>"
         "GradientDescent::new(α)", 70)
    nodo("epoca", "<b>Para cada época</b> e = 1, …, E  ·  acumuladores ∇w = 0, ∇b = 0", 44, relleno="#F1F5F9")
    nodo("muestra", "<b>Para cada muestra</b> (x, y) del conjunto fijo", 44, relleno="#F1F5F9")
    y_grupo = y - 16
    nodo("fwd", "<b>1. forward</b>  Neuron::forward / Layer::forward<br>z = x · w + b", 58, borde=AZUL, relleno="#E8EDF5")
    nodo("sal", "<b>2. Salida</b><br>lineal: ŷ = z   ·   booleano: p = σ(z)   ·   vocales: p = softmax(z)",
         58, borde=NARANJA, relleno="#F1F5F9")
    nodo("err", "<b>3. Error por muestra</b><br>lineal: δ = MSE′(ŷ, y) / N = 2(ŷ − y) / N<br>"
         "booleano y vocales: δ = (p − y) / N", 78, borde=PURPURA, relleno="#E8EDF5")
    nodo("acu", "<b>4. Acumular</b>  Gradient::weights / Gradient::bias<br>∇w += δ · x,   ∇b += δ", 58,
         borde=PURPURA, relleno="#E8EDF5")
    y_fin_grupo = y - 36 + 16
    nodo("q1", "¿Quedan<br>muestras?", 88, "rhombus;fontStyle=1;", relleno="#F1F5F9", ancho=200)
    nodo("upd", "<b>5. Actualizar una vez por época</b>  GradientDescent<br>w ← w − α·∇w,   b ← b − α·∇b", 60,
         borde=VERDE, relleno="#ECF5EF")
    nodo("log", "<b>Informar</b>: parámetros, MSE o probabilidades por época (stdout)", 46, relleno="#F1F5F9")
    nodo("q2", "¿e &lt; E y no<br>se alcanzó la meta?", 100, "rhombus;fontStyle=1;", relleno="#F1F5F9", ancho=230)
    nodo("eval", "<b>Resultado final</b>: predicciones, clase reconocida y confianza", 46)
    nodo("fin", "Fin", 46, inicio_fin, relleno="#E2E8F0", ancho=180)
    grupo = d.caja("", x - 30, y_grupo, w + 60, y_fin_grupo - y_grupo, "dashed=1;dashPattern=6 4;", borde=GRIS, relleno="none")
    d.celdas.insert(0, d.celdas.pop())
    d.texto("<b>Cuerpo del ciclo interno</b><br>escrito en cada experimento", x + w + 40, y_grupo, 240, 50,
            "align=left;fontSize=12;fontColor=#475569;")
    orden = ["ini", "init", "epoca", "muestra", "fwd", "sal", "err", "acu", "q1", "upd", "log", "q2", "eval", "fin"]
    for a, b in zip(orden, orden[1:]):
        etiqueta = "no" if a in ("q1", "q2") else ""
        d.flecha(nodos[a][0], nodos[b][0], etiqueta, "exitX=0.5;exitY=1;entryX=0.5;entryY=0;")

    def yc(k):
        return nodos[k][1] + nodos[k][2] / 2

    d.flecha(nodos["q1"][0], nodos["muestra"][0], "sí", "exitX=0;exitY=0.5;entryX=0;entryY=0.5;",
             puntos=[(x - 70, yc("q1")), (x - 70, yc("muestra"))])
    d.flecha(nodos["q2"][0], nodos["epoca"][0], "sí", "exitX=0;exitY=0.5;entryX=0;entryY=0.5;",
             puntos=[(x - 120, yc("q2")), (x - 120, yc("epoca"))])
    d.caja("<b>Notación</b><br>N: número de muestras · α: tasa de aprendizaje<br>σ: Sigmoid · softmax: e^zₖ / Σⱼ e^zⱼ<br>"
           "δ: gradiente de la pérdida respecto a z<br><br><b>Configuración real</b><br>lineal: N = 6, α = 0.02, E ≤ 10 000<br>"
           "booleano: N = 2, α = 0.5, E = 250<br>vocales: N = 5, α = 0.3, E = 500",
           x + w + 40, nodos["err"][1] - 10, 300, 210, "align=left;verticalAlign=top;fontSize=12;", borde=GRIS, relleno="#F8FAFC")
    return d


# --------------------------------------------------------------------------
def d04_memoria():
    d = Diagrama("Memoria y ownership en Rust")
    zona = "align=left;verticalAlign=top;spacingLeft=12;spacingTop=6;fontStyle=1;fontSize=14;"
    fila = "align=left;spacingLeft=8;fontSize=12;rounded=0;"
    d.caja("STACK  (marco de ejecutar(): tamaño fijo)", 0, 0, 430, 470, zona,
           borde=AZUL, relleno="#F8FAFC")
    d.caja("HEAP  (buffers de Vec&lt;T&gt;: tamaño dinámico, liberados por Drop)", 500, 0, 820, 470, zona,
           borde=PURPURA, relleno="#F8FAFC")
    d.texto("<b>red: Network</b>  (XOR 2-4-1, propietaria de sus capas)", 20, 50, 390, 26, "align=left;")
    red_layers = d.caja("layers: Vec&lt;Layer&gt;  { ptr ●, len = 2, cap = 2 }", 20, 78, 390, 34, fila, borde=AZUL)
    d.caja("loss: Mse  (struct de tamaño 0)", 20, 112, 390, 34, fila, borde=AZUL)
    d.texto("<b>x: Vector</b>  (entrada de una muestra)", 20, 175, 390, 26, "align=left;")
    x_data = d.caja("data: Vec&lt;f64&gt;  { ptr ●, len = 2, cap = 2 }", 20, 203, 390, 34, fila, borde=AZUL)
    d.texto("<b>alpha: f64 = 0.5</b>  (Copy: vive completo en el stack)", 20, 265, 390, 26, "align=left;")
    d.caja("Un Vec&lt;T&gt; ocupa 24 B en el stack (puntero, longitud y capacidad); "
           "sus elementos viven contiguos en el heap.", 20, 320, 390, 70, "fontSize=12;align=left;", borde=GRIS, relleno="#FFFFFF")
    d.texto("<b>Buffer de Vec&lt;Layer&gt;</b>  (2 capas contiguas)", 520, 40, 500, 26, "align=left;")
    l0 = d.caja("<b>Layer 0</b>  (2 → 4, Sigmoid)", 520, 68, 380, 30, fila + "fillColor=#E8EDF5;", borde=PURPURA)
    l0w = d.caja("weights: Matrix { rows = 4, cols = 2, data: ptr ● }", 520, 98, 380, 30, fila, borde=PURPURA)
    d.caja("biases, input, z, output, delta: Vector · grad_weights: Matrix", 520, 128, 380, 30, fila + "fontSize=11;", borde=PURPURA)
    d.caja("<b>Layer 1</b>  (4 → 1, Sigmoid)", 520, 158, 380, 30, fila + "fillColor=#E8EDF5;", borde=PURPURA)
    d.caja("weights: Matrix { rows = 1, cols = 4, data: ptr ● } · …", 520, 188, 380, 30, fila + "fontSize=11;", borde=PURPURA)
    d.texto("<b>Datos de weights de Layer 0</b> (W⁽¹⁾): 4 × 2 = 8 valores f64 en orden por filas (64 B contiguos)", 520, 255, 780, 26, "align=left;")
    celdas = []
    for k in range(8):
        i, j = divmod(k, 2)
        relleno = "#F1F5F9" if i % 2 == 0 else "#E2E8F0"
        celdas.append(d.caja(f"w<sub>{i}{j}</sub><br><font style=\"font-size:10px\">[{k}]</font>", 520 + k * 72, 285, 72, 54,
                             "rounded=0;", borde=CIAN, relleno=relleno))
    d.texto("idx(i, j) = i·cols + j   →   W[i][j] = data[i·2 + j]   ·   recorrido secuencial amigable con la caché",
            520, 345, 780, 26, "align=left;fontSize=12;fontColor=#475569;")
    d.texto("<b>Datos de x</b>", 1120, 40, 180, 26, "align=left;")
    xb = [d.caja(f"x<sub>{k + 1}</sub>", 1120 + k * 80, 68, 80, 44, "rounded=0;", borde=CIAN, relleno="#F1F5F9") for k in range(2)]
    puntero = "strokeColor=#B91C1C;endArrow=classic;endFill=1;strokeWidth=1.6;"
    d.flecha(red_layers, l0, "", puntero + "exitX=1;exitY=0.5;entryX=0;entryY=0.5;")
    d.flecha(x_data, xb[0], "", puntero + "exitX=1;exitY=0.5;entryX=0.5;entryY=1;",
             puntos=[(460, 220), (460, 420), (1160, 420)])
    d.flecha(l0w, celdas[0], "", puntero + "exitX=1;exitY=0.5;entryX=0.5;entryY=0;", puntos=[(940, 113), (940, 240), (556, 240)])
    reglas = [
        ("Ownership", "Network posee su Vec&lt;Layer&gt;; cada Layer posee sus Matrix y Vector. "
         "Cuando red sale de ámbito, Drop libera todo el heap en cascada: sin recolector de basura y sin fugas.", AZUL, "#E8EDF5"),
        ("Préstamo inmutable  &amp;T", "predict(&amp;self, x: &amp;Vector) y evaluate_mse(&amp;self, …) solo leen: "
         "admiten varios lectores a la vez y no copian los datos.", VERDE, "#ECF5EF"),
        ("Préstamo mutable  &amp;mut T", "forward, backward, update y train_step(&amp;mut self, …) modifican pesos y cachés: "
         "un único escritor; el compilador impide alias con mutación.", PURPURA, "#E8EDF5"),
        ("Result&lt;T, MathError&gt;", "get(i, j), matmul o add validan índices y dimensiones y devuelven Err "
         "en lugar de acceder fuera de rango o entrar en pánico.", NARANJA, "#F1F5F9"),
    ]
    for k, (t, cuerpo, b, r) in enumerate(reglas):
        d.caja(f"<b>{t}</b><br>{cuerpo}", k * 335, 500, 315, 120, "align=left;verticalAlign=top;fontSize=12;", borde=b, relleno=r)
    d.texto("● puntero (ptr) del Vec hacia su buffer en el heap", 0, 630, 420, 24, "align=left;fontSize=11;fontColor=#B91C1C;")
    return d


# --------------------------------------------------------------------------
def d05_fases():
    d = Diagrama("Fases de la metodología")
    fases = [
        ("Matemática", "Vector&lt;T&gt; y Matrix&lt;T&gt; genéricos: suma, resta, escalar, producto punto, producto matricial y transpuesta",
         "Base de álgebra lineal", CIAN),
        ("Neurona", "Neuron con pesos, bias y forward: z = x·w + b; Layer y Network", "Una neurona calcula su salida", CIAN),
        ("Activaciones", "Activacion::sigmoid y relu; softmax para salidas multiclase", "Salidas como probabilidad", CIAN),
        ("Error y gradiente", "MSE y su derivada; Gradient y GradientDescent", "Regla θ ← θ − α∇ disponible", CIAN),
        ("Primer aprendizaje", "Neurona lineal que aprende y = 2x con MSE", "MSE ≤ 10⁻¹²: w → 2", AZUL),
        ("Clasificación binaria", "Neurona Sigmoid: 0 → falso, 1 → verdadero, umbral 0.5", "Decisión probabilística", AZUL),
        ("Vocales", "Capa 25 → 5 con softmax sobre patrones 5×5 de A, E, I, O, U", "5 de 5 vocales reconocidas", PURPURA),
        ("Validación", "Motor complementario: XOR 2-4-1, ruido, 52 pruebas y gradient checking", "Fundamentos verificados", PURPURA),
        ("Documentación", "Documentación ///, prueba de escritorio, benchmarks, tesis APA 7 y kit de feria",
         "Proyecto educativo abierto", NARANJA),
    ]
    bloques = [("Fundamentos matemáticos", 0, 4, CIAN, "#F8FAFC"), ("Aprendizaje", 4, 6, AZUL, "#F8FAFC"),
               ("Experimentación", 6, 8, PURPURA, "#F8FAFC"), ("Difusión", 8, 9, NARANJA, "#F8FAFC")]
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
    d.texto("Cada flecha es una compuerta de calidad: la fase siguiente inicia cuando la ejecución reproduce el resultado esperado.",
            0, 560, 1200, 26, "align=left;fontSize=12;fontColor=#475569;")
    ciclo = ["Diseñar<br>(ecuaciones y dimensiones)", "Implementar<br>(Rust, sin crates de ML)",
             "Ejecutar y observar<br>(trazas por época)", "Validar<br>(cargo test + gradient checking)",
             "Documentar evidencia<br>(resultados/*.csv)"]
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
