# Sesión 4: Modelos no lineales. Threshold VAR, volatilidad estocástica y TVP-VAR

## Objetivos

1. Threshold VAR, la no linealidad más simple: dos VAR y una variable observable que decide cuál
   rige; umbral y rezago estimados; exogeneidad de bloque para la variable que no depende de la
   economía doméstica; respuestas generalizadas que dependen de la historia, el régimen y el
   tamaño del choque; escenarios con cambio de régimen; la pandemia tratada con las escalas de
   Lenza y Primiceri de la sesión 2.
2. Volatilidad estocástica: la varianza como estado latente con su propio choque, cómo se estima
   (mezcla de normales de Kim, Shephard y Chib; Metropolis período a período) y por qué cambia las
   bandas y no las medianas.
3. TVP-VAR con volatilidad estocástica, el modelo completamente no lineal: coeficientes que
   derivan como paseos aleatorios; el Gibbs en tres bloques de Chan y Eisenstat (2018); una
   impulso-respuesta, una FEVD y una descomposición histórica por fecha; la comparación de modelos
   con verosimilitud marginal y DIC; la familia de Chan y Eisenstat como extensión.
4. Lecturas aplicadas: Alessandri y Mumtaz (2019), Auerbach y Gorodnichenko (2012), Sánchez y
   Vassallo (2026), Primiceri (2005), Cogley y Sargent (2005), Gambetti y Musso (2017), Rodríguez,
   Vassallo y Castillo (2023), Chan y Eisenstat (2018).

Menos álgebra que en las sesiones anteriores: la intuición, los pasos de cada algoritmo y lo que
dicen los datos.

## Los sistemas

**Threshold VAR** (aplicación A): $\mathbf{y}_t = (F_t,\ y_t,\ \pi_t,\ ing_t)'$, trimestral, 1996Q1 a
2026Q2, dos rezagos. $F_t$ es la anomalía de la temperatura superficial del mar en la región Niño
1+2 y es la variable umbral. Forma un **bloque exógeno** (`b_exo`): un AR lineal, sin regímenes y
sin rezagos de las variables domésticas, mientras que las ecuaciones domésticas tienen dos
regímenes y reciben $F_t$ y sus rezagos. La pandemia se trata como en la sesión 2, con escalas de
volatilidad de Lenza y Primiceri (2022) para 2020Q1 a 2021Q4, estimadas por verosimilitud marginal
en el VAR lineal con el mismo prior (`covid_mode="lenza-primiceri"`); la ventana cubre los dos
trimestres cuyos rezagos son la caída de 2020Q2 y el rebote interanual de 2021Q2.

| Código | Variable | Notación | Construcción |
|:-|:-|:-|:-|
| NOAA `nina1` | anomalía Niño 1+2 | $F_t$ | promedio trimestral de la serie mensual, °C respecto a 1981-2010 |
| `PN02538AQ` | PBI real trimestral | $y_t$ | var. % interanual |
| `PN38705PM` | índice de precios al consumidor | $\pi_t$ | promedio trimestral, var. % interanual |
| `PN38689FM` | ingresos corrientes del gobierno central, en términos reales | $ing_t$ | promedio trimestral, var. % interanual (la serie empieza en 1995, de ahí la muestra desde 1996Q1) |

**TVP-VAR-SV** (aplicación B): $\mathbf{y}_t = (tot_t,\ y_t,\ \pi_t,\ i_t)'$, el sistema de la sesión 3,
pero de 1997Q1 a 2026Q2, con la pandemia dentro de la muestra y sin tratamiento especial, y con
los términos de intercambio como bloque exógeno: sus rezagos entran en todas las ecuaciones, los
de las variables domésticas no entran en la suya.

Series nuevas en la base del curso, agregadas el 2026-10-16 sin tocar las demás: `nino12` y
`nino34` (NOAA PSL, ERSST v6); `cdbcrp`, la tasa de los certificados de depósito del BCRP
(`PN06503OM`, desde junio de 1992), con la que `course_data.interbank_long` empalma la tasa
interbancaria hacia atrás hasta 1992Q3; y `pbi_sa`, el PBI desestacionalizado con X-13ARIMA-SEATS
(el binario que trae `MacroPy` no existe para Windows, así que el ajuste queda fijado en la copia;
los notebooks de esta sesión no lo usan, queda para ejercicios en niveles).

## Material

- **En las láminas**: los modelos, las lecturas aplicadas (Alessandri y Mumtaz, 2019; Sánchez y
  Vassallo, 2026; Chan y Eisenstat, 2018; en el apéndice, un resumen de Primiceri, 2005, Gambetti
  y Musso, 2017, y Rodríguez, Vassallo y Castillo, 2023) y las **instrucciones** de las dos
  aplicaciones: qué estimar y qué preguntas responder. Las láminas no adelantan los resultados de
  las aplicaciones, salvo la volatilidad estimada que cierra la sección de volatilidad estocástica
  (TVP-SV frente a la desviación estándar constante): se obtienen al correr los notebooks, que
  cierran con sus ideas centrales.
- `session4_A_tvar.ipynb` (aplicación A): las escalas de Lenza y Primiceri, el umbral, el rezago
  y los trimestres Niño; dos factores de Bayes, el del umbral y el de la exogeneidad de bloque, y
  qué cambia con la muestra hasta 2019, sin tratamiento o con dummies; respuestas por régimen del
  PBI, la inflación y los ingresos fiscales a un calentamiento de 1 °C, con y sin bloque, con
  asimetrías de tamaño y signo; la densidad predictiva simulada a mano con cambio de régimen y
  cuatro escenarios para el Niño de 2026, comparados con el VAR lineal; y una tabla de robustez
  (sin bloque, términos de intercambio como control, sin ingresos desde 1994, Niño 3.4). La
  extensión con volatilidad estocástica, `ThresholdVARSV`, queda en el tutorial de `MacroPy`.
- `session4_B_tvpvar.ipynb` (aplicación B): `C` frente a `TVP-SV` con verosimilitud marginal y
  DIC; la volatilidad estocástica frente a la desviación estándar constante; IRF resumidas con la
  mediana de las medianas, en superficies 3D **interactivas** (`plotly`: se rotan en VS Code,
  Codespaces y JupyterLab) y en tres fechas, con el tamaño del choque normalizado para separar
  tamaño y transmisión; FEVD a 20 trimestres y descomposición histórica por fecha; y la
  competencia con `C-SV` y `TVP-R1-SV`, con el factor de Bayes de la exogeneidad de bloque.
- `nonlinear_lp.py` (cierre; apéndice de las láminas): proyecciones locales no lineales para El
  Niño. Estima directamente la respuesta acumulada a dos años del PBI y de los ingresos fiscales
  con un spline lineal en la anomalía (nudo en 1 °C), compara un calentamiento moderado ($+1$ °C)
  con uno extremo ($+3$ °C) y los contrasta con las GIRF del TVAR del notebook A. `python
  nonlinear_lp.py` imprime las tablas y la robustez y guarda la figura; tarda unos 10 segundos.
- Los datos salen de la base del curso, `data/macro_peru.csv`, a través de `course_data.py`.
- Requiere `MacroPy` 0.3.3 (exogeneidad de bloque en `ThresholdVAR` y `TimeVaryingVAR`;
  verosimilitud marginal y DIC estables en los modelos con volatilidad estocástica) y `plotly`;
  `python check_setup.py` lo verifica.
- Tiempo de corrida medido en macOS y Linux: el notebook A, 15 a 26 segundos; el B, minuto y medio
  con cuatro núcleos o más, dos minutos con dos y tres con uno, sin celdas de más de un minuto. Los
  dos notebooks dejan el álgebra lineal de `numpy` con un hilo en su primera celda (con todos los
  hilos, OpenBLAS, el de Windows, Linux y Codespaces, hace cientos de veces más lenta la
  verosimilitud marginal del TVP-SV), y el B reparte la verosimilitud marginal y el DIC entre
  hasta cuatro procesos.
- Las diapositivas se distribuyen aparte, por el Aula Virtual. Sus figuras propias se regeneran con
  `slides/figures.py`.

## Referencias

Hamilton (1989); Tong (1990); Jacquier, Polson y Rossi (1994); Chen y Lee (1995); Koop, Pesaran y
Potter (1996); Cushman y Zha (1997); Kim, Shephard y Chib (1998); Balke (2000); Cogley y Sargent
(2005); Jordà (2005); Primiceri (2005); Sims y Zha (2006); Chan y Jeliazkov (2009); Koop y Korobilis
(2010); Kilian y Vigfusson (2011); Auerbach y Gorodnichenko (2012); Alessandri y Mumtaz (2017,
2019); Gambetti y Musso (2017); Chan y Eisenstat (2018); Ramey y Zubairy (2018); Plagborg-Møller y
Wolf (2021); Lenza y Primiceri (2022); Rodríguez, Vassallo y Castillo (2023); Li, Plagborg-Møller y
Wolf (2024); Sánchez y Vassallo (2026); Vassallo (2026), *Macroeconometría Aplicada con Python*.
