# Sesión 1: presentación del curso y el modelo VAR

## Objetivos

1. Representación del VAR: forma compacta $Y = XB + U$ y forma companion, estabilidad y raíces
   unitarias.
2. Estimación: mínimos cuadrados (MCO) y máxima verosimilitud coinciden con errores normales, y la
   verosimilitud da además toda la superficie.
3. Pronóstico recursivo: la media se obtiene iterando la companion y la banda se abre porque el ECM
   se acumula con el horizonte.

Antes, la presentación del curso y la preparación del entorno.

## Notación

La del libro *Macroeconometría Aplicada con Python* (Vassallo, 2026), capítulo 3:
$\mathbf{y}_t = c + \Phi_1\mathbf{y}_{t-1} + \Phi_2\mathbf{y}_{t-2} + \mathbf{u}_t$, forma compacta
$Y = XB + U$ con la constante en la primera fila de $B$, forma companion
$\tilde{\mathbf y}_t = \tilde c + F\tilde{\mathbf y}_{t-1} + \tilde{\mathbf u}_t$ y $\Psi_j = JF^jJ'$.
El código de los notebooks está en inglés y el texto, en castellano.

## Material

- `session1_var.ipynb` (aplicación 1): VAR(2) bivariado en precios de exportación ($x_t$) e ingresos
  fiscales ($r_t$), 2002Q2 a 2017Q4. Matrices $Y$ y $X$ a mano, MCO contra máxima verosimilitud,
  forma companion y estabilidad, y pronóstico de ocho trimestres con la banda del ECM, contrastado
  con lo que pasó en 2018-2019.
- Los datos salen de la base del curso, `data/macro_peru.csv`, a través de `course_data.py`; los
  dos están en la raíz del repositorio.
- Las diapositivas se distribuyen aparte, por el Aula Virtual.

Los notebooks usan rutas relativas, así que hay que ejecutarlos desde esta carpeta. En VS Code eso ya
viene configurado; desde la terminal, `cd session1` antes de abrir Jupyter.

## Series utilizadas

De la base del curso; el detalle de cada una está en `data/diccionario.csv`.

| Código BCRP | Variable | Notación | Construcción |
|:-|:-|:-|:-|
| `PN38915BM` | índice de precios de exportación | $x_t$ | promedio trimestral, var. % interanual |
| `PN38689FM` | ingresos corrientes del gobierno central (términos reales) | $r_t$ | promedio trimestral, var. % interanual |

## Referencias

Sims (1980); Sims, Stock y Watson (1990); Hamilton (1994); Lütkepohl (2005); Kilian y Lütkepohl
(2017); Vassallo (2026), *Macroeconometría Aplicada con Python*, cap. 3.
