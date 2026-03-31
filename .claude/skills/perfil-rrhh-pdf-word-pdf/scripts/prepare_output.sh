#!/usr/bin/env bash
# Vacía output/ en la raíz del repo y crea la carpeta.
# Repo = carpeta que contiene .claude/skills/ (tres niveles arriba desde el directorio del skill).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$SKILL_DIR/../../.." && pwd)"
OUT="$REPO_ROOT/output"
mkdir -p "$OUT"
rm -rf "${OUT:?}/"*
echo "$OUT"
