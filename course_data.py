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
completos. Cada trimestre se fecha el primer día de su último mes (marzo,
junio, setiembre, diciembre). El detalle de cada serie está en
``data/diccionario.csv``.
"""
from __future__ import annotations

import io
import urllib.request
from datetime import date
from pathlib import Path

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
}

# Etiquetas legibles para los gráficos, con la notación de las láminas.
LABELS = {
    "x": "Precios de exportación", "y": "PBI", "r": "Ingresos fiscales",
    "tot": "Términos de intercambio", "pi": "Inflación", "i": "Tasa interbancaria",
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


# ------------------------------------------------- descarga (docente)
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


def _quarterly(s: pd.Series, freq: str) -> pd.Series:
    """A trimestral, solo trimestres completos, fechados en su último mes."""
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
        q = m.groupby(m.index.asfreq("Q")).mean()[meses == 3]
    q.index = q.index.to_timestamp(how="start") + pd.DateOffset(months=2)
    q.index.name = "date"
    return q


def download() -> pd.DataFrame:
    """Descarga todas las series de las APIs y las arma en trimestral."""
    cols = {}
    for name, (fuente, code, freq, _, _) in SERIES.items():
        raw = _bcrp(code, "Q" if freq == "Q" else "M") if fuente == "BCRP" else _fred(code)
        cols[name] = _quarterly(raw, freq)
    df = pd.DataFrame(cols)
    df.index.name = "date"
    return df.dropna(how="all")


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
    pd.DataFrame(filas).to_csv(DICCIONARIO, index=False)
    print(f"Copia congelada: {DATA.relative_to(ROOT)} ({df.shape[0]} trimestres, "
          f"{df.shape[1]} series), descargada el {hoy}.")
    return df
