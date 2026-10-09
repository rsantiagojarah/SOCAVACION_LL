@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Falta el entorno local. Consulta LEEME.md para prepararlo.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" iniciar_interfaz.py
if errorlevel 1 (
    echo No se pudo iniciar la interfaz. Revisa el mensaje anterior y LEEME.md.
    pause
    exit /b 1
)
