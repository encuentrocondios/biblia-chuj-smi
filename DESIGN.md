---
name: Biblia Chuj · San Mateo Ixtatán
description: Un visor bíblico PWA cuyo marco es sal negra y cuyo centro es una columna de lectura serena en sal blanca, con una sola brasa como acento.
colors:
  sal-negra: "#1F1A17"
  sal-negra-hondo: "#100D0C"
  sal: "#F3F5F4"
  tinta: "#1A1715"
  niebla: "#4F5B5D"
  brasa: "#B03E15"
  brasa-marco: "#F28F63"
  celda: "#E3E8E7"
  linea: "#CBD3D2"
  borde: "#7A8789"
  sobre-marco: "#F3F5F4"
  sal-oscuro: "#1E1917"
  tinta-oscuro: "#EBEEED"
  niebla-oscuro: "#A5B0B2"
  brasa-oscuro: "#F0865B"
  celda-oscuro: "#2B2421"
  linea-oscuro: "#3B332F"
  borde-oscuro: "#868F91"
typography:
  display:
    fontFamily: "Literata, Iowan Old Style, Palatino Linotype, Georgia, serif"
    fontSize: "clamp(2.5rem, 9vw, 3.75rem)"
    fontWeight: 800
    lineHeight: 1.02
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Literata, Iowan Old Style, Palatino Linotype, Georgia, serif"
    fontSize: "clamp(2.25rem, 8vw, 3.25rem)"
    fontWeight: 800
    lineHeight: 1.05
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, sans-serif"
    fontSize: "1.2rem"
    fontWeight: 800
    lineHeight: 1.1
  body:
    fontFamily: "Literata, Iowan Old Style, Palatino Linotype, Georgia, serif"
    fontSize: "1.25rem"
    fontWeight: 400
    lineHeight: 1.68
  body-secondary:
    fontFamily: "Literata, Iowan Old Style, Palatino Linotype, Georgia, serif"
    fontSize: "0.86em"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 700
    lineHeight: 1
rounded:
  xs: "0.25rem"
  sm: "0.4rem"
  md: "0.5rem"
  lg: "0.6rem"
spacing:
  xs: "0.25rem"
  sm: "0.5rem"
  md: "1rem"
  lg: "1.75rem"
  xl: "3rem"
  masthead-height: "3.5rem"
  rail-height: "3.75rem"
  tap-target: "2.75rem"
components:
  masthead:
    backgroundColor: "{colors.sal-negra}"
    textColor: "{colors.sobre-marco}"
    height: "3.5rem"
  rail:
    backgroundColor: "{colors.sal-negra}"
    textColor: "{colors.sobre-marco}"
    height: "3.75rem"
  verse-action-bar:
    backgroundColor: "{colors.sal-negra-hondo}"
    textColor: "{colors.sobre-marco}"
    padding: "0.4rem 0.5rem 0.4rem 0.75rem"
  button:
    backgroundColor: "transparent"
    textColor: "{colors.tinta}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    height: "2.9rem"
    padding: "0 1.1rem"
  button-hover:
    backgroundColor: "{colors.tinta}"
    textColor: "{colors.sal}"
  crystal-cell:
    backgroundColor: "{colors.celda}"
    textColor: "{colors.tinta}"
    rounded: "0"
    padding: "0.6rem 0.7rem"
    height: "4.25rem"
  field:
    backgroundColor: "{colors.sal}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.sm}"
    height: "3rem"
    padding: "0.6rem 0.9rem"
  notice:
    backgroundColor: "{colors.celda}"
    textColor: "{colors.niebla}"
    rounded: "{rounded.md}"
    padding: "0.9rem 1rem"
  settings-popover:
    backgroundColor: "{colors.sal}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.lg}"
    padding: "1.1rem 1.1rem 0.9rem"
---

# Design System: Biblia Chuj · San Mateo Ixtatán

## Overview

**Creative North Star: "La Sal Negra" (atz'am k'ik')**

El visor pertenece a San Mateo Ixtatán por su sal, no por motivos textiles prestados: un marco mineral alrededor de una columna de lectura tranquila. La franja superior y la barra inferior son losas de sal negra con letras de sal blanca; entre ellas, el texto reposa sobre un fondo de sal blanca ligeramente azulada. Un único acento, la brasa del fogón donde hierve la salmuera, marca los números de versículo, el lugar actual y el foco.

La densidad es baja y la jerarquía plana: nada actúa detrás del texto. El título del capítulo es una sola línea pesada en Literata ("Salmo 95", con el número en brasa); el versículo es lo más grande del cuerpo. La interfaz usa Atkinson Hyperlegible Next, sobria y de alto contraste, pensada para pantallas de gama media a plena luz y vista reducida. El modo oscuro no inventa otro mundo: el fondo de lectura se vuelve la propia sal negra, tibia y parda.

Rechazos confirmados por el contrato de dirección: el "libro antiguo" crema con serifa, y el azul genérico de las apps bíblicas.

**Key Characteristics:**
- Marco de sal negra (franja y barra) con columna de lectura de 38rem.
- Un solo acento, la brasa, usado con escasez (números, lugar actual, foco, casilla marcada).
- Serifa Literata para el texto sagrado; sans Atkinson para controles.
- Selector en retícula de cristales de sal: celdas cuadradas, esquinas opuestas cortadas, mortero de 2px.
- Plano por defecto: la profundidad es tonal; solo las superficies flotantes llevan sombra.
- Objetivos táctiles de 2.75rem como mínimo.

## Colors

Una paleta mineral y cálida: negros pardos de sal quemada, blancos fríos de sal cristalina, grises de niebla y una brasa naranja rojiza.

### Primary
- **Brasa del Fogón** ({colors.brasa}): único acento sobre fondo claro. Números de versículo, número del capítulo en el título, resaltado de búsqueda (al 22%), selección de versículo (al 13%), foco (contorno de 3px), caja marcada, marca de "último leído" y borde inferior de la celda actual. En oscuro pasa a {colors.brasa-oscuro}.
- **Brasa sobre Marco** ({colors.brasa-marco}): la misma brasa aclarada para iconos y foco sobre la sal negra (masthead, barra, acciones).

### Neutral
- **Sal Negra** ({colors.sal-negra}): marco de la franja y la barra inferior; botón "Seguir leyendo"; theme-color y fondo del manifiesto.
- **Sal Negra Honda** ({colors.sal-negra-hondo}): barra de acciones de versículo, una capa más hundida que el marco; en oscuro es el marco mismo.
- **Sal Blanca** ({colors.sal}): fondo de lectura y de campos. En oscuro: {colors.sal-oscuro}.
- **Tinta** ({colors.tinta}): texto principal y contorno de botones. En oscuro: {colors.tinta-oscuro}.
- **Niebla** ({colors.niebla}): texto secundario, rótulos, marcadores de posición. En oscuro: {colors.niebla-oscuro}.
- **Cristal de Sal** ({colors.celda}): relleno de celdas del selector y de avisos; hover de versículos. En oscuro: {colors.celda-oscuro}.
- **Mortero** ({colors.linea}): divisores de 1px, mortero entre celdas y facetas cortadas. En oscuro: {colors.linea-oscuro}.
- **Borde de Control** ({colors.borde}): borde de 2px de campos, al menos 3:1 sobre el fondo. En oscuro: {colors.borde-oscuro}.
- **Letra sobre Marco** ({colors.sobre-marco}): texto e iconos sobre la sal negra.

### Named Rules
**La Regla de la Única Brasa.** La brasa es el único color con croma; no se añade un segundo acento. Su escasez es lo que señala "aquí estás".

**La Regla del Marco Negro.** Franja, barra inferior y barra de acciones son siempre sal negra, también en modo claro; el tema solo cambia el lienzo central.

## Typography

**Display Font:** Literata (peso 800, eje opsz 72), con Iowan Old Style, Palatino Linotype, Georgia, serif
**Body Font:** Literata (peso 400, opsz 14), misma pila; cursiva para la comparación en español
**Label/UI Font:** Atkinson Hyperlegible Next, con system-ui, Segoe UI, Roboto, sans-serif

**Character:** una serifa de lectura larga con presencia pesada en los títulos, junto a una sans de legibilidad máxima para el cromo. Ambas se sirven locales en woff2 (subconjunto latino) para funcionar sin conexión.

### Hierarchy
- **Display** (800, clamp(2.5rem, 9vw, 3.75rem), 1.02, -0.02em): título del capítulo, una sola línea; el número va en brasa.
- **Headline** (800, clamp(2.25rem, 8vw, 3.25rem), 1.05): título de "Libros" y del libro elegido.
- **Title** (800, 1.2rem, 1.1; Literata en el título del popover de ajustes): rótulos de panel, código de libro en la celda (Atkinson 800 1.2rem).
- **Body** (400, 1.25rem por defecto, 1.68): versículos. `--leer` se ajusta con la preferencia de tamaño; columna de 38rem, `hyphens:none` y `overflow-wrap:break-word` para no partir palabras en el apóstrofo.
- **Body secondary** (italic 400, 0.86em, 1.5, niebla): versículo en español de comparación bajo el chuj.
- **Label** (Atkinson 700 a 800, 0.9rem a 1.15rem): botones, rutas, número de versículo (0.72em, brasa, cifras tabulares).

### Named Rules
**La Regla del Apóstrofo.** El apóstrofo de b', t', k', tz', ch' es una letra: se pinta como U+02BC y nunca se parte la palabra ahí.

**La Regla de los Dos Registros.** Serifa para texto bíblico, títulos y resultados; sans solo para controles, códigos y rótulos.

## Layout

Una columna central: lectura de 38rem, selector de 44rem, búsqueda de 42rem, centradas con relleno lateral de 1.25rem (lectura) o 1rem y respetando las áreas seguras. El marco (franja de 3.5rem, barra de 3.75rem) es fijo y sus contenidos se alinean a la misma medida de 46rem en pantallas anchas. El ritmo vertical se apoya en múltiplos de 0.25rem; los versículos van en una rejilla de dos columnas (2.35rem de número, 3rem desde 46rem). La retícula de libros usa `repeat(auto-fill, minmax(7.6rem, 1fr))` (capítulos: 3.6rem) con 2px de mortero. Primero móvil (390px); un solo punto de ruptura en 46rem. El cuerpo reserva espacio para franja y barra, y las barras flotantes usan `env(safe-area-inset-*)`.

## Elevation & Depth

Plano por defecto; la profundidad es tonal. El marco negro contra el lienzo claro, las celdas de cristal contra el fondo y el mortero de 1px bastan. La sombra aparece solo en superficies que flotan sobre el texto.

### Shadow Vocabulary
- **Barra de acciones** (`box-shadow: 0 -10px 24px -12px #000a`): la barra de copiar/compartir que sube sobre la barra inferior.
- **Popover de ajustes** (`box-shadow: 0 18px 40px -16px #000b`): panel de ajustes bajo la franja.
- **Celda de cristal** (`box-shadow: 0 0 0 1px var(--linea)`): no es sombra sino contorno de 1px; la celda actual añade `inset 0 -.28rem 0 brasa`.

### Named Rules
**La Regla de lo Plano en Reposo.** El texto, las celdas y los botones no llevan sombra; solo lo que se superpone la tiene, y es difusa, nunca desplazada y dura.

## Shapes

Esquinas contenidas y minerales. Controles y campos con radio de 0.4rem; tarjetas y avisos de 0.5rem; popover de 0.6rem; botones de franja de 0.5rem; foco con 2px. La firma es la celda de cristal: cuadrada, sin radio, con dos facetas cortadas en esquinas opuestas (degradados a 225deg de 0.75rem y a 45deg de 0.4rem) y 2px de mortero. Los bordes de controles son de 2px; los divisores, de 1px.

## Components

### Franja (masthead)
Losa de sal negra de 3.5rem: a la izquierda la referencia actual ("Salmo 95") con el icono de retícula, a la derecha búsqueda y ajustes en botones de 2.75rem. Hover: velo blanco al 8%. Foco: contorno brasa-marco.

### Barra inferior (rail)
Losa de sal negra de 3.75rem en tres zonas: capítulo anterior, Libros (icono de retícula en brasa-marco), capítulo siguiente. Vínculos de 2.75rem; deshabilitado a 35% de opacidad.

### Versículo
Fila de rejilla con el número en brasa a la izquierda (botón con zona táctil ampliada a 44px) y el texto a la derecha. Hover: celda al 55%. Seleccionado: fondo brasa al 13% y número subrayado 2px.

### Celda de cristal (firma)
- **Forma:** cuadrada, facetas cortadas, mortero de 2px, altura mínima 4.25rem (3.6rem para capítulos).
- **Contenido:** código del libro en Atkinson 800 y nombre en niebla; capítulos solo con cifra.
- **Estados:** hover oscurece el relleno; actual (`aria-current`) lleva borde inferior brasa de 0.28rem; último leído lleva una marca brasa de 1.1rem por 0.2rem.
- **Entrada:** aparece con retraso escalonado de 14ms por celda, `entra` .5s con `cubic-bezier(.16,1,.3,1)`; sin movimiento si el usuario lo reduce.

### Botones
Contorno de 2px en tinta, radio 0.4rem, 2.9rem de alto, texto 700. Hover: se rellena de tinta con texto de sal. El botón "Seguir leyendo" es una losa de sal negra con flecha brasa. El paso de tamaño de texto es del mismo tipo (A− / A+), y el selector Auto/Claro/Oscuro es un segmentado con borde de 2px cuya opción activa se rellena de tinta.

### Campos
Fondo sal, borde de 2px en borde de control, radio 0.4rem, 3rem de alto (3.25rem en búsqueda, con texto en Literata). Foco: el borde pasa a brasa, sin contorno extra. Marcador en niebla.

### Aviso y casilla
Aviso: fondo cristal, radio 0.5rem, texto niebla con negrita en tinta (usado para capítulos cuyos versículos no coinciden con el español). Casilla: caja de 1.6rem, borde de tinta; marcada se rellena de brasa con una marca de sal.

### Barra de acciones de versículo
Franja de sal negra honda sobre la barra inferior, con referencia, Copiar, Compartir y cerrar; entra desde abajo en .35s.

## Do's and Don'ts

### Do:
- **Do** usar la brasa ({colors.brasa}) solo para números de versículo, lugar actual, foco y estados marcados.
- **Do** mantener el marco (franja, barra, acciones) en sal negra en ambos temas.
- **Do** dar a cada objetivo táctil al menos 2.75rem (2.9rem en botones) y bordes de control de 2px con contraste de 3:1.
- **Do** componer los selectores como retículas de celdas cuadradas con facetas cortadas y mortero de 2px.
- **Do** usar Literata para texto y títulos, y Atkinson para controles; servir las fuentes localmente.
- **Do** respetar `prefers-reduced-motion` y las áreas seguras del dispositivo.

### Don't:
- **Don't** usar azul genérico de app bíblica ni el crema de "libro antiguo".
- **Don't** añadir un segundo color de acento.
- **Don't** poner sombras en reposo sobre texto, celdas ni botones.
- **Don't** partir una palabra en el apóstrofo ni dibujarlo con comilla recta.
- **Don't** hacer que algo se anime detrás del texto de lectura.
- **Don't** introducir iconos de glifo ni fuentes de sistema como cara de título; los iconos son símbolos SVG inline.
