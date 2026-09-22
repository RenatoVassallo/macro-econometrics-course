#!/usr/bin/env bash
# Prepara el entorno del curso de una sola vez.
#
#   bash setup_env.sh            # crea el entorno e instala todo   (~1 min)
#   bash setup_env.sh --force    # lo borra y lo vuelve a crear
#
# Funciona en macOS, Linux y Windows (desde Git Bash, que viene con Git para
# Windows). En PowerShell use setup_env.ps1.
#
# El entorno se crea en .venv, dentro de la carpeta del curso, que es donde
# VS Code lo encuentra solo. Si guarda el curso en OneDrive o Dropbox, un venv
# son decenas de miles de archivos pequenos: pongalo fuera con
#   VENV="$HOME/.venvs/macro-course" bash setup_env.sh

set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="${VENV:-$AQUI/.venv}"
KERNEL="macro-course"
FORCE=0
[ "${1:-}" = "--force" ] && FORCE=1

case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*) BIN="Scripts"; WINDOWS=1 ;;
  *)                    BIN="bin";     WINDOWS=0 ;;
esac

titulo() { printf '\n\033[1m%s\033[0m\n' "$1"; }
ok()     { printf '  \033[32mok\033[0m  %s\n' "$1"; }
aviso()  { printf '  \033[33m!!\033[0m  %s\n' "$1"; }
fatal()  { printf '\n\033[31mError:\033[0m %s\n\n' "$1" >&2; exit 1; }

# ---------------------------------------------------------------- 1. Python
titulo "1. Buscando Python 3.11"

version_ok() {   # 0 si el interprete existe y es 3.11
  "$@" -c 'import sys; sys.exit(0 if sys.version_info[:2] == (3, 11) else 1)' 2>/dev/null
}

PY=""
for cand in "python3.11" "python3" "python"; do
  if command -v "$cand" >/dev/null 2>&1 && version_ok "$cand"; then PY="$cand"; break; fi
done
if [ -z "$PY" ] && command -v py >/dev/null 2>&1 && version_ok py -3.11; then PY="py -3.11"; fi

if [ -z "$PY" ]; then
  encontrado="$(command -v python3 || command -v python || true)"
  if [ -n "$encontrado" ]; then
    aviso "encontré $("$encontrado" --version 2>&1), que no sirve"
  fi
  fatal "el curso necesita Python 3.11 (no 3.12 ni 3.13: MacroPy todavía no los soporta).
  Instálelo desde https://www.python.org/downloads/release/python-3119/
  y vuelva a ejecutar este script. Guía completa, con capturas:
  https://renatovassallo.github.io/posts/python-vscode-practical-setup/"
fi
ok "$($PY --version 2>&1) en $(command -v ${PY%% *})"

# ---------------------------------------------------------------- 2. Entorno
titulo "2. Creando el entorno en $VENV"
if [ -d "$VENV" ] && [ "$FORCE" = "1" ]; then
  rm -rf "$VENV"; ok "entorno anterior borrado (--force)"
fi
if [ -x "$VENV/$BIN/python" ] || [ -x "$VENV/$BIN/python.exe" ]; then
  ok "ya existía, lo reutilizo"
else
  $PY -m venv "$VENV" || fatal "no se pudo crear el entorno virtual en $VENV"
  ok "creado"
fi
VPY="$VENV/$BIN/python"
[ -x "$VPY" ] || VPY="$VENV/$BIN/python.exe"
[ -x "$VPY" ] || fatal "el entorno quedó incompleto; pruebe de nuevo con --force"

# ---------------------------------------------------------------- 3. Paquetes
titulo "3. Instalando los paquetes del curso"
"$VPY" -m pip install --quiet --upgrade pip
if ! "$VPY" -m pip install --quiet -r "$AQUI/requirements.txt"; then
  fatal "falló la instalación. Si está detrás de un proxy o sin internet,
  vuelva a intentarlo; si el error menciona 'macropy', revise su versión de Python."
fi
ok "$("$VPY" -m pip list 2>/dev/null | wc -l | tr -d ' ') paquetes instalados"

# ---------------------------------------------------------------- 4. Kernel
titulo "4. Registrando el kernel de Jupyter"
"$VPY" -m ipykernel install --user --name "$KERNEL" \
       --display-name "Python 3.11 (curso macro)" >/dev/null 2>&1 \
  && ok "disponible como \"Python 3.11 (curso macro)\"" \
  || aviso "no se pudo registrar el kernel; en VS Code igual puede elegir el intérprete de .venv"

# ---------------------------------------------------------------- 5. Prueba
titulo "5. Comprobando que todo funciona"
"$VPY" "$AQUI/check_setup.py" || fatal "la comprobación falló; revise los puntos marcados con [!!]"

titulo "Listo"
if [ "$WINDOWS" = "1" ]; then
  echo "  Para trabajar desde la terminal:  source .venv/Scripts/activate"
else
  echo "  Para trabajar desde la terminal:  source .venv/bin/activate"
fi
echo "  En VS Code: Ctrl+Shift+P -> Python: Select Interpreter -> el de .venv"
echo "  Y abra session1/session1_A_var_bvar.ipynb"
echo
