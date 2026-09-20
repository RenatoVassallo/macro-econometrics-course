# Sesión 1: modelos VAR bayesianos. Estimación, pronóstico y escenarios

## Objetivos

1. Representación del VAR: forma compacta, companion y vectorizada, estabilidad, y la equivalencia
   entre mínimos cuadrados (MCO) y máxima verosimilitud.
2. Del prior a la posterior: prior de Minnesota para los coeficientes, inversa-Wishart para la
   covarianza y el muestreador de Gibbs.
3. Pronóstico con la forma companion: el ECM se acumula con el horizonte y abre la banda; la densidad
   predictiva bayesiana suma la incertidumbre de los parámetros (bandas al 68 y 95 %).
4. Pronósticos condicionales (Waggoner y Zha, 1999): la matriz de restricciones $A$ y dos escenarios
   para los precios de exportación.

Todo usa datos hasta 2019. La exogeneidad de bloque y la pandemia pasan a la sesión 2; el material
que ya estaba hecho quedó en `../session2/de_sesion1/`.

## Notación

La del libro *Macroeconometría Aplicada con Python* (Vassallo, 2026):
$\mathbf{y}_t = c + \Phi_1\mathbf{y}_{t-1} + \Phi_2\mathbf{y}_{t-2} + \mathbf{u}_t$, forma compacta
$Y = XB + U$ con la constante en la primera fila de $B$, $b = \operatorname{vec}(B)$,
$b \sim N(b_0, H)$, $\Sigma \sim \mathcal{IW}(S_0, \nu_0)$ y $\mathbf{u}_t = S\varepsilon_t$. Las variables
son el crecimiento interanual de los precios de exportación ($x_t$), del PBI ($y_t$) y de los ingresos
fiscales ($r_t$); $p$ es el número de rezagos. El código de los notebooks está en inglés y el texto, en
castellano.

## Material

- `bvar_peru_1_del_var_al_bvar.ipynb` (aplicación 1): VAR(2) bivariado en $x_t$ y $r_t$, 2002Q2 a
  2017Q4. Matrices a mano, MCO igual a máxima verosimilitud, $b_0$ y $H$ del prior de Minnesota,
  muestreador de Gibbs programado a mano y contraste con `MacroPy`.
- `bvar_peru_2_pronostico.ipynb` (aplicación 2): modelo macrofiscal en $(x_t, y_t, r_t)'$. Densidad
  predictiva a mano (companion y Cholesky) contra `MacroPy` y el ECM, pronóstico 2018-2019 contra lo
  observado, la matriz $A$ de Waggoner y Zha armada a mano y verificada contra `MacroPy`, y dos
  escenarios de precios de exportación.
- `macrofiscal_data.py`: descarga las series de la API del BCRP y actualiza el respaldo local.
- `slides/session1_bvar.tex`: las diapositivas (beamer, 3 horas). La figura del apéndice sale del
  notebook 2; `slides/figures/_sin_uso/` guarda figuras de versiones anteriores y `slides/_respaldo/`,
  versiones anteriores del .tex.
- `data/peru_macrofiscal_bcrp.csv`: niveles trimestrales de respaldo.
- `_archivo_version_mensual/`: versión anterior de la sesión (modelo mensual de cinco variables).
  Leer su `LEEME.md` antes de reutilizarla.

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
