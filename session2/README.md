# Sesión 2: VAR bayesianos. Estimación, pronóstico y la pandemia

## Objetivos

1. Por qué encoger: con muchos coeficientes y pocos datos, MCO pronostica mal. El prior escribe la
   restricción como una distribución.
2. Del prior a la posterior: prior de Minnesota para los coeficientes, inversa-Wishart para la
   covarianza y el muestreador de Gibbs.
3. La densidad predictiva: no hay fórmula cerrada sino trayectorias simuladas, un choque nuevo por
   trimestre, y un *fan chart* cuyas bandas son percentiles de esas trayectorias.
4. Pronósticos condicionales (Waggoner y Zha, 1999): imponer una senda y recuperar las demás.
   Condicionar es proyectar.
5. La pandemia: qué le hacen 2020 y 2021 a la persistencia y a $\Sigma$, y tres tratamientos
   (descartar, dummies con prior y escalamiento de volatilidad de Lenza y Primiceri, 2022).

Todo lo anterior a la pandemia usa datos hasta 2019.

## Notación

La del libro *Macroeconometría Aplicada con Python* (Vassallo, 2026), capítulo 5: $b = \operatorname{vec}(B)$,
$b \sim N(b_0, H)$, $\Sigma \sim \mathcal{IW}(S_0, \nu_0)$. Las variables son el crecimiento interanual
de los precios de exportación ($x_t$), del PBI ($y_t$) y de los ingresos fiscales ($r_t$).

## Material

- `session2_A_bvar.ipynb` (aplicación 1): el mismo VAR(2) bivariado de la sesión 1. $b_0$ y $H$ del
  prior de Minnesota, muestreador de Gibbs programado a mano, contraste con `MacroPy` y cuánto
  encoge el prior.
- `session2_B_forecasting.ipynb` (aplicación 2): modelo macrofiscal en $(x_t, y_t, r_t)'$. Densidad
  predictiva a mano contra `MacroPy`, pronóstico 2018-2019 contra lo observado, la matriz $A$ de
  Waggoner y Zha verificada contra `MacroPy`, y dos escenarios de precios de exportación.
- `session2_C_pandemia.ipynb` (aplicación 3): muestra completa. Qué le hace la pandemia a la
  persistencia y a la volatilidad, tres tratamientos comparados, tres *fan charts* lado a lado y la
  respuesta al impulso bajo cada tratamiento.
- Los datos salen de la base del curso, `data/macro_peru.csv`, a través de `course_data.py`; los
  dos están en la raíz del repositorio.
- Las diapositivas se distribuyen aparte, por el Aula Virtual.

## Series utilizadas

De la base del curso; el detalle de cada una está en `data/diccionario.csv`.

| Código BCRP | Variable | Notación | Construcción |
|:-|:-|:-|:-|
| `PN38915BM` | índice de precios de exportación | $x_t$ | promedio trimestral, var. % interanual |
| `PN02538AQ` | PBI real trimestral | $y_t$ | var. % interanual |
| `PN38689FM` | ingresos corrientes del gobierno central (términos reales) | $r_t$ | promedio trimestral, var. % interanual |

## Referencias

Litterman (1986); Kadiyala y Karlsson (1997); Waggoner y Zha (1999); Lütkepohl (2005); Karlsson
(2013); Blake y Mumtaz (2017); Lenza y Primiceri (2022); Cascaldi-Garcia (2022); Carriero, Clark,
Marcellino y Mertens (2024); Vassallo (2026), *Macroeconometría Aplicada con Python*, cap. 5.
