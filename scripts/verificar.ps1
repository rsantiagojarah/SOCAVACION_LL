# Ejecuta pruebas, cobertura de ramas, análisis, tipos y auditoría; falla si falta una herramienta.
param([string]$Python = (Join-Path $PSScriptRoot '../.venv/Scripts/python.exe'))
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    Write-Error 'Falta Python local. Crear .venv e instalar .[desarrollo] antes de verificar.'
    exit 1
}
& $Python (Join-Path $PSScriptRoot 'calidad.py')
exit $LASTEXITCODE
