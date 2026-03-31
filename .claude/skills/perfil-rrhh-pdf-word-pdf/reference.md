# Referencia: perfil-rrhh-pdf-word-pdf

## Claude Code (recordatorio)

- El skill vive en `.claude/skills/perfil-rrhh-pdf-word-pdf/`. Claude Code carga skills del proyecto automáticamente.
- Pide en chat: *“Ejecuta el skill perfil-rrhh-pdf-word-pdf con mi PDF en `…/cv.pdf`”* o *“Sigue `SKILL.md` de perfil-rrhh”*.
- Requisitos: `pip install -r requirements.txt` en el directorio del skill; para PDF final, LibreOffice o `--word`.

## JSON: `theme` y `hr_analysis`

- `"theme": "corporate"` o `"executive"` colorea títulos (azul vs teal/gris).
- `hr_analysis` debe ser un análisis extenso (orientativo 250–450 palabras); ver `SKILL.md`.

## Directorio `output/`

- Todos los artefactos generados van a **`output/`** en la raíz del repo (hermano de `.claude/`), no dentro del skill.
- Antes de una nueva corrida: `bash scripts/prepare_output.sh` desde el directorio del skill (vacía `output/` y muestra la ruta).

## PDF escaneado (sin texto seleccionable)

Si `extract_pdf_text.py` devuelve vacío o texto inútil:

1. Instalar [Tesseract](https://github.com/tesseract-ocr/tesseract) y, si quieres un flujo integrado, `ocrmypdf`:
   - macOS: `brew install tesseract ocrmypdf`
2. Generar un PDF con capa de texto:  
   `ocrmypdf entrada.pdf salida_ocr.pdf`
3. Volver a ejecutar la extracción sobre `salida_ocr.pdf` guardando en `output/extracted.txt`.

Alternativa: herramientas gráficas (Adobe, Preview con OCR en algunos flujos) según tu entorno.

## LibreOffice (conversión a PDF)

- **macOS (Homebrew)**: `brew install --cask libreoffice`  
  El binario suele estar en `/Applications/LibreOffice.app/Contents/MacOS/soffice`.
- Si `docx_to_pdf.py` no lo encuentra, exporta la variable:  
  `export LIBREOFFICE_PATH="/Applications/LibreOffice.app/Contents/MacOS/soffice"`

## Microsoft Word (docx2pdf)

- Requiere Word instalado (macOS o Windows).
- `pip install docx2pdf` ya está en `requirements.txt`.
- Uso forzado: `python scripts/docx_to_pdf.py archivo.docx --word -o salida.pdf`

## Rúbrica extendida (opcional)

Además de los criterios del `SKILL.md`, puedes valorar:

| Criterio | Pregunta guía |
|----------|-----------------|
| Coherencia narrativa | ¿El resumen condice con la experiencia listada? |
| Métricas | En versión B, ¿hay números o porcentajes cuando es posible? |
| Neutralidad de sesgo | ¿Se evitan datos no solicitados (edad, foto, estado civil) salvo que el mercado lo exija? |
| Formato | ¿Encabezados consistentes y sin errores ortográficos graves? |

## Comandos rápidos (desde el directorio del skill)

Sustituye la ruta del PDF por la que indique el usuario (ejemplo: `/ruta/al/cv.pdf`):

```bash
pip install -r requirements.txt
bash scripts/prepare_output.sh
python scripts/extract_pdf_text.py "/ruta/al/cv.pdf" -o ../../../output/extracted.txt
python scripts/build_docx.py --json ../../../output/payload_v1.json --out ../../../output/perfil_v1_rrhh_corporativo.docx
python scripts/docx_to_pdf.py ../../../output/perfil_v1_rrhh_corporativo.docx -o ../../../output/perfil_rrhh_final.pdf
```

## Verificación local

1. Coloca un PDF de prueba en cualquier ruta (p. ej. la de ejemplo anterior).
2. Ejecuta el flujo del `SKILL.md`; comprueba que los archivos aparecen en `output/`.
3. Paso PDF: requiere LibreOffice o `--word`; sin ellos, `docx_to_pdf.py` falla con mensaje claro.
