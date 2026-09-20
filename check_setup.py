"""Comprueba que el entorno del curso está listo.

Uso:  python check_setup.py
"""
import importlib
import sys
from pathlib import Path

REQUIRED = ["numpy", "pandas", "scipy", "matplotlib", "statsmodels", "tqdm", "MacroPy"]
OK, BAD = "  [ok] ", "  [!!] "


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
    try:
        from MacroPy import BayesianVAR, ClassicVAR  # noqa: F401
    except ImportError as err:
        print(BAD + f"MacroPy está incompleto: {err}")
        return False
    print(OK + "MacroPy expone BayesianVAR y ClassicVAR")
    return True


def check_data():
    session = Path(__file__).parent / "session1"
    sys.path.insert(0, str(session))
    try:
        from macrofiscal_data import load_levels, yoy_growth
        levels, source = load_levels(session / "data" / "peru_macrofiscal_bcrp.csv")
        growth = yoy_growth(levels)
    except Exception as err:
        print(BAD + f"no se pudieron cargar los datos: {err}")
        return False
    print(OK + f"datos cargados desde {source.split('(')[0].strip()}, "
          f"{len(growth)} trimestres hasta {growth.index[-1].date()}")
    return True


def main():
    print("\nEntorno del curso de macroeconometría aplicada\n" + "-" * 46)
    results = [check_python(), check_packages(), check_macropy(), check_data()]
    print("-" * 46)
    if all(results):
        print("Todo listo. Abre session1/session1_A_var_bvar.ipynb\n")
        return 0
    print("Revisa los puntos marcados con [!!] y la sección "
          "'Si algo falla' del README.\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
