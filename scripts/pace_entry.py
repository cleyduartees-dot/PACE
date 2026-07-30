"""PyInstaller entry point for the standalone `pace` binary.

Build a single-file executable that needs no Python installed:

    pip install pyinstaller
    pyinstaller --onefile --name pace \
        --add-data "pace/contracts;pace/contracts" \
        --add-data "pace/templates;pace/templates" \
        scripts/pace_entry.py

On macOS/Linux replace the ';' in --add-data with ':'. The result is in
dist/ (pace.exe on Windows). Double-clicking it with no arguments opens
the guided menu.
"""
import sys

from pace.cli.pace import main

if __name__ == "__main__":
    sys.exit(main())
