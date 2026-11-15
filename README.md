# biblia-chuj-smi
Biblia en Chuj de San Mateo Ixtatán

# Descripción del proyecto

La primera version de esta biblia en formato Zefania XML (compatible con varios softwares de lecture de biblia) está basada en la versión de la Sociedad Bíblica de Guatemala.
La intención de este repositorio es actualizar esta version de la biblia basandose en la "Gramática normativa Chuj" de la Academia de Lenguas Mayas.

# Como apoyar

Cualquiera con el conocimiento de Git puede colaborar con el proyecto y crear un "Pull request" con los cambios que crea necesarios, si no pueden enviar un correo con un archivo excel a info@iglesiacuentrocondios.net con dos columnas, una columna de la palabra o frase que se desea corregir y otra columna de la corrección.

Todas las colaboraciones serán revisadas antes de ser aceptadas.

# Visor, API y módulo de MyBible

El texto vigente es `CHSM_fixed.xml` (Zefania XML). Con cada cambio en `main` la acción *Publicar API y visor* genera:

- **Visor web instalable (PWA)**: https://encuentrocondios.github.io/biblia-chuj-smi/ (se lee sin conexión y se puede instalar desde el navegador).
- **API JSON estática** en la misma dirección:
  - `books.json`: libros (`name`, `short_name`, `number`, `testament`, `chapters`, `verses`).
  - `{libro}/{capitulo}.json`: un capítulo (`chapter`, `verses[{number, text}]`, `aligned`, `es_verses`).
  - `{libro}.json`: libro completo, compacto. `es/{libro}.json`: Reina-Valera 1909 (dominio público) para comparar.
  - `revision.json`: capítulos cuyo número de versículos no coincide con el español (para revisar la traducción).
  - `version.json`: fecha y totales.
- **Módulo de MyBible (Android)**: ver los *releases*. Registry: `https://github.com/encuentrocondios/biblia-chuj-smi/releases/latest/download/CHSMI.registry.json`

Herramientas (`tools/`):

- `build_api.py`: genera la API y empaqueta `visor/` en `output/`.
- `fix_chuj_ortografia.py`: aplica el alfabeto oficial de la ALMG (sin `c`, `qu`, `v`; `d'` → `t'`) respetando nombres propios (`nombres.txt`). Uso: `python tools/fix_chuj_ortografia.py CHSM_fixed.xml SPARV.xml salida.xml cambios.csv pendientes.csv`
- `zefania_to_mybible.py`: convierte el XML en módulo `.SQLite3` para MyBible.

El español de comparación es Reina-Valera **1909**. La 1960 tiene derechos de autor y no se incluye.
