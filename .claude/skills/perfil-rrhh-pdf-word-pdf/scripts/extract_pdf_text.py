#!/usr/bin/env python3
"""Extract text from a PDF (selectable text). Prints to stdout or writes to -o file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pdfplumber


def extract(pdf_path: Path) -> str:
    parts: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            parts.append(f"--- Página {i} ---\n{text.strip()}")
    return "\n\n".join(parts).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Extrae texto de un PDF.")
    parser.add_argument("pdf", type=Path, help="Ruta al archivo .pdf")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Archivo de salida .txt (si no se indica, usa stdout)",
    )
    args = parser.parse_args()
    if not args.pdf.is_file():
        print(f"Error: no existe el archivo: {args.pdf}", file=sys.stderr)
        return 1
    try:
        text = extract(args.pdf)
    except Exception as e:
        print(f"Error al leer PDF: {e}", file=sys.stderr)
        return 1
    if not text:
        print(
            "Advertencia: no se extrajo texto. Puede ser un PDF escaneado; "
            "considera OCR (ver reference.md del skill).",
            file=sys.stderr,
        )
    if args.output:
        args.output.write_text(text, encoding="utf-8")
        print(f"Escrito: {args.output} ({len(text)} caracteres)", file=sys.stderr)
    else:
        sys.stdout.write(text + ("\n" if text else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
