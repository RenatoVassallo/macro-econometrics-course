"""Quarterly macro-fiscal data for Peru from the BCRP API, with a CSV cache.

Series: export price index (PN38915BM, monthly), real GDP (PN02538AQ,
quarterly) and general government current revenues in real terms
(PN38689FM, monthly). Monthly series are averaged to quarters.
"""
import pandas as pd

MONTHLY = {"PN38915BM": "ipx", "PN38689FM": "icgg"}
QUARTERLY = {"PN02538AQ": "pbi"}
NAMES = {"ipx": "x", "pbi": "y", "icgg": "r"}   # notation of the slides


def load_levels(cache="data/peru_macrofiscal_bcrp.csv"):
    """Quarterly levels; refresh the cache when the API answers."""
    try:
        from MacroPy import get_bcrp_data
        monthly = get_bcrp_data(MONTHLY, frequency="M",
                                start_period="1996-1", date_index=True)
        quarterly = get_bcrp_data(QUARTERLY, frequency="Q",
                                  start_period="1995-1", date_index=True)
        if (monthly is None or quarterly is None
                or len(monthly) == 0 or len(quarterly) == 0):
            raise ConnectionError("la API del BCRP no respondió")
        levels = pd.DataFrame({c: monthly[c].resample("QS").mean()
                               for c in ("ipx", "icgg")})
        levels = levels[monthly["ipx"].resample("QS").count() == 3]
        levels.index = levels.index.to_period("Q")
        gdp = quarterly["pbi"]
        gdp.index = pd.DatetimeIndex(gdp.index).to_period("Q")
        levels["pbi"] = gdp
        levels = levels[["ipx", "pbi", "icgg"]]
        stamps = levels.index.to_timestamp(how="start")
        levels.index = stamps + pd.DateOffset(months=2)
        levels.index.name = "date"
        levels.to_csv(cache)
        return levels, "API del BCRP (respaldo actualizado)"
    except Exception as err:
        levels = pd.read_csv(cache, index_col="date", parse_dates=True)
        return levels, f"respaldo local {cache} ({err})"


def yoy_growth(levels, start="2002-06-01"):
    """Year-on-year growth in percent, with columns x, y, r."""
    growth = 100 * (levels / levels.shift(4) - 1)
    growth = growth.dropna().loc[start:].rename(columns=NAMES)
    return growth[["x", "y", "r"]]


def quarter(stamp):
    """Timestamp to the label used in the slides, e.g. 2017Q4."""
    return f"{stamp.year}Q{stamp.quarter}"
