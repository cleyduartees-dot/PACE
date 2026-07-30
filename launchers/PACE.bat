@echo off
REM ============================================================
REM  PACE - lanzador de doble clic.
REM  Haz doble clic en este archivo para abrir el menu de PACE.
REM  No necesitas escribir ningun comando.
REM ============================================================
title PACE
where pace >nul 2>nul
if %errorlevel%==0 (
  pace %*
) else (
  py -3 -m pace.cli.pace %*
)
echo.
echo (Puedes cerrar esta ventana)
pause >nul
