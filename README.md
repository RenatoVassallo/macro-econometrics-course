# Macroeconometría Aplicada con Python

Notebooks y datos del curso; las diapositivas se distribuyen aparte. Los modelos se estiman con
[MacroPy](https://github.com/RenatoVassallo/MacroPy), la librería del curso.
El código está en inglés y el texto, en castellano.

## Sesiones

| | Tema | Material |
|:-|:-|:-|
| 1 | Presentación del curso y el modelo VAR: representación, estimación y pronóstico | [`session1/`](session1/) |
| 2 | VAR bayesianos: prior de Minnesota, Gibbs, *fan charts*, escenarios y la pandemia | [`session2/`](session2/) |
| 3 | VAR estructurales: identificación por ceros y por signos, IRF, FEVD y descomposición histórica | [`session3/`](session3/) |
| 4 | VAR no lineales: Threshold VAR y TVP-VAR con volatilidad estocástica | próximamente |
| 5 | Componentes no observados: tendencia, ciclo y brecha del producto | próximamente |

## Cómo empezar

### Opción A: en el navegador, sin instalar nada

Ideal para la primera clase. Se abre un entorno ya configurado en GitHub; solo
hace falta una cuenta.

[![Abrir en GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/RenatoVassallo/macro-econometrics-course?quickstart=1)

1. Clic en el botón. La primera vez tarda entre uno y dos minutos: se instala
   todo solo.
2. Cuando abra el editor, ir a `session1/` y abrir el primer notebook.
3. Ejecutar la primera celda. Si pregunta por el kernel, elegir **Python 3.11**
   (`/usr/local/bin/python`).

El plan gratuito de GitHub incluye 120 horas-núcleo al mes, es decir 60 horas en
la máquina de 2 núcleos: de sobra para el curso. El codespace se apaga solo tras
30 minutos de inactividad y se retoma después desde el mismo botón, con tu
trabajo intacto.

Lo que edites vive en el codespace, no en tu computadora. Para conservar los
cambios: `File → Download` sobre el notebook, o `git commit` y `git push` si
trabajas sobre tu propio fork.

### Opción B: en tu computadora, con un solo comando

Necesitas tres cosas instaladas: **Python 3.11** (no 3.12 ni 3.13: MacroPy
todavía no los soporta), **VS Code** y **git**. El paso a paso, con capturas,
está en
[Python + VS Code: a practical setup](https://renatovassallo.github.io/posts/python-vscode-practical-setup/).

Después, clona el repositorio y ejecuta el script de instalación: crea el
entorno, instala los paquetes, registra el kernel de Jupyter y comprueba que
todo funciona.

```bash
git clone https://github.com/RenatoVassallo/macro-econometrics-course.git
cd macro-econometrics-course
bash setup_env.sh
```

En Windows con PowerShell, la última línea es `.\setup_env.ps1`. Si Windows se
niega a ejecutarlo, primero:
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`. Desde Git Bash
funciona `bash setup_env.sh` igual que en Mac.

Si te falta Python 3.11, el script te lo dice y te da el enlace de descarga.
Para reinstalar desde cero: `bash setup_env.sh --force`.

Después, en VS Code: `Ctrl+Shift+P` (`Cmd+Shift+P` en Mac) →
**Python: Select Interpreter** → el de `.venv`.

> Si guardas el curso en OneDrive o Dropbox, pon el entorno fuera de la carpeta
> sincronizada: un entorno son decenas de miles de archivos pequeños.
> `VENV="$HOME/.venvs/macro-course" bash setup_env.sh`

### Opción C: en tu computadora, con `uv`

Si ya usas [uv](https://docs.astral.sh/uv/), esta es la vía más rápida:

```bash
git clone https://github.com/RenatoVassallo/macro-econometrics-course.git
cd macro-econometrics-course
uv sync
```

## Comprobar que todo funciona

Cualquiera sea la opción elegida, esto lo confirma en dos segundos:

```bash
python check_setup.py
```

Revisa la versión de Python, los paquetes, MacroPy y la base de datos del
curso, y dice exactamente qué falta si algo no está.

## Si algo falla

| Síntoma | Causa y solución |
|:-|:-|
| `ModuleNotFoundError: No module named 'MacroPy'` | El notebook está usando otro intérprete. Seleccionar el kernel de `.venv` (arriba a la derecha en VS Code). |
| `ModuleNotFoundError: No module named 'course_data'` | El kernel arrancó fuera de la carpeta de la sesión. Abrir el notebook desde ella; desde la terminal, `cd session1` antes de abrir Jupyter. |
| El instalador rechaza `macropy` | La versión de Python no es 3.11. Verificar con `python --version`. |
| Mis números no coinciden con las diapositivas | Se usó `load(refresh=True)`, que trae los datos de hoy con las revisiones del BCRP. Con `load()` se vuelve a la copia congelada. |

## Datos

Todo el curso usa una sola base, [`data/macro_peru.csv`](data/macro_peru.csv):
14 series trimestrales de Perú y de Estados Unidos, del BCRP y de FRED, en
niveles. Es una copia congelada, así que todos reproducen exactamente los números
de las diapositivas, con o sin internet. El código, la unidad, la fuente y la
fecha de descarga de cada serie están en
[`data/diccionario.csv`](data/diccionario.csv).

Los notebooks la leen con `course_data.py`, que está en la raíz:

```python
import sys; sys.path.append("..")     # desde la carpeta de una sesión
from course_data import load, yoy

df = load()                           # niveles trimestrales, todas las series
g = yoy(df[["pbi", "ipc"]])           # variación % interanual
```

Para trabajar con los datos más recientes, `load(refresh=True)` los descarga de
las APIs sin tocar la copia congelada. Ninguna de las dos fuentes pide clave.

## Referencia

Vassallo, R. (2026).
[*Macroeconometría Aplicada con Python*](https://renatovassallo.github.io/MacroeconometricsBook/).
Las diapositivas citan capítulo y sección del libro donde cada concepto se
desarrolla; el libro se lee gratis en línea.
