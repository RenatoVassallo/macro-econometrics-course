# Sesión 4: Modelos no lineales. Threshold VAR, volatilidad estocástica y TVP-VAR

## Objetivos

1. Threshold VAR, la no linealidad más simple: dos VAR y una variable observable que decide cuál
   rige; umbral y rezago estimados; respuestas generalizadas que dependen de la historia, el
   régimen y el tamaño del choque; pronósticos y escenarios con cambio de régimen; la pandemia
   tratada con las escalas de Lenza y Primiceri de la sesión 2.
2. Volatilidad estocástica: la varianza como estado latente con su propio choque, cómo se estima
   (mezcla de normales de Kim, Shephard y Chib; Metropolis período a período) y por qué cambia las
   bandas y no las medianas.
3. TVP-VAR con volatilidad estocástica, el modelo completamente no lineal: coeficientes que
   derivan como paseos aleatorios; una impulso-respuesta, una FEVD y una descomposición histórica
   por fecha; la familia de Chan y Eisenstat (2018) y cómo compararla sin verosimilitud marginal
   ni DIC.
4. Lecturas aplicadas: Alessandri y Mumtaz (2019), Auerbach y Gorodnichenko (2012), Sánchez y
   Vassallo (2026), Primiceri (2005), Gambetti y Musso (2017), Chan y Eisenstat (2018), Rodríguez,
   Vassallo y Castillo (2023), Sánchez y Vassallo (2023).

Menos álgebra que en las sesiones anteriores: la intuición, los pasos de cada algoritmo y lo que
dicen los datos.

## Los sistemas

**Threshold VAR** (aplicación A): $\mathbf{y}_t = (F_t,\ y_t,\ \pi_t)'$, trimestral, 1994Q1 a 2026Q2,
dos rezagos. $F_t$ es la anomalía de la temperatura superficial del mar en la región Niño 1+2 y
es la variable umbral. La pandemia se trata como en la sesión 2, con escalas de volatilidad de
Lenza y Primiceri (2022) para 2020Q1 a 2021Q4, estimadas por verosimilitud marginal en el VAR
lineal con el mismo prior (`covid_mode="lenza-primiceri"`, desde `MacroPy` 0.3.1); la ventana
cubre los dos trimestres cuyos rezagos son la caída de 2020Q2 y el rebote interanual de 2021Q2.

| Código | Variable | Notación | Construcción |
|:-|:-|:-|:-|
| NOAA `nina1` | anomalía Niño 1+2 | $F_t$ | promedio trimestral de la serie mensual, °C respecto a 1981-2010 |
| `PN02538AQ` | PBI real trimestral | $y_t$ | var. % interanual |
| `PN38705PM` | índice de precios al consumidor | $\pi_t$ | promedio trimestral, var. % interanual |

**TVP-VAR-SV** (aplicación B): $\mathbf{y}_t = (tot_t,\ y_t,\ \pi_t,\ i_t)'$, el sistema de la sesión 3,
pero de 1997Q1 a 2026Q2, con la pandemia dentro de la muestra y sin tratamiento especial.

Series nuevas en la base del curso, agregadas el 2026-10-16 sin tocar las demás: `nino12` y
`nino34` (NOAA PSL, ERSST v6); `cdbcrp`, la tasa de los certificados de depósito del BCRP
(`PN06503OM`, desde junio de 1992), con la que `course_data.interbank_long` empalma la tasa
interbancaria hacia atrás hasta 1992Q3; y `pbi_sa`, el PBI desestacionalizado con X-13ARIMA-SEATS
(el binario que trae `MacroPy` no existe para Windows, así que el ajuste queda fijado en la copia;
los notebooks de esta sesión no lo usan, queda para ejercicios en niveles).

## Material

- **En las láminas**: los modelos, las lecturas aplicadas (Alessandri y Mumtaz, 2019; Sánchez y
  Vassallo, 2026; Primiceri, 2005; Chan y Eisenstat, 2018; Rodríguez, Vassallo y Castillo, 2023;
  Sánchez y Vassallo, 2023) y las **instrucciones** de las dos aplicaciones: qué estimar y qué
  preguntas responder. Las láminas no adelantan los resultados de las aplicaciones, salvo las
  volatilidades estimadas que cierran la sección de volatilidad estocástica: se obtienen al correr
  los notebooks, que cierran con sus ideas centrales.
- `session4_A_tvar.ipynb` (aplicación A): las escalas de Lenza y Primiceri, el umbral, el rezago
  y los trimestres Niño, y qué cambia con la muestra hasta 2019, sin tratamiento o con dummies;
  respuestas por régimen a un calentamiento de 1 °C, con asimetrías de tamaño y signo; la densidad
  predictiva simulada a mano con cambio de régimen y cuatro escenarios para el Niño de 2026,
  comparados con el VAR lineal con el mismo tratamiento; y una tabla con doce especificaciones
  (controles externos, inversión, tasa de interés, más historia, Niño 3.4, otras ventanas para
  las escalas). La extensión con volatilidad estocástica, `ThresholdVARSV`, queda en el tutorial
  de `MacroPy`.
- `session4_B_tvpvar.ipynb` (aplicación B): los modelos `C`, `C-SV`, `TVP-SV` y `TVP-R3-SV`;
  volatilidades; IRF en tres fechas, en el tiempo y en superficies 3D **interactivas** (`plotly`:
  se rotan en VS Code, Codespaces y JupyterLab), con el tamaño del choque normalizado para separar
  tamaño y transmisión; FEVD a 20 trimestres y descomposición histórica por fecha; y una
  evaluación de pronósticos 2024-2026 con origen en 2023Q4.
- Los datos salen de la base del curso, `data/macro_peru.csv`, a través de `course_data.py`.
- Requiere `MacroPy` 0.3.3 (gráficos en grilla, FEVD a 20 pasos y FEVD que no depende de
  `irf_1std`) y `plotly`; `python check_setup.py` lo verifica.
- Tiempo de corrida en un portátil reciente: unos 20 segundos el notebook A y un minuto y medio el B.
- Las diapositivas se distribuyen aparte, por el Aula Virtual. Sus figuras propias se regeneran con
  `slides/figures.py`.

## Referencias

Hamilton (1989); Tong (1990); Jacquier, Polson y Rossi (1994); Chen y Lee (1995); Koop, Pesaran y
Potter (1996); Kim, Shephard y Chib (1998); Balke (2000); Cogley y Sargent (2005); Primiceri
(2005); Sims y Zha (2006); Chan y Jeliazkov (2009); Koop y Korobilis (2010); Auerbach y
Gorodnichenko (2012); Alessandri y Mumtaz (2017, 2019); Gambetti y Musso (2017); Chan y Eisenstat
(2018); Ramey y Zubairy (2018); Lenza y Primiceri (2022); Rodríguez, Vassallo y Castillo (2023);
Sánchez y Vassallo (2023, 2026); Vassallo (2026), *Macroeconometría Aplicada con Python*.
