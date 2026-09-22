# Sesión 1: modelos VAR bayesianos. Estimación, pronóstico y escenarios

## Objetivos

1. Representación del VAR: forma compacta, companion y vectorizada, estabilidad, y la equivalencia
   entre mínimos cuadrados (MCO) y máxima verosimilitud.
2. Del prior a la posterior: prior de Minnesota para los coeficientes, inversa-Wishart para la
   covarianza y el muestreador de Gibbs.
3. La densidad predictiva bayesiana: no hay fórmula cerrada sino trayectorias simuladas, un choque
   nuevo por trimestre, y un *fan chart* cuyas bandas son percentiles de esas trayectorias
   (10, 30, 50, 70 y 90 %).
4. Pronósticos condicionales (Waggoner y Zha, 1999): imponer una senda y recuperar las demás.
   Condicionar es proyectar.
5. La pandemia: qué le hacen 2020 y 2021 a la persistencia y a $\Sigma$, y tres tratamientos
   (descartar, dummies con prior y escalamiento de volatilidad de Lenza y Primiceri, 2022).

Duración: unas 3 horas y 40 minutos. La exogeneidad de bloque y la identificación estructural quedan
para la sesión 2.

## Notación

La del libro *Macroeconometría Aplicada con Python* (Vassallo, 2026):
$\mathbf{y}_t = c + \Phi_1\mathbf{y}_{t-1} + \Phi_2\mathbf{y}_{t-2} + \mathbf{u}_t$, forma compacta
$Y = XB + U$ con la constante en la primera fila de $B$, $b = \operatorname{vec}(B)$,
$b \sim N(b_0, H)$, $\Sigma \sim \mathcal{IW}(S_0, \nu_0)$ y $\mathbf{u}_t = S\varepsilon_t$. Las variables
son el crecimiento interanual de los precios de exportación ($x_t$), del PBI ($y_t$) y de los ingresos
fiscales ($r_t$); $p$ es el número de rezagos. El código de los notebooks está en inglés y el texto, en
castellano.

## Material

- `session1_A_var_bvar.ipynb` (aplicación 1): VAR(2) bivariado en $x_t$ y $r_t$, 2002Q2 a
  2017Q4. Matrices a mano, MCO igual a máxima verosimilitud, $b_0$ y $H$ del prior de Minnesota,
  muestreador de Gibbs programado a mano y contraste con `MacroPy`.
- `session1_B_forecasting.ipynb` (aplicación 2): modelo macrofiscal en $(x_t, y_t, r_t)'$. Densidad
  predictiva a mano contra `MacroPy`, pronóstico 2018-2019 contra lo observado, la matriz $A$ de
  Waggoner y Zha armada a mano y verificada contra `MacroPy`, y dos escenarios de precios de
  exportación.
- `session1_C_pandemia.ipynb` (aplicación 3): muestra completa. Qué le hace la pandemia a la
  persistencia y a la volatilidad, tres tratamientos comparados, tres *fan charts* lado a lado y la
  respuesta al impulso bajo cada tratamiento.
- `macrofiscal_data.py`: descarga las series de la API del BCRP y actualiza el respaldo local.
- Las diapositivas (beamer) se distribuyen aparte. Las figuras salen de los notebooks.
- `data/peru_macrofiscal_bcrp.csv`: niveles trimestrales de respaldo, que se usan automáticamente si
  la API del BCRP no responde.

Los notebooks usan rutas relativas, así que hay que ejecutarlos desde esta carpeta. En VS Code eso ya
viene configurado; desde la terminal, `cd session1` antes de abrir Jupyter.

## Series utilizadas (API del BCRP)

| Código | Variable | Notación | Construcción |
|:-|:-|:-|:-|
| `PN38915BM` | índice de precios de exportación | $x_t$ | promedio trimestral, var. % interanual |
| `PN02538AQ` | PBI real trimestral | $y_t$ | var. % interanual |
| `PN38689FM` | ingresos corrientes del gobierno general (términos reales) | $r_t$ | promedio trimestral, var. % interanual |

## Referencias

Sims (1980); Litterman (1986); Sims, Stock y Watson (1990); Hamilton (1994); Waggoner y Zha (1999);
Lütkepohl (2005); Karlsson (2013); Blake y Mumtaz (2017); Vassallo (2026), *Macroeconometría
Aplicada con Python*.
