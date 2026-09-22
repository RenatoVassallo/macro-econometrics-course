# Prepara el entorno del curso de una sola vez, en Windows con PowerShell.
#
#   .\setup_env.ps1              # crea el entorno e instala todo
#   .\setup_env.ps1 -Force       # lo borra y lo vuelve a crear
#
# Si Windows se niega a ejecutar el script, abra PowerShell y escriba primero:
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#
# El entorno se crea en .venv, dentro de la carpeta del curso, que es donde
# VS Code lo encuentra solo. Si guarda el curso en OneDrive, pongalo fuera:
#   $env:VENV = "$HOME\.venvs\macro-course"; .\setup_env.ps1

param([switch]$Force)

$ErrorActionPreference = "Stop"
$Aqui   = Split-Path -Parent $MyInvocation.MyCommand.Definition
$Venv   = if ($env:VENV) { $env:VENV } else { Join-Path $Aqui ".venv" }
$Kernel = "macro-course"

function Titulo($t) { Write-Host "`n$t" -ForegroundColor White }
function Ok($t)     { Write-Host "  ok  $t" -ForegroundColor Green }
function Aviso($t)  { Write-Host "  !!  $t" -ForegroundColor Yellow }
function Fatal($t)  { Write-Host "`nError: $t`n" -ForegroundColor Red; exit 1 }

function Es311($exe, $args) {
    try {
        & $exe @args -c "import sys; sys.exit(0 if sys.version_info[:2]==(3,11) else 1)" 2>$null
        return ($LASTEXITCODE -eq 0)
    } catch { return $false }
}

# ---------------------------------------------------------------- 1. Python
Titulo "1. Buscando Python 3.11"
$Py = $null; $PyArgs = @()
if (Es311 "py" @("-3.11"))      { $Py = "py";          $PyArgs = @("-3.11") }
elseif (Es311 "python3.11" @()) { $Py = "python3.11" }
elseif (Es311 "python" @())     { $Py = "python" }

if (-not $Py) {
    Fatal @"
el curso necesita Python 3.11 (no 3.12 ni 3.13: MacroPy todavía no los soporta).
  Instálelo desde https://www.python.org/downloads/release/python-3119/
  marcando "Add python.exe to PATH", y vuelva a ejecutar este script.
  Guía completa, con capturas:
  https://renatovassallo.github.io/posts/python-vscode-practical-setup/
"@
}
Ok ((& $Py @PyArgs --version) 2>&1)

# ---------------------------------------------------------------- 2. Entorno
Titulo "2. Creando el entorno en $Venv"
if ((Test-Path $Venv) -and $Force) { Remove-Item -Recurse -Force $Venv; Ok "entorno anterior borrado (-Force)" }
$VPy = Join-Path $Venv "Scripts\python.exe"
if (Test-Path $VPy) {
    Ok "ya existía, lo reutilizo"
} else {
    & $Py @PyArgs -m venv $Venv
    if ($LASTEXITCODE -ne 0) { Fatal "no se pudo crear el entorno virtual en $Venv" }
    Ok "creado"
}
if (-not (Test-Path $VPy)) { Fatal "el entorno quedó incompleto; pruebe de nuevo con -Force" }

# ---------------------------------------------------------------- 3. Paquetes
Titulo "3. Instalando los paquetes del curso"
& $VPy -m pip install --quiet --upgrade pip
& $VPy -m pip install --quiet -r (Join-Path $Aqui "requirements.txt")
if ($LASTEXITCODE -ne 0) {
    Fatal "falló la instalación. Si está detrás de un proxy o sin internet, vuelva a intentarlo."
}
Ok "paquetes instalados"

# ---------------------------------------------------------------- 4. Kernel
Titulo "4. Registrando el kernel de Jupyter"
& $VPy -m ipykernel install --user --name $Kernel --display-name "Python 3.11 (curso macro)" *> $null
if ($LASTEXITCODE -eq 0) { Ok 'disponible como "Python 3.11 (curso macro)"' }
else { Aviso "no se pudo registrar el kernel; en VS Code igual puede elegir el intérprete de .venv" }

# ---------------------------------------------------------------- 5. Prueba
Titulo "5. Comprobando que todo funciona"
& $VPy (Join-Path $Aqui "check_setup.py")
if ($LASTEXITCODE -ne 0) { Fatal "la comprobación falló; revise los puntos marcados con [!!]" }

Titulo "Listo"
Write-Host "  Para trabajar desde la terminal:  .\.venv\Scripts\Activate.ps1"
Write-Host "  En VS Code: Ctrl+Shift+P -> Python: Select Interpreter -> el de .venv"
Write-Host "  Y abra session1\session1_A_var_bvar.ipynb`n"
