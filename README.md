# Macroeconometría Aplicada con Python

Notebooks y datos del curso; las diapositivas se distribuyen aparte. Los modelos se estiman con
[MacroPy](https://github.com/RenatoVassallo/MacroPy), la librería del curso.
El código está en inglés y el texto, en castellano.

## Sesiones

| | Tema | Material |
|:-|:-|:-|
| 1 | Del VAR clásico al BVAR; pronósticos incondicionales y condicionales | [`session1/`](session1/) |

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

### Opción B: en tu computadora, con `uv`

Es la vía moderna y la más rápida. Requiere [uv](https://docs.astral.sh/uv/)
instalado.

```bash
git clone https://github.com/RenatoVassallo/macro-econometrics-course.git
cd macro-econometrics-course
uv sync
```

`uv sync` crea el entorno en `.venv` con las versiones exactas de `uv.lock`, las
mismas para todos. En VS Code: `Ctrl+Shift+P` (`Cmd+Shift+P` en Mac) →
**Python: Select Interpreter** → el de `.venv`.

### Opción C: en tu computadora, con `venv` y `pip`

La vía clásica. Requiere **Python 3.11** instalado (no 3.12 ni 3.13: MacroPy
todavía no los soporta).

```bash
git clone https://github.com/RenatoVassallo/macro-econometrics-course.git
cd macro-econometrics-course
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

En Windows, las dos últimas líneas son:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Después, seleccionar el intérprete de `.venv` igual que en la opción B.

¿Primera vez con Python, VS Code y entornos virtuales? El paso a paso completo,
con capturas, está en
[Python + VS Code: a practical setup](https://renatovassallo.github.io/posts/python-vscode-practical-setup/).

## Comprobar que todo funciona

Cualquiera sea la opción elegida, esto lo confirma en dos segundos:

```bash
python check_setup.py
```

Revisa la versión de Python, los paquetes, MacroPy y la descarga de datos, y
dice exactamente qué falta si algo no está.

## Si algo falla

| Síntoma | Causa y solución |
|:-|:-|
| `ModuleNotFoundError: No module named 'MacroPy'` | El notebook está usando otro intérprete. Seleccionar el kernel de `.venv` (arriba a la derecha en VS Code). |
| `FileNotFoundError: data/peru_macrofiscal_bcrp.csv` | El kernel arrancó fuera de `session1/`. Abrir el notebook desde esa carpeta o ejecutar `import os; os.chdir("session1")`. |
| El instalador rechaza `macropy` | La versión de Python no es 3.11. Verificar con `python --version`. |
| Las series no se actualizan | La API del BCRP no respondió y se usó la copia local de `session1/data/`. El notebook lo avisa al cargar los datos; no es un error. |

## Datos

Las series vienen de la API del BCRP y se descargan al vuelo. Cada carpeta
guarda además una copia en `data/`, que se usa automáticamente si la API no
responde, de modo que los notebooks corren siempre, también sin internet.

## Referencia

Vassallo, R. (2026). *Macroeconometría Aplicada con Python*.
