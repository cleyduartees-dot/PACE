#!/bin/bash
# PACE - lanzador (Linux). Abre el menu de PACE.
if command -v pace >/dev/null 2>&1; then
  pace "$@"
else
  python3 -m pace.cli.pace "$@"
fi
