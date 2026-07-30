# Compilar el binario standalone de PACE (sin Python)

Objetivo: un ejecutable único (`pace.exe` en Windows) que cualquiera pueda
usar sin instalar Python. Es el paso que, junto con el lanzador de doble
clic (`launchers/`), vuelve PACE usable por no técnicos.

> Importante: PyInstaller **no** compila entre sistemas. Para obtener un
> `.exe` de Windows hay que compilarlo **en Windows**; para macOS, en macOS.

## Windows (PowerShell), desde la raíz del repo

```powershell
py -3.12 -m pip install pyinstaller
py -3.12 -m PyInstaller --onefile --name pace `
    --add-data "pace/contracts;pace/contracts" `
    --add-data "pace/templates;pace/templates" `
    scripts/pace_entry.py
```

El ejecutable queda en `dist\pace.exe`. Pruébalo:

```powershell
.\dist\pace.exe --help
.\dist\pace.exe            REM abre el menu guiado
```

## macOS / Linux

Igual, pero cambia el `;` de `--add-data` por `:`:

```bash
pip install pyinstaller
pyinstaller --onefile --name pace \
    --add-data "pace/contracts:pace/contracts" \
    --add-data "pace/templates:pace/templates" \
    scripts/pace_entry.py
```

## Verificar

Tras compilar, confirma que el binario encuentra sus datos:

```
pace doctor --deep .     # sobre una instancia .pace existente
pace create --guided     # crea un proyecto nuevo, pregunta la ruta
```

Si el binario funciona, puedes ponerlo junto al lanzador de doble clic
para una experiencia totalmente sin terminal ni Python.
