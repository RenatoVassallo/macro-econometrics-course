# Sesión 3: VAR estructurales. Identificación, IRF, FEVD y descomposición histórica

## Objetivos

1. Plantear el problema de identificación con precisión y contar cuántas restricciones hacen falta:
   los datos dan $\Sigma$, no $S$, y faltan $n(n-1)/2$ restricciones que no pueden salir de la
   muestra.
2. Identificación recursiva (Cholesky): ceros contemporáneos, qué supone el orden y exogeneidad de
   bloque para una economía pequeña y abierta.
3. Las tres lecturas de un VAR estructural, con las mismas matrices $\Theta_j = \Psi_j S$: la
   impulso-respuesta es un experimento, la descomposición de varianza es un promedio y la
   descomposición histórica es un relato.
4. Identificación por restricciones de signo: rotaciones $\tilde S = LQ$, aceptación y rechazo,
   identificación por conjunto y por qué la mediana del conjunto no es un modelo.

Todo es bayesiano: las bandas y los conjuntos salen de las extracciones de la posterior de la
sesión 2, no de un bootstrap.

## El sistema

Economía pequeña y abierta, Perú trimestral, 2002Q1 a 2019Q4 (metas de inflación, antes de la
pandemia), cuatro rezagos:

$$\mathbf{y}_t = (tot_t,\ y_t,\ \pi_t,\ i_t)'$$

ordenado de lo más exógeno a lo que reacciona más rápido, que es ya la primera decisión de
identificación.

| Código BCRP | Variable | Notación | Construcción |
|:-|:-|:-|:-|
| `PN38923BM` | términos de intercambio | $tot_t$ | promedio trimestral, var. % interanual |
| `PN02538AQ` | PBI real trimestral | $y_t$ | var. % interanual |
| `PN38705PM` | índice de precios al consumidor | $\pi_t$ | promedio trimestral, var. % interanual |
| `PN07819NM` | tasa interbancaria promedio | $i_t$ | promedio trimestral, en niveles |

## Notación

La del libro *Macroeconometría Aplicada con Python* (Vassallo, 2026), capítulo 4:
$\mathbf{u}_t = S\varepsilon_t$ con $\Sigma = SS'$, respuestas $\Theta_j = \Psi_j S$ con
$\Psi_j = JF^jJ'$, $L$ el factor de Cholesky de $\Sigma$ y $Q$ la matriz ortonormal que recorre el
conjunto identificado. El código de los notebooks está en inglés y el texto, en castellano.

## Material

Las láminas explican con sistemas pequeños; los notebooks aplican con uno más rico.

- **En las láminas**: un VAR(1) en $(\pi_t, i_t)'$ para la identificación recursiva, con IRF bajo
  cuatro estimadores (MCO, Minnesota, normal-Wishart y difusa), FEVD y descomposición histórica;
  y un VAR(2) en $(y_t, \pi_t, i_t)'$ para las restricciones de signo, paso a paso, desde el primer
  sorteo aceptado hasta la distribución final.
- `session3_A_identificacion.ipynb` (aplicación 1): el conteo de restricciones, la rotación que no
  cambia el ajuste, Cholesky a mano contra `MacroPy`, el efecto del orden, $\Theta_j$ programado
  con la forma companion, FEVD y descomposición histórica con su identidad contable, y exogeneidad
  de bloque con `b_exo`.
- `session3_B_signos.ipynb` (aplicación 2): el elipsoide de impactos admisibles, el algoritmo de
  aceptación y rechazo sobre las extracciones de la posterior, el conjunto identificado contra la
  respuesta recursiva, el esquema híbrido de ceros para el bloque externo más signos adentro, y la
  comprobación de Fry y Pagan.
- Los datos salen de la base del curso, `data/macro_peru.csv`, a través de `course_data.py`; los
  dos están en la raíz del repositorio.
- Las diapositivas se distribuyen aparte, por el Aula Virtual.

## Resultados que citan las láminas

Los del sistema bivariado y del de tres variables salen de `MacroPy` 0.2.0 con datos 2002Q1-2019Q4.

| | |
|:-|:-|
| VAR(1) en $(\pi, i)$: impacto del choque de política sobre la tasa | 0.44 pp con los cuatro estimadores |
| VAR(1) en $(\pi, i)$: inflación ante la política en $h = 4$ | MCO $+0.12$ pp; con los tres priors, entre $+0.06$ y $+0.07$ (*price puzzle*) |
| VAR(1) en $(\pi, i)$: FEVD a 8 trimestres | la política explica 3.7 % de la inflación y 71.5 % de la tasa |
| VAR(2) en $(y, \pi, i)$, signos: tasa de aceptación | 59 % |
| VAR(2) en $(y, \pi, i)$: PBI ante la política en $h = 4$ | Cholesky $-0.21$ (92 % de los modelos con PBI $< 0$); signos $+0.02$ (48 %) |

Y en los notebooks, con el sistema de cuatro variables:

| | |
|:-|:-|
| Restricciones necesarias ($n = 4$) | 6 |
| Impacto del choque de política sobre la inflación | 0.000 con el orden $(tot, y, \pi, i)$; 0.283 con el orden invertido |
| Respuesta del PBI en $h = 4$, recursiva | $-0.148$; 85 % de las extracciones con PBI $< 0$ |
| Respuesta del PBI en $h = 4$, signos | $+0.089$; 42 % de los modelos con PBI $< 0$ |
| Tasa de aceptación | 34 % con dos signos; 76 % con el esquema híbrido |

## Referencias

Sims (1980); Blanchard y Quah (1989); Faust (1998); Christiano, Eichenbaum y Evans (1999); Galí
(1999); Stock y Watson (2001); Canova y De Nicoló (2002); Uhlig (2005); Rubio-Ramírez, Waggoner y
Zha (2010); Fry y Pagan (2011); Baumeister y Hamilton (2015); Kilian y Lütkepohl (2017); Arias,
Rubio-Ramírez y Waggoner (2018); Vassallo (2026), *Macroeconometría Aplicada con Python*, cap. 4.
