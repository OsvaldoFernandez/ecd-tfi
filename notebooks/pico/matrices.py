import sys
import glob
import zipfile
import numpy as np
import pandas as pd

ROOT = sys.argv[1]
TZ = "America/Los_Angeles"
START, END = pd.Timestamp("2025-11-01", tz=TZ), pd.Timestamp("2026-11-01", tz=TZ)
DIAS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

G_PER_KWH = {
    "Net Generation (MW) from Natural Gas": 116.65 * 7781 / 1e6 * 453.592,
    "Net Generation (MW) from Coal": 211.63 * 10647 / 1e6 * 453.592,
    "Net Generation (MW) from All Petroleum Products": 163.45 * 10969 / 1e6 * 453.592,
}


def hour_of_week(ts):
    return pd.DataFrame({"dow": ts.dt.dayofweek, "hour": ts.dt.hour})


def to_matrix(df, col, how="mean"):
    m = df.groupby(["dow", "hour"])[col].agg(how).unstack("hour")
    m.index = [DIAS[i] for i in m.index]
    return m


def in_window(ts):
    return (ts >= START) & (ts < END)


def eia():
    files = sorted(glob.glob(f"{ROOT}/data/external/eia/EIA930_BALANCE_*.csv"))
    d = pd.concat([pd.read_csv(f, low_memory=False, thousands=",") for f in files])
    d = d[d["Balancing Authority"] == "CISO"].copy()
    end_utc = pd.to_datetime(d["UTC Time at End of Hour"], format="%m/%d/%Y %I:%M:%S %p", utc=True)
    d["ts"] = (end_utc - pd.Timedelta(hours=1)).dt.tz_convert(TZ)
    d = d[in_window(d.ts)].drop_duplicates("ts")
    num = lambda c: pd.to_numeric(d[c], errors="coerce").fillna(0) if c in d else 0
    solar = num("Net Generation (MW) from Solar without Integrated Battery Storage") + num("Net Generation (MW) from Solar with Integrated Battery Storage")
    wind = num("Net Generation (MW) from Wind without Integrated Battery Storage") + num("Net Generation (MW) from Wind with Integrated Battery Storage")
    d["net_demand_mw"] = pd.to_numeric(d["Demand (MW) (Adjusted)"], errors="coerce") - solar - wind
    gen = pd.to_numeric(d["Net Generation (MW) (Adjusted)"], errors="coerce")
    d["g_co2_kwh"] = sum(num(c) * f for c, f in G_PER_KWH.items()) / gen
    d = pd.concat([d.reset_index(drop=True), hour_of_week(d.ts.reset_index(drop=True))], axis=1)
    return d


def lmp():
    rows = []
    for f in sorted(glob.glob(f"{ROOT}/data/external/caiso/*.zip")):
        with zipfile.ZipFile(f) as z:
            for name in z.namelist():
                x = pd.read_csv(z.open(name))
                rows.append(x[x.LMP_TYPE == "LMP"][["INTERVALSTARTTIME_GMT", "NODE", "MW"]])
    d = pd.concat(rows)
    d["ts"] = pd.to_datetime(d.INTERVALSTARTTIME_GMT, utc=True).dt.tz_convert(TZ)
    d = d[in_window(d.ts)].groupby("ts", as_index=False).MW.mean().rename(columns={"MW": "usd_mwh"})
    return pd.concat([d, hour_of_week(d.ts)], axis=1)


def evcs(max_hours=12):
    c = pd.read_csv(f"{ROOT}/data/charges_all_12m.csv")
    c = c[(c.kwh > 0) & c.duration.between(60, max_hours * 3600)].copy()
    start = pd.to_datetime(c.start_local, format="mixed").dt.tz_localize(TZ, ambiguous="NaT", nonexistent="shift_forward")
    c = c.assign(s=start, e=start + pd.to_timedelta(c.duration, unit="s")).dropna(subset=["s"])
    c = c[in_window(c.s)]
    hours = pd.DataFrame({"s": c.s.reset_index(drop=True), "e": c.e.reset_index(drop=True)})
    hours["h0"] = hours.s.dt.floor("h")
    hours["n"] = ((hours.e - hours.h0) / pd.Timedelta(hours=1)).apply(np.ceil).astype(int)
    rep = hours.loc[hours.index.repeat(hours.n)].copy()
    rep["k"] = rep.groupby(level=0).cumcount()
    rep["bucket"] = rep.h0 + pd.to_timedelta(rep.k, unit="h")
    rep["frac"] = (np.minimum(rep.e, rep.bucket + pd.Timedelta(hours=1)) - np.maximum(rep.s, rep.bucket)) / pd.Timedelta(hours=1)
    occ = rep.groupby("bucket").frac.sum()
    full = pd.date_range(START, END, freq="h", inclusive="left")
    occ = occ.reindex(full, fill_value=0).rename("sesiones_activas").reset_index().rename(columns={"index": "ts"})
    return pd.concat([occ, hour_of_week(occ.ts)], axis=1), len(c)


if __name__ == "__main__":
    out = f"{ROOT}/data/pico"
    import os
    os.makedirs(out, exist_ok=True)
    parts = sys.argv[2].split(",")
    if "eia" in parts:
        d = eia()
        print(f"EIA CISO horas: {len(d)} desde {d.ts.min()} hasta {d.ts.max()}")
        to_matrix(d, "net_demand_mw").round(0).to_csv(f"{out}/X_demanda_neta_mw.csv")
        to_matrix(d, "g_co2_kwh").round(1).to_csv(f"{out}/Z_gco2_kwh.csv")
        print(to_matrix(d, "net_demand_mw").round(-2).astype(int).to_string())
        print(to_matrix(d, "g_co2_kwh").round(0).astype(int).to_string())
    if "lmp" in parts:
        d = lmp()
        print(f"LMP horas: {len(d)} desde {d.ts.min()} hasta {d.ts.max()}")
        to_matrix(d, "usd_mwh").round(2).to_csv(f"{out}/Y_lmp_usd_mwh.csv")
        print(to_matrix(d, "usd_mwh").round(0).astype(int).to_string())
    if "evcs" in parts:
        d, n = evcs()
        print(f"EVCS cargas usadas: {n} | horas: {len(d)}")
        to_matrix(d, "sesiones_activas").round(2).to_csv(f"{out}/W_sesiones_activas_evcs.csv")
        print(to_matrix(d, "sesiones_activas").round(0).astype(int).to_string())
