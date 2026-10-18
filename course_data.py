"""Una sola base de datos para todo el curso.

    import sys; sys.path.append("..")        # desde la carpeta de una sesión
    from course_data import load, yoy

    df = load()                              # niveles trimestrales, todas las series
    g = yoy(df[["ipx", "pbi", "icgc"]])      # variación % interanual

La base es una copia congelada en ``data/macro_peru.csv``: todos reproducen
exactamente los números de las láminas, con o sin internet. Para traer datos
nuevos de las APIs, ``load(refresh=True)`` los descarga sin tocar la copia;
esos números pueden diferir de las láminas por las revisiones del BCRP.

Las series están en niveles y en frecuencia trimestral. Las mensuales y la
diaria se promedian dentro del trimestre, y solo entran los trimestres
completos. Las anomalías ENSO de NOAA y ``pbi_sa``, el PBI desestacionalizado
con X-13ARIMA-SEATS (sesión 4), se agregaron a la copia congelada el
2026-10-16 sin tocar las demás series. Cada trimestre se fecha el primer día
de su último mes (marzo, junio, setiembre, diciembre). El detalle de cada
serie está en ``data/diccionario.csv``.
"""
from __future__ import annotations

import io
import urllib.request
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "macro_peru.csv"
DICCIONARIO = ROOT / "data" / "diccionario.csv"

# nombre: (fuente, código, frecuencia de origen, descripción, unidad)
SERIES = {
    "pbi":     ("BCRP", "PN02538AQ", "Q", "PBI real", "millones de S/ de 2007"),
    "invpriv": ("BCRP", "PN02533AQ", "Q", "Inversión bruta fija privada", "millones de S/ de 2007"),
    "ipc":     ("BCRP", "PN38705PM", "M", "Índice de precios al consumidor, Lima Metropolitana", "índice dic. 2021 = 100"),
    "int":     ("BCRP", "PN07819NM", "M", "Tasa de interés interbancaria promedio", "% anual"),
    "tpm":     ("BCRP", "PD04722MM", "M", "Tasa de referencia de la política monetaria", "% anual"),
    "tdi":     ("BCRP", "PN38923BM", "M", "Términos de intercambio", "índice 2007 = 100"),
    "ipx":     ("BCRP", "PN38915BM", "M", "Índice de precios de exportación", "índice 2007 = 100"),
    "icgc":    ("BCRP", "PN38689FM", "M", "Ingresos corrientes del gobierno central, en términos reales", "millones de S/ de dic. 2021"),
    "tc":      ("BCRP", "PN01210PM", "M", "Tipo de cambio bancario promedio", "S/ por US$"),
    "usgdp":   ("FRED", "GDPC1",     "Q", "PBI real de Estados Unidos", "miles de millones de US$ de 2017"),
    "uscpi":   ("FRED", "CPIAUCSL",  "M", "Índice de precios al consumidor de Estados Unidos", "índice 1982-84 = 100"),
    "fed":     ("FRED", "FEDFUNDS",  "M", "Tasa de fondos federales", "% anual"),
    "vix":     ("FRED", "VIXCLS",    "D", "Índice de volatilidad implícita VIX", "puntos"),
    "cobre":   ("FRED", "PCOPPUSDM", "M", "Precio internacional del cobre", "US$ por tonelada métrica"),
    "cdbcrp":  ("BCRP", "PN06503OM", "M", "Tasa de interés de los certificados de depósito del BCRP (promedio de los meses con subasta)", "% anual"),
    "nino12":  ("NOAA", "nina1",     "M", "Anomalía de la temperatura superficial del mar, región Niño 1+2", "°C respecto al promedio 1981-2010 (ERSST v6)"),
    "nino34":  ("NOAA", "nina34",    "M", "Anomalía de la temperatura superficial del mar, región Niño 3.4", "°C respecto al promedio 1981-2010 (ERSST v6)"),
}

# Series derivadas de las anteriores: nombre: (serie de origen, descripción).
# Se calculan al armar la base, así que la copia congelada fija también el
# ajuste estacional (el binario de X-13 que trae MacroPy no existe en Windows).
DERIVED = {
    "pbi_sa": ("pbi", "PBI real desestacionalizado (X-13ARIMA-SEATS aplicado a pbi en la copia congelada)"),
}

# Etiquetas legibles para los gráficos, con la notación de las láminas.
LABELS = {
    "x": "Precios de exportación", "y": "PBI", "r": "Ingresos fiscales",
    "tot": "Términos de intercambio", "pi": "Inflación", "i": "Tasa interbancaria",
    "nino12": "Anomalía Niño 1+2 (°C)", "vix": "VIX",
}


# ----------------------------------------------------------------- uso
def load(refresh: bool = False) -> pd.DataFrame:
    """Base trimestral en niveles. Por defecto, la copia congelada."""
    if refresh:
        print("Datos descargados hoy de las APIs: pueden diferir de las láminas "
              "por revisiones del BCRP. La copia congelada no se modifica.")
        return download()
    return pd.read_csv(DATA, index_col="date", parse_dates=True)


def vintage() -> str:
    """Fecha en que se descargó la copia congelada."""
    return str(pd.read_csv(DICCIONARIO)["descargado"].iloc[0])


def yoy(df):
    """Variación porcentual interanual: 100 (x_t / x_{t-4} - 1)."""
    return 100 * (df / df.shift(4) - 1)


def quarter(stamp) -> str:
    """Fecha a etiqueta de las láminas, por ejemplo 2017Q4."""
    stamp = pd.Timestamp(stamp)
    return f"{stamp.year}Q{stamp.quarter}"


# --------------------------------------------- sistemas de las sesiones
def macrofiscal(df: pd.DataFrame | None = None, start: str = "2002-06-01") -> pd.DataFrame:
    """Sesiones 1 y 2: (x, y, r) = precios de exportación, PBI e ingresos
    fiscales, en variación % interanual, desde 2002Q2."""
    df = load() if df is None else df
    g = yoy(df[["ipx", "pbi", "icgc"]]).rename(columns={"ipx": "x", "pbi": "y", "icgc": "r"})
    return g.dropna().loc[start:]


def small_open_economy(df: pd.DataFrame | None = None, start: str = "2002-03-01",
                       end: str = "2019-12-01") -> pd.DataFrame:
    """Sesión 3: (tot, y, pi, i) = términos de intercambio, PBI e inflación en
    variación % interanual, y la tasa interbancaria en niveles."""
    df = load() if df is None else df
    g = yoy(df[["tdi", "pbi", "ipc"]]).rename(columns={"tdi": "tot", "pbi": "y", "ipc": "pi"})
    return g.join(df["int"].rename("i")).loc[start:end].dropna()


def interbank_long(df: pd.DataFrame | None = None) -> pd.Series:
    """Tasa de interés de corto plazo empalmada: la de los certificados de
    depósito del BCRP (``cdbcrp``, desde 1992Q3, con huecos en 1992Q4, 1993Q1 y
    1997Q1-Q2 cubiertos por los meses disponibles) hasta 1995Q3 y la
    interbancaria (``int``) desde 1995Q4. Sin ajuste de nivel: en el
    solapamiento 1995Q4-2000Q4 la interbancaria promedia 0.4 puntos menos."""
    df = load() if df is None else df
    return df["int"].fillna(df["cdbcrp"].where(df.index < "1995-12-01")).rename("i")


def el_nino(df: pd.DataFrame | None = None, start: str = "1994-03-01",
            end: str = "2019-12-01") -> pd.DataFrame:
    """Sesión 4: (nino12, y, pi) = anomalía de temperatura del mar en la región
    Niño 1+2 (promedio trimestral, °C), PBI e inflación en variación %
    interanual. Desde 1994Q1, con la inflación ya en dos dígitos tras la
    hiperinflación, y hasta 2019Q4 por defecto; con ``end`` posterior, el
    notebook de la sesión excluye la pandemia de la verosimilitud."""
    df = load() if df is None else df
    g = yoy(df[["pbi", "ipc"]]).rename(columns={"pbi": "y", "ipc": "pi"})
    return df[["nino12"]].join(g).loc[start:end].dropna()


# ------------------------------------------------- descarga (docente)
def _noaa(code: str) -> pd.Series:
    """Índices ENSO mensuales de NOAA PSL (https://psl.noaa.gov/data/climateindices/)."""
    url = f"https://psl.noaa.gov/data/correlation/{code}.anom.data"
    txt = urllib.request.urlopen(url, timeout=60).read().decode()
    values = {}
    for line in txt.splitlines():
        parts = line.split()
        if len(parts) == 13 and parts[0].isdigit():          # año + 12 meses
            for month, v in enumerate(parts[1:], 1):
                if float(v) > -90:                            # -99.99 = sin dato
                    values[pd.Timestamp(int(parts[0]), month, 1)] = float(v)
    return pd.Series(values).sort_index()


def _bcrp(code: str, freq: str) -> pd.Series:
    from MacroPy import get_bcrp_data
    out = get_bcrp_data({code: code}, frequency=freq, start_period="1975-1", date_index=True)
    if out is None or len(out) == 0:
        raise ConnectionError(f"la API del BCRP no devolvió {code}")
    s = out[code].astype(float)
    s.index = pd.DatetimeIndex(s.index)
    return s


def _fred(code: str) -> pd.Series:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={code}"
    raw = urllib.request.urlopen(url, timeout=60).read()
    d = pd.read_csv(io.BytesIO(raw))
    s = pd.to_numeric(d[code], errors="coerce")
    s.index = pd.DatetimeIndex(d.iloc[:, 0])
    return s.dropna()


def _quarterly(s: pd.Series, freq: str, complete: bool = True) -> pd.Series:
    """A trimestral, solo trimestres completos (``complete=False`` promedia los
    meses disponibles), fechados en su último mes."""
    if freq == "Q":
        q = s.copy()
        q.index = q.index.to_period("Q")
    else:
        m = s.resample("MS").mean() if freq == "D" else s.copy()
        if freq == "D":                                   # el último mes solo si terminó
            fin = s.index.max()
            if fin < fin + pd.offsets.BMonthEnd(0):       # antes de su último día hábil
                m = m.iloc[:-1]
        m.index = m.index.to_period("M")
        meses = m.groupby(m.index.asfreq("Q")).count()
        q = m.groupby(m.index.asfreq("Q")).mean()[meses == 3 if complete else meses >= 1]
    q.index = q.index.to_timestamp(how="start") + pd.DateOffset(months=2)
    q.index.name = "date"
    return q


def download() -> pd.DataFrame:
    """Descarga todas las series de las APIs y las arma en trimestral."""
    cols = {}
    for name, (fuente, code, freq, _, _) in SERIES.items():
        if fuente == "BCRP":
            raw = _bcrp(code, "Q" if freq == "Q" else "M")
        elif fuente == "NOAA":
            raw = _noaa(code)
        else:
            raw = _fred(code)
        cols[name] = _quarterly(raw, freq, complete=name != "cdbcrp")
    df = pd.DataFrame(cols)
    df.index.name = "date"
    for name, (source, _) in DERIVED.items():
        df[name] = _seasonal(df[source])
    return df.dropna(how="all")


def _seasonal(s: pd.Series) -> pd.Series:
    """Ajuste estacional con X-13 (binario incluido en MacroPy para macOS y
    Linux); si no está disponible, STL, que da factores parecidos pero no
    idénticos a los de la copia congelada."""
    from MacroPy import seasonal_adjust
    s = s.dropna()
    try:
        out = seasonal_adjust(s, method="x13").seasadj
    except Exception:
        print("X-13 no disponible en esta plataforma: ajuste estacional con STL.")
        out = seasonal_adjust(s, method="stl").seasadj
    out.index = s.index                       # X-13 fecha los trimestres en su primer mes
    return out


def build_snapshot() -> pd.DataFrame:
    """Regenera la copia congelada y el diccionario. Solo para el docente:
    cambia los números que reproducen las láminas."""
    df = download()
    DATA.parent.mkdir(exist_ok=True)
    df.round(6).to_csv(DATA)
    hoy = date.today().isoformat()
    filas = []
    for name, (fuente, code, freq, desc, unidad) in SERIES.items():
        s = df[name].dropna()
        filas.append({"serie": name, "descripcion": desc, "unidad": unidad,
                      "fuente": fuente, "codigo": code,
                      "frecuencia_origen": {"Q": "trimestral", "M": "mensual", "D": "diaria"}[freq],
                      "desde": quarter(s.index[0]), "hasta": quarter(s.index[-1]),
                      "descargado": hoy})
    for name, (source, desc) in DERIVED.items():
        s = df[name].dropna()
        fuente, code, freq, _, unidad = SERIES[source]
        filas.append({"serie": name, "descripcion": desc, "unidad": unidad,
                      "fuente": fuente, "codigo": code,
                      "frecuencia_origen": {"Q": "trimestral", "M": "mensual", "D": "diaria"}[freq],
                      "desde": quarter(s.index[0]), "hasta": quarter(s.index[-1]),
                      "descargado": hoy})
    pd.DataFrame(filas).to_csv(DICCIONARIO, index=False)
    print(f"Copia congelada: {DATA.relative_to(ROOT)} ({df.shape[0]} trimestres, "
          f"{df.shape[1]} series), descargada el {hoy}.")
    return df
