' Un solo pythonw de ventana. El redirector de .venv abre y cierra otra pestaña.
Option Explicit

Dim sistema, shell, carpeta, cfg, venvPythonw, basePythonw, script, comando, codigo

Set sistema = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
carpeta = sistema.GetParentFolderName(WScript.ScriptFullName)
cfg = carpeta & "\.venv\pyvenv.cfg"
venvPythonw = carpeta & "\.venv\Scripts\pythonw.exe"
script = carpeta & "\iniciar_interfaz.py"
basePythonw = ResolverPythonw(cfg)

If basePythonw = "" Or Not sistema.FileExists(basePythonw) Or Not sistema.FileExists(script) Then
    MsgBox "Falta el entorno local. Consulta LEEME.md para prepararlo.", vbCritical, "Socavacion LL"
    WScript.Quit 1
End If

shell.Environment("PROCESS")("__PYVENV_LAUNCHER__") = venvPythonw
shell.CurrentDirectory = carpeta
comando = """" & basePythonw & """ """ & script & """"
codigo = shell.Run(comando, 1, True)

If codigo <> 0 Then
    MsgBox "No se pudo iniciar la interfaz. Consulta LEEME.md.", vbCritical, "Socavacion LL"
    WScript.Quit codigo
End If

Function ResolverPythonw(rutaCfg)
    Dim archivo, linea, partes, inicio
    ResolverPythonw = ""
    If Not sistema.FileExists(rutaCfg) Then Exit Function
    Set archivo = sistema.OpenTextFile(rutaCfg, 1, False)
    Do Until archivo.AtEndOfStream
        linea = Trim(archivo.ReadLine)
        If InStr(linea, "=") > 0 Then
            partes = Split(linea, "=", 2)
            If LCase(Trim(partes(0))) = "home" Then
                inicio = Trim(partes(1))
                If Len(inicio) > 0 Then
                    If Right(inicio, 1) = "\" Then
                        ResolverPythonw = inicio & "pythonw.exe"
                    Else
                        ResolverPythonw = inicio & "\pythonw.exe"
                    End If
                End If
                Exit Do
            End If
        End If
    Loop
    archivo.Close
End Function
