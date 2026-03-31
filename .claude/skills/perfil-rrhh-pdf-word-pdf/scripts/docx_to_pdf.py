#!/usr/bin/env python3
"""Convert .docx to PDF using mammoth+weasyprint (pure Python), LibreOffice, or docx2pdf."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def convert_python(docx: Path, pdf_out: Path) -> bool:
    """Pure-Python conversion: mammoth (docx→HTML) + weasyprint (HTML→PDF)."""
    try:
        import mammoth
        from weasyprint import HTML
    except ImportError:
        return False
    pdf_out.parent.mkdir(parents=True, exist_ok=True)
    try:
        with docx.open("rb") as f:
            result = mammoth.convert_to_html(f)
        html = f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>body{{font-family:Calibri,sans-serif;font-size:11pt;margin:2cm 2.5cm;line-height:1.4}}h1{{font-size:16pt}}h2{{font-size:13pt}}p{{margin:0 0 6pt}}</style></head><body>{result.value}</body></html>"
        HTML(string=html).write_pdf(str(pdf_out))
        return pdf_out.is_file()
    except Exception:
        return False


def find_soffice() -> str | None:
    candidates = [
        os.environ.get("LIBREOFFICE_PATH"),
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/usr/bin/soffice",
        "/usr/local/bin/soffice",
        shutil.which("soffice"),
    ]
    for c in candidates:
        if c and Path(c).is_file():
            return c
    return None


def convert_libreoffice(docx: Path, pdf_out: Path) -> bool:
    soffice = find_soffice()
    if not soffice:
        return False
    out_dir = pdf_out.parent.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    # LibreOffice names output based on input basename
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        tmp_docx = tmp / docx.name
        tmp_docx.write_bytes(docx.read_bytes())
        cmd = [
            soffice,
            "--headless",
            "--nologo",
            "--nofirststartwizard",
            "--convert-to",
            "pdf",
            "--outdir",
            str(tmp),
            str(tmp_docx),
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False
        produced = tmp / (tmp_docx.stem + ".pdf")
        if produced.is_file():
            pdf_out.write_bytes(produced.read_bytes())
            return True
    return False


def convert_docx2pdf(docx: Path, pdf_out: Path) -> bool:
    try:
        from docx2pdf import convert
    except ImportError:
        return False
    pdf_out.parent.mkdir(parents=True, exist_ok=True)
    try:
        convert(str(docx), str(pdf_out))
        return pdf_out.is_file()
    except Exception:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Convierte .docx a PDF.")
    parser.add_argument("docx", type=Path, help="Archivo .docx de entrada")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Ruta del PDF de salida (por defecto: mismo nombre que .docx con .pdf)",
    )
    parser.add_argument(
        "--word",
        action="store_true",
        help="Forzar docx2pdf (Microsoft Word) en lugar de LibreOffice",
    )
    args = parser.parse_args()
    if not args.docx.is_file():
        print(f"Error: no existe: {args.docx}", file=sys.stderr)
        return 1
    out = args.output or args.docx.with_suffix(".pdf")

    if args.word:
        ok = convert_docx2pdf(args.docx, out)
        if not ok:
            print(
                "Error: docx2pdf falló. ¿Tienes Microsoft Word instalado? "
                "Prueba sin --word para usar mammoth+weasyprint.",
                file=sys.stderr,
            )
            return 1
        print(f"PDF (Word): {out}", file=sys.stderr)
        return 0

    if convert_python(args.docx, out):
        print(f"PDF (mammoth+weasyprint): {out}", file=sys.stderr)
        return 0

    if convert_libreoffice(args.docx, out):
        print(f"PDF (LibreOffice): {out}", file=sys.stderr)
        return 0

    print(
        "Error: no se pudo convertir a PDF.\n"
        "Instala las dependencias Python: pip install mammoth weasyprint\n"
        "O instala LibreOffice: brew install --cask libreoffice\n"
        "O usa Microsoft Word: python scripts/docx_to_pdf.py archivo.docx --word -o salida.pdf",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
