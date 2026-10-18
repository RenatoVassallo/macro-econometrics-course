"""Comprueba que el entorno del curso está listo.

Uso:  python check_setup.py        (con uv: uv run python check_setup.py)

Si se ejecuta con un Python que no tiene los paquetes del curso (por ejemplo, una
terminal abierta antes de `uv sync`) y el entorno del curso existe, se vuelve a
ejecutar con ese entorno y explica cómo activarlo en la terminal.
"""
import importlib
import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIRED = ["numpy", "pandas", "scipy", "matplotlib", "statsmodels", "tqdm", "plotly", "MacroPy"]
MACROPY_MIN = (0, 3, 2)
OK, BAD = "  [ok] ", "  [!!] "
RELAUNCHED = "CHECK_SETUP_RELAUNCHED"      # evita relanzar más de una vez


def course_env():
    """Carpeta e intérprete del entorno del curso, si existe y no es el actual."""
    for env in filter(None, [os.environ.get("UV_PROJECT_ENVIRONMENT"), ROOT / ".venv"]):
        env = Path(env) if Path(env).is_absolute() else ROOT / env
        if Path(sys.prefix).resolve() == env.resolve():
            return None                       # ya estamos en él
        for exe in (env / "bin" / "python", env / "Scripts" / "python.exe"):
            if exe.exists():
                return env, exe
    return None


def relaunch():
    """Vuelve a ejecutar el chequeo con el entorno del curso cuando el Python
    actual no tiene MacroPy. Devuelve el código de salida, o None si no hace falta."""
    if os.environ.get(RELAUNCHED) or importlib.util.find_spec("MacroPy") is not None:
        return None
    found = course_env()
    if found is None:
        return None
    env, exe = found
    try:
        shown = env.relative_to(Path.cwd())
    except ValueError:
        shown = env
    activate = (f"{shown}\\Scripts\\Activate.ps1" if os.name == "nt"
                else f"source {shown}/bin/activate")
    print(f"\nEsta terminal usa {sys.executable}, que no tiene los paquetes del curso.\n"
          f"Compruebo con el entorno del curso ({shown}). Para que la terminal lo use:\n"
          f"    {activate}\n"
          "o abra una terminal nueva en VS Code (o Developer: Reload Window).", flush=True)
    code = subprocess.call([str(exe), str(ROOT / "check_setup.py")],
                           env={**os.environ, RELAUNCHED: "1"})
    print(f"Recuerde: esta terminal sigue sin el entorno; actívelo con {activate}\n")
    return code


def check_python():
    v = sys.version_info
    print(f"Python {v.major}.{v.minor}.{v.micro}  ({sys.executable})")
    if (v.major, v.minor) != (3, 11):
        print(BAD + "el curso necesita Python 3.11; MacroPy no instala en otras versiones")
        return False
    print(OK + "versión correcta")
    return True


def check_packages():
    ok = True
    for name in REQUIRED:
        try:
            mod = importlib.import_module(name)
        except ImportError:
            print(BAD + f"falta {name}")
            ok = False
            continue
        print(OK + f"{name} {getattr(mod, '__version__', '')}".rstrip())
    return ok


def check_macropy():
    minimo = ".".join(map(str, MACROPY_MIN))
    try:
        import MacroPy
    except ImportError:
        return False                       # check_packages ya lo reportó
    m = re.match(r"(\d+)\.(\d+)\.(\d+)", MacroPy.__version__)
    if m is None or tuple(map(int, m.groups())) < MACROPY_MIN:
        print(BAD + f"MacroPy {MacroPy.__version__} es anterior a {minimo}: vuelva a ejecutar "
              "bash setup_env.sh (o uv sync)")
        return False
    try:
        from MacroPy import BayesianVAR, ClassicVAR, set_style  # noqa: F401
    except ImportError as err:
        print(BAD + f"MacroPy está incompleto: {err}")
        return False
    print(OK + f"MacroPy {MacroPy.__version__} expone BayesianVAR, ClassicVAR y set_style")
    return True


def check_data():
    sys.path.insert(0, str(ROOT))
    try:
        from course_data import load, vintage, SERIES
        df = load()
    except Exception as err:
        print(BAD + f"no se pudo leer la base del curso: {err}")
        return False
    faltan = sorted(set(SERIES) - set(df.columns))
    if faltan:
        print(BAD + f"a la base le faltan series: {', '.join(faltan)}")
        return False
    print(OK + f"base del curso: {df.shape[1]} series, descargada el {vintage()}")
    return True


def main():
    print("\nEntorno del curso de macroeconometría aplicada\n" + "-" * 46)
    results = [check_python(), check_packages(), check_macropy(), check_data()]
    print("-" * 46)
    if all(results):
        print("Todo listo. Abre session1/session1_var.ipynb\n")
        return 0
    print("Revisa los puntos marcados con [!!] y la sección "
          "'Si algo falla' del README.\n")
    return 1


if __name__ == "__main__":
    code = relaunch()
    raise SystemExit(main() if code is None else code)
