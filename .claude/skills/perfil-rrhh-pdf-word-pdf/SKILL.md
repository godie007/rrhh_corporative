---
name: perfil-rrhh-pdf-word-pdf
description: >-
  Lee un PDF de perfil o CV desde una ruta que indique el usuario, genera dos
  .docx como analista de RR.HH. (corporativo vs logros), compara con rúbrica y
  exporta la elegida a PDF en output/ del proyecto. Usar con CV en PDF, dos
  versiones Word, o conversión a PDF final en carpeta output.
dependencies: python>=3.10, pdfplumber, python-docx
---

# Perfil RR.HH.: PDF → 2× Word → validar → PDF

## Entrada y salida

- **PDF de entrada**: ruta absoluta o relativa que proporcione el usuario (ejemplo de referencia: `/ruta/al/cv.pdf`).
- **Salida**: todo se escribe en **`output/`** en la **raíz del repositorio** (carpeta del proyecto que contiene `.claude/skills/`), no dentro del directorio del skill.

## Antes de cada ejecución

1. [ ] Ir al directorio del skill: `.claude/skills/perfil-rrhh-pdf-word-pdf/`.
2. [ ] Vaciar la carpeta de salida del proyecto y obtener su ruta:
   ```bash
   bash scripts/prepare_output.sh
   ```
   Devuelve una línea con la ruta a `.../output` (útil para `-o` en los siguientes comandos).
3. [ ] Definir `OUT` si hace falta: `OUT="$(bash scripts/prepare_output.sh | tail -1)"` — o usar rutas relativas `../../../output/` desde el directorio del skill.

## Cuándo aplicar

- El usuario entrega o menciona un **PDF** de CV, perfil profesional o hoja de vida.
- Debe haber **dos borradores en Word** en `output/` y el **PDF final** del mejor allí mismo.

## Profundidad del análisis RR.HH. (obligatorio)

Cada uno de los **dos documentos Word** debe incluir un bloque **`hr_analysis`** (ver JSON) que sea un **análisis de RR.HH. real**, no un resumen de tres líneas:

- **Extensión orientativa**: **250–450 palabras** en el campo `hr_analysis.body` (ajustar al contenido del PDF: perfiles largos → análisis más largo).
- **Versión A (corporativo)**: diagnóstico alineado a **encaje cultural, competencias transversales, nivel de seniority, riesgos de contratación** y recomendación de **cómo presentar el perfil** en procesos formales / ATS.
- **Versión B (ejecutiva / logros)**: el **mismo candidato** pero diagnóstico centrado en **impacto, resultados medibles, narrativa para decisiones rápidas** y posicionamiento frente a **negocio o dirección**.
- Las dos versiones deben ser **claramente distintas** (no solo sinónimos): distinto **énfasis**, **orden de ideas** y **tipo de recomendación**, no solo otro color.
- El resto de secciones (resumen, experiencia, etc.) deben ser **completas** respecto al PDF de origen, sin dejar fuera datos relevantes.

## Temas visuales (Word)

- En el JSON, **`theme": "corporate"`** para la versión corporativa (azul institucional en títulos).
- **`"theme": "executive"`** para la versión ejecutiva (teal / gris sobrio).
- El script aplica **Calibri**, tamaños legibles y colores profesionales; no uses solo texto plano sin `theme` ni sin `hr_analysis`.

## Cómo usar este skill desde Claude Code

1. **Requisito**: proyecto abierto en Claude Code donde exista esta carpeta: `.claude/skills/perfil-rrhh-pdf-word-pdf/` (debe estar presente en el workspace).
2. **Dependencias** una vez: en terminal integrada o shell, `cd` al directorio del skill y `pip install -r requirements.txt` (o `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`).
3. **Invocación**: en el chat de Claude Code, pide explícitamente el flujo, por ejemplo: *“Usa el skill perfil-rrhh-pdf-word-pdf: PDF en `/ruta/a/mi/cv.pdf`, deja salida en `output/` del proyecto y ejecuta extracción, dos versiones Word con análisis RR.HH. completos, rúbrica y PDF final.”*  
   Claude Code **descubre** el skill por la descripción en el frontmatter; si no lo aplica, nómbralo: **“sigue las instrucciones de `.claude/skills/perfil-rrhh-pdf-word-pdf/SKILL.md`”**.
4. **Rutas**: el agente debe trabajar desde el directorio del skill para los comandos `python scripts/...` y usar `../../../output/` o la ruta que devuelve `bash scripts/prepare_output.sh`.

## Flujo (checklist)

1. [ ] Confirmar ruta del PDF de entrada (ej.: `/ruta/al/cv.pdf`) y (opcional) puesto/objetivo.
2. [ ] Tras `prepare_output.sh`, extraer texto:
   ```bash
   python scripts/extract_pdf_text.py "/ruta/al/cv.pdf" -o ../../../output/extracted.txt
   ```
   Sustituir `"/ruta/al/cv.pdf"` por la ruta real que indique el usuario (entre comillas si la ruta tiene espacios).
3. [ ] Si el texto está vacío o es basura → PDF escaneado: ver [reference.md](reference.md) (OCR opcional).
4. [ ] Redactar **dos versiones** como analista de RR.HH. a partir del texto extraído, cumpliendo [Profundidad del análisis](#profundidad-del-análisis-rrhh-obligatorio):
   - **Versión A**: `theme: "corporate"` + análisis tipo encaje/ATS/competencias.
   - **Versión B**: `theme: "executive"` + análisis tipo impacto/negocio (mismo CV, otro ángulo).
5. [ ] Crear dos JSON en `output/` (p. ej. `payload_v1.json`, `payload_v2.json`) con `hr_analysis` completo y generar:
   - `../../../output/perfil_v1_rrhh_corporativo.docx`
   - `../../../output/perfil_v2_rrhh_logros.docx`
   ```bash
   python scripts/build_docx.py --json ../../../output/payload_v1.json --out ../../../output/perfil_v1_rrhh_corporativo.docx
   python scripts/build_docx.py --json ../../../output/payload_v2.json --out ../../../output/perfil_v2_rrhh_logros.docx
   ```
6. [ ] **Evaluar** A vs B con la [rúbrica](#rúbrica-rrhh).
7. [ ] Elegir la mejor versión; si empate fuerte, **preguntar al usuario**.
8. [ ] Convertir el `.docx` elegido a PDF en `output/`:
   ```bash
   python scripts/docx_to_pdf.py ../../../output/perfil_v1_rrhh_corporativo.docx -o ../../../output/perfil_rrhh_final.pdf
   ```
   (Ajustar el `.docx` de entrada según la versión elegida.)
9. [ ] **Limpieza opcional**: eliminar intermedios que no quiera conservar (`extracted.txt`, `payload_*.json`) y dejar en `output/` sobre todo los dos `.docx`, `perfil_rrhh_final.pdf` y, si aplica, un `README` o nota breve con la justificación de la elección.

## JSON para `build_docx.py`

Estructura esperada (UTF-8). **`theme`** y **`hr_analysis`** son obligatorios para el flujo completo.

```json
{
  "title": "Nombre Apellido — Perfil profesional",
  "theme": "corporate",
  "hr_analysis": {
    "heading": "Análisis RR.HH. — Diagnóstico del perfil (enfoque corporativo)",
    "body": "Texto largo en varios párrafos separados por \\n\\n. Mínimo orientativo 250 palabras: fortalezas, encaje, gaps, recomendaciones de posicionamiento y riesgos. Debe reflejar todo el contenido relevante del PDF."
  },
  "sections": [
    { "heading": "Resumen profesional", "body": "Varios párrafos según el CV; no escatimar." },
    { "heading": "Experiencia", "body": "..." },
    { "heading": "Formación", "body": "..." },
    { "heading": "Competencias", "body": "..." },
    { "heading": "Idiomas / Otros", "body": "..." }
  ]
}
```

- Segunda versión: `"theme": "executive"` y otro `hr_analysis.heading` + cuerpo con **énfasis distinto** (impacto, métricas, narrativa ejecutiva).

## Rúbrica RRHH

| Criterio | Qué mirar |
|----------|-----------|
| Claridad | Jerarquía de ideas, sin párrafos densos innecesarios. |
| Adecuación | Si el usuario dio puesto/sector, ¿refleja palabras clave y nivel? |
| Diferenciación | Evita redundancias entre secciones; cada bloque aporta valor. |
| Longitud | Ni excesivamente largo ni tan corto que pierda credibilidad. |
| Palabras clave | Términos buscables por ATS/reclutadores donde aplique. |

Tras puntuar, **elige una versión** y justifica en **3–5 viñetas** citando criterios.

## Dependencias

Desde el directorio del skill:

```bash
pip install -r requirements.txt
```

Para PDF final: **LibreOffice** (macOS: `brew install --cask libreoffice`) o **Microsoft Word** con `docx2pdf` y flag `--word` en `docx_to_pdf.py`.

## Scripts

| Script | Uso |
|--------|-----|
| `scripts/prepare_output.sh` | Vacía `output/` del proyecto y muestra su ruta |
| `scripts/extract_pdf_text.py` | PDF → texto por página |
| `scripts/build_docx.py` | JSON → `.docx` |
| `scripts/docx_to_pdf.py` | `.docx` → PDF (LibreOffice o `--word`) |

## Recursos

- OCR, LibreOffice, rúbrica extendida: [reference.md](reference.md)
