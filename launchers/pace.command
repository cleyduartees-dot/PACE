#!/bin/bash
# PACE - doble clic (macOS). Abre el menu de PACE.
cd "$(dirname "$0")"
if command -v pace >/dev/null 2>&1; then
  pace "$@"
else
  python3 -m pace.cli.pace "$@"
fi
echo
read -n 1 -s -r -p "Pulsa una tecla para cerrar..."
