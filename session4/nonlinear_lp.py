"""Proyecciones locales no lineales: El Niño por intensidad.

Ejercicio de cierre de la sesión 4 (apéndice de las láminas). En lugar de estimar dos sistemas
dinámicos completos, como el Threshold VAR de session4_A_tvar.ipynb, una regresión por variable
estima directamente la respuesta acumulada a dos años del PBI y de los ingresos fiscales a la
anomalía Niño 1+2 del trimestre (Jordà, 2005). La intensidad entra con un spline lineal: una
pendiente hasta 1 °C y otra por encima.

    S_t = x_t + ... + x_{t+8} = a + b F_t + g (F_t - k)_+ + sum_{j=1}^{2} G_j' w_{t-j} + u_t

x es el PBI o los ingresos (var. % interanual), w = (F, y, pi, ing) y k = 1 °C. La respuesta a
una anomalía F desde condiciones neutrales es R(F) = b F + g (F - k)_+: moderado R(1) = b,
extremo R(3) = 3b + 2g. Errores estándar HAC (Newey-West); bandas al 68 %. Se excluyen los
trimestres t cuya ventana [t - 2, t + 8] toca la pandemia (2020Q1-2021Q4).

La comparación es la GIRF acumulada del TVAR del notebook A (régimen normal, mismas opciones y
semilla) a choques de +1, +2 y +3 °C. Al final se imprime la robustez de la respuesta a +3 °C.

Uso, desde session4:
    python nonlinear_lp.py
    python nonlinear_lp.py --out slides/figures/fig_lp_nino.pdf
Tarda menos de un minuto.
"""
import os
for var in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ.setdefault(var, "1")         # antes de numpy: con matrices pequeñas, un hilo rinde más

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from MacroPy import ThresholdVAR, set_style

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE.parent))           # course_data.py vive en la raíz del repositorio
import course_data as cd

H = 8                                       # respuesta acumulada entre el impacto y h = 8
LAGS = 2
KNOT = 1.0                                  # °C: cambio de pendiente del spline
COVID = (pd.Timestamp("2020-03-01"), pd.Timestamp("2021-12-01"))
HAC_LAGS = H + 4                            # suma de 9 trimestres de tasas interanuales
Z68 = 0.9945                                # cuantil 84 de la normal
SHOCKS = (1.0, 2.0, 3.0)                    # choques del TVAR, °C
N_JOBS = min(4, os.cpu_count() or 1)
VARS = {"y": "PBI", "ing": "Ingresos fiscales"}
INK, ACCENT, BLUE, MUTED = "#2A231D", "#B0472A", "#3D647F", "#6B5F52"


def load_data() -> pd.DataFrame:
    """(nino12, y, pi, ing), 1996Q1-2026Q2: el sistema del notebook A."""
    levels = cd.load()
    g = cd.yoy(levels[["pbi", "ipc", "icgc"]]).rename(columns={"pbi": "y", "ipc": "pi", "icgc": "ing"})
    return levels[["nino12"]].join(g).loc["1996-03-01":"2026-06-01"].dropna()


def spline(F, knot=KNOT) -> pd.DataFrame:
    """Base del spline lineal: F y (F - k)_+. Con knot=None, solo F (la LP lineal)."""
    F = pd.Series(np.asarray(F, dtype=float).ravel())
    return pd.DataFrame({"F": F} if knot is None else {"F": F, "F_k": np.maximum(F - knot, 0.0)})


def lp_cumulative(Y: pd.DataFrame, var: str, knot=KNOT, lags=LAGS, controls=None):
    """Regresión de x_t + ... + x_{t+H} sobre el spline de F_t, una constante y rezagos de w."""
    W = Y if controls is None else Y.join(controls)
    S = sum(W[var].shift(-h) for h in range(H + 1)).rename("S")
    X = spline(W["nino12"], knot).set_index(W.index)
    X = X.join([W.shift(j).add_suffix(f"_l{j}") for j in range(1, lags + 1)])
    df = pd.concat([S, sm.add_constant(X)], axis=1).dropna()
    first = df.index - pd.DateOffset(months=3 * lags)
    last = df.index + pd.DateOffset(months=3 * H)
    df = df[(last < COVID[0]) | (first > COVID[1])]
    fit = sm.OLS(df["S"], df.drop(columns="S")).fit(cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS})
    fit.knot = knot
    return fit, df


def lp_response(fit, F):
    """R(F) = b F + g (F - k)_+ y su error estándar."""
    B = spline(F, fit.knot)
    cols = list(B.columns)
    V = fit.cov_params().loc[cols, cols].to_numpy()
    B = B.to_numpy()
    return B @ fit.params[cols].to_numpy(), np.sqrt(np.einsum("ij,jk,ik->i", B, V, B))


def tvar_responses(Y: pd.DataFrame) -> dict:
    """Percentiles 16, 50 y 84 de la GIRF acumulada del TVAR, régimen normal, por choque y variable."""
    b_exo = np.zeros((4, 4), dtype=int)
    b_exo[0, 1:] = 1                        # la anomalía excluye PBI, inflación e ingresos
    model = ThresholdVAR(Y, threshold_var="nino12", lags=2, max_delay=4, post_draws=4000, burnin=0.5,
                         hor=12, irf_1std=0, seed=1, b_exo=b_exo, covid_mode="lenza-primiceri",
                         covid_window=("2020Q1", "2021Q4"), covid_n_free=8)
    model.sample_posterior(show_progress=False)
    out = {}
    for s in SHOCKS:
        irf = model.compute_irfs(shock="level", n_draws=200, reps=25, scale=s, n_jobs=N_JOBS,
                                 show_progress=False)
        for var in VARS:
            cum = irf["regime1"]["level"][:, :H + 1, model.names.index(var), 0].sum(axis=1)
            out[(var, s)] = np.percentile(cum, [16, 50, 84])
    return out


def plot(fits, samples, tvar, out: Path):
    grid = np.linspace(0.0, 3.8, 77)
    set_style("slides", font="sans")
    plt.rcParams.update({"savefig.dpi": 200})
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.3), constrained_layout=True)
    for ax, (var, title) in zip(axes, VARS.items()):
        mean, se = lp_response(fits[var], grid)
        ax.fill_between(grid, mean - Z68 * se, mean + Z68 * se, color=ACCENT, alpha=0.15, lw=0)
        ax.plot(grid, mean, color=ACCENT, lw=2.0, label="LP con spline (banda al 68 %)")
        q = np.array([tvar[(var, s)] for s in SHOCKS])
        ax.errorbar(SHOCKS, q[:, 1], yerr=[q[:, 1] - q[:, 0], q[:, 2] - q[:, 1]], fmt="o--",
                    color=BLUE, lw=1.2, ms=5, capsize=3, label="TVAR, régimen normal (GIRF, 68 %)")
        ax.axhline(0, color=MUTED, lw=0.7)
        for x, label in ((1.0, "moderado"), (3.0, "extremo")):
            ax.axvline(x, color=MUTED, lw=0.8, ls=":")
            ax.text(x, 1.0, label, transform=ax.get_xaxis_transform(), ha="center", va="bottom",
                    fontsize=9, color=MUTED)
        ax.plot(samples[var]["F"], np.full(len(samples[var]), 0.02), "|", color=MUTED, ms=7,
                transform=ax.get_xaxis_transform())
        ax.set_title(title, fontweight="bold", pad=14)
        ax.set_xlabel("Anomalía Niño 1+2 en $t$ (°C)")
        ax.set_xlim(grid[0], grid[-1])
    axes[0].set_ylabel("p.p., acumulado $h=0$ a $8$")
    axes[1].legend(fontsize=9, loc="lower left", frameon=False)
    fig.savefig(out)
    print(f"Figura: {out}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--out", type=Path, default=HERE / "fig_lp_nino.png")
    args = parser.parse_args()

    Y = load_data()
    fits, samples = {}, {}
    for var in VARS:
        fits[var], samples[var] = lp_cumulative(Y, var)
    tvar = tvar_responses(Y)

    first, last = samples["y"].index[[0, -1]]
    print(f"LP: t de {cd.quarter(first)} a {cd.quarter(last)}, {len(samples['y'])} trimestres "
          f"({(samples['y']['F'] > KNOT).sum()} con F_t > {KNOT:g} °C)")
    rows = {}
    for var, name in VARS.items():
        m, se = lp_response(fits[var], [1.0, 3.0])
        g, g_se = fits[var].params["F_k"], fits[var].bse["F_k"]
        rows[name] = {"LP +1 °C": m[0], "(e.e.)": se[0], "LP +3 °C": m[1], "(e.e.) ": se[1],
                      "LP 3/1": m[1] / m[0], "cambio de pendiente g": g, "t de g": g / g_se,
                      "TVAR +1 °C": tvar[(var, 1.0)][1], "TVAR +3 °C": tvar[(var, 3.0)][1],
                      "TVAR 3/1": tvar[(var, 3.0)][1] / tvar[(var, 1.0)][1]}
    print("Respuesta acumulada a 8 trimestres (p.p. de la tasa interanual)")
    print(pd.DataFrame(rows).T.round(2).to_string())

    tot = cd.small_open_economy(cd.load(), start="1992-03-01", end="2026-06-01")[["tot"]]
    specs = {"base": {}, "nudo 0.5 °C": {"knot": 0.5}, "nudo 1.5 °C": {"knot": 1.5},
             "cuatro rezagos": {"lags": 4}, "con términos de intercambio": {"controls": tot},
             "LP lineal": {"knot": None}}
    robust = {}
    for label, kw in specs.items():
        for var, name in VARS.items():
            m, se = lp_response(lp_cumulative(Y, var, **kw)[0], [3.0])
            robust.setdefault(label, {})[name] = f"{m[0]:6.1f} ({se[0]:.1f})"
    print("\nRobustez: respuesta acumulada a +3 °C (e.e.)")
    print(pd.DataFrame(robust).T.to_string())
    plot(fits, samples, tvar, args.out)


if __name__ == "__main__":
    main()
