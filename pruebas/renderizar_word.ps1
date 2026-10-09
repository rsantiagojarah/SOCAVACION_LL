param(
    [Parameter(Mandatory=$true)][string]$Entrada,
    [Parameter(Mandatory=$true)][string]$Salida
)
$ErrorActionPreference = 'Stop'
$rutaEntrada = (Resolve-Path -LiteralPath $Entrada).Path
$rutaSalida = [System.IO.Path]::GetFullPath($Salida)
$aplicacionWord = $null
$documento = $null
try {
    $aplicacionWord = New-Object -ComObject Word.Application
    $aplicacionWord.Visible = $false
    $aplicacionWord.DisplayAlerts = 0
    $aplicacionWord.AutomationSecurity = 3
    $documento = $aplicacionWord.Documents.Open($rutaEntrada, $false, $true, $false)
    $documento.ExportAsFixedFormat($rutaSalida, 17)
    Write-Output $rutaSalida
}
finally {
    if ($null -ne $documento) {
        $documento.Close(0)
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($documento)
    }
    if ($null -ne $aplicacionWord) {
        $aplicacionWord.Quit(0)
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($aplicacionWord)
    }
}
