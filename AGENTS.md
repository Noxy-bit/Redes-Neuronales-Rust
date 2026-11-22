# Directrices Maestras del Repositorio — Redes Neuronales desde Cero en Rust (FICCT-UAGRM 2-2026)

## 1. Orden estricto de páginas preliminares de la tesis
1. **Página 1 — Carátula institucional:** Escudo oficial FICCT (`assets/logos/logo_ficct_escudo.jpeg`), Universidad Autónoma Gabriel René Moreno (UAGRM), Facultad de Ingeniería en Ciencias de la Computación y Telecomunicaciones (FICCT), título del proyecto, materia (`Programación 1 - INF120`), grupo (`SH-SD`), variables editables `[NOMBRE_DOCENTE_COMPLETO]`, `[CODIGO_DOCENTE]` y `[NRO_PROYECTO]`, lista de los 5 integrantes con su código ORCID y ciudad/año (Santa Cruz de la Sierra - Bolivia, 2026).
2. **Página 2 — Identificación de Investigadores y ORCID:** Explicación breve de ORCID + tabla detallada con los 5 integrantes: Nombre completo, Número de Registro universitario, Carrera, Grupo (`SH-SD`), ID ORCID y rol en el proyecto.
3. **Página 3 — Agradecimientos (sección formal obligatoria):**
   - Al **Ing. Hugo Acosta** (`[CONFIRMAR_NOMBRE_COMPLETO_PROGRAMACION_1]`), docente de la asignatura Programación 1 (`INF120`), por su guía académica y respaldo técnico.
   - Al **Lic. Edwin Vargas Yapura** (`[CONFIRMAR_TITULO_Y_CARGO_COMPLETO]`), Coordinador del Instituto de Investigación de la FICCT (IICCT) y organizador de la Feria Facultativa FICCT-UAGRM, por el impulso a los semilleros de investigación y las orientaciones metodológicas.
   - A la **Universidad Autónoma Gabriel René Moreno (UAGRM)**, a la **Facultad de Ingeniería en Ciencias de la Computación y Telecomunicaciones (FICCT)** y al **Instituto de Investigación (IICCT)** por el espacio formativo e institucional.
   - A nuestras familias y compañeros de equipo por el esfuerzo colaborativo durante el desarrollo del proyecto.
4. **Siguientes preliminares (numeración romana):** Resumen y Abstract (con Palabras Clave / Keywords), Índice General, Índice de Figuras, Índice de Tablas e Índice / Lista de Códigos.

## 2. Riqueza documental y contextualización multinivel (Capítulo 1)
La contextualización y justificación deben estructurarse con enfoque de embudo y datos verificables (citados en APA 7) cubriendo explícitamente los **cinco niveles de análisis**:
- **Nivel Internacional:** Crecimiento global de la IA, brecha entre usuarios de frameworks de "caja negra" y desarrolladores que dominan fundamentos matemáticos, y adopción de Rust en ingeniería de sistemas e IA de alto rendimiento.
- **Nivel Nacional (Bolivia):** Estado de la formación en ciencias de la computación, transformación digital, demanda de talento en IA y adopción de tecnologías emergentes en universidades bolivianas.
- **Nivel Departamental (Santa Cruz):** Ecosistema tecnológico cruceño, industria del software, comunidades tech y necesidad de formación de ingenieros con base matemática y algorítmica sólida.
- **Nivel Regional / Provincial:** Descentralización del conocimiento tecnológico hacia provincias del departamento y acceso a recursos educativos Open Source sin depender de hardware costoso ni licencias pagadas.
- **Nivel Local (UAGRM – FICCT):** Realidad académica de los estudiantes de primeros semestres en Programación 1 (`INF120`) y el impacto directo de los Semilleros de Investigación del IICCT.

## 3. Estándar editorial anti-choque de títulos y diseño atractivo
- **Cero choque de títulos:** Prohibido dejar títulos huérfanos al final de una página (`needspace` / `keep-with-next` obligatorio), prohibido colocar dos títulos seguidos sin párrafo introductorio entre ellos y prohibido solapar encabezados de página (*running head*) con títulos de capítulo o figuras.
- **Ritmo visual profesional:** Alternar texto técnico conciso con ecuaciones numeradas en LaTeX, cajas de nota técnica/resumen (*callouts*), tablas limpias estilo APA 7 (sin bordes verticales), diagramas `.drawio` exportados en 300 DPI, gráficas generadas desde CSV reales y bloques de código Rust con sintaxis resaltada y numeración de líneas.
- **Datos reales obligatorios:** Prohibido inventar resultados experimentales; toda pérdida, precisión, matriz de confusión o tiempo de ejecución proviene de `resultados/*.csv`.

## 4. Branding RN y estándar gráfico FICCT (carpeta `feria/`)
- **Libertad creativa en identidad RN:** Las imágenes en `assets/branding/` son inspiración de paleta y concepto; el agente puede diseñar el isotipo/logo vectorial RN propio en **versión fondo oscuro y versión fondo claro** (`.svg` + PNG 300 DPI).
- **Elementos obligatorios en Banners y Credenciales FICCT:**
  - Incluir los tres sellos oficiales desde `assets/logos/`: `logo_uagrm.jpeg`, `logo_ficct_escudo.jpeg` y `logo_iicct.jpeg`.
  - Mostrar de forma destacada el **Número de Proyecto (`#[NRO_PROYECTO]`)** configurable.
  - Incluir **código QR grande** ("Escanea para más información") en el banner y en las credenciales/tríptico.
  - En credenciales: nombre completo, registro universitario, carrera, rol (`Expositor`), logo RN + sellos FICCT/IICCT y marco opcional para foto del estudiante.

## 5. Requisitos oficiales de entrega (Moodle — `Documento-Final-REVISADO`)
- **Cierre oficial:** Miércoles 25 de noviembre de 2026, 23:55.
- **Secciones obligatorias (deben figurar de forma explícita y localizable en el Índice General):**
  1. Carátula
  2. Índice (General, Figuras, Tablas y Lista de Códigos)
  3. Contextualización (multinivel: internacional, nacional, departamental, regional/provincial y local)
  4. Planteamiento del Problema
  5. Justificación
  6. Objetivo General
  7. Objetivos Específicos
  8. Marco Teórico (fundamentos matemáticos de redes neuronales + fundamentos técnicos de Rust)
  9. Descripción de la Propuesta Solución (arquitectura modular, implementación por fases en Rust, prueba de escritorio, 3 experimentos reales `y=2x`, `XOR` y vocales `A-E-I-O-U`, gráficas 300 DPI y validación/benchmarks)
  10. Conclusiones y Recomendaciones
  11. Bibliografía (formato APA 7ª edición)
  12. Anexos (código fuente completo, manual Cargo, listado de `.drawio`, roles del equipo y Carta de Compromiso)
- **Número de proyecto:** Mantener el número oficial asignado en la carátula y en todo el kit gráfico; si todavía no existe número asignado, usar **`0`** como valor por defecto configurable (`PROY_NUM=0`).
- **Nomenclatura exacta del entregable final:** Además del `.docx` editable, el script de compilación debe exportar el PDF final exactamente como **`tesis/build/Proy-<NUM>-Doc-Final.PDF`** (ej. `Proy-0-Doc-Final.PDF`).

## 6. Estándar oficial de Logos y Trípticos FICCT (`feria/`)
- **Logos (`feria/logos/`):** Entregar el logo vectorial RN limpio en formato `.svg`, `.png` con fondo transparente (300 DPI) en versión clara y oscura, y un `.pdf` presentable listo para `Entrega-LOGOS`. Prohibido usar imágenes con marcas de agua o baja resolución.
- **Tríptico doble cara (`feria/triptico/`):** Hoja Carta apaisada (6 caras con guías de pliegue):
  - *Cara exterior:* (1) Portada con logos UAGRM, FICCT, IICCT, `Proyecto #<NUM>`, logo RN, título y eslogan; (2) Contraportada con integrantes, materia `INF120`, correos/repositorio y código QR grande ("Escanea para más información"); (3) Solapa con sección "¿Quiénes somos?" y el impacto de abrir la "caja negra" de la IA.
  - *Cara interior:* (4) Contexto y problemática; (5) Objetivo general y objetivos específicos; (6) Propuesta técnica en Rust puro + resultados reales de los 3 experimentos.
- **Control de calidad editorial:** Verificar cero faltas de ortografía, cero texto de relleno (*Lorem ipsum*) y contraste legible tanto en pantalla como impreso.

## 7. Nombres oficiales confirmados y reglas de Entrega-LOGOS
- **Docente Tutor (Programación 1 - INF120):** MSc. Ing. Víctor Hugo Acosta Ortega.
- **Organizador Feria / Coordinador IICCT:** MSc. Edwin Vargas Yapura.
- **Número de proyecto inicial:** 0 (variable editable PROY_NUM=0 hasta confirmar #Fila en la lista oficial de la Feria 2-2026).
- **Requisitos exactos de Entrega-LOGOS (cierre miércoles 25 nov 23:59):** colores representativos al dominio, sin texto recargado (isotipo o siglas RN), vectorial limpio sin marcas de agua, exportar como `feria/logos/Proy-<NUM>-LOGO.PDF` (+ SVG y PNG transparente).
