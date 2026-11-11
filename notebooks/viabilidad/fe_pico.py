import sys
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score

ROOT = sys.argv[1]
DIAS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

F = pd.read_csv(f"{ROOT}/data/pico/franja_pico_valle.csv", index_col=0)
I = pd.read_csv(f"{ROOT}/data/pico/indice_pico.csv", index_col=0)
is_pico = {(DIAS.index(d), int(h)): F.loc[d, h] == "pico" for d in F.index for h in F.columns}
idx_val = {(DIAS.index(d), int(h)): I.loc[d, h] for d in I.index for h in I.columns}

df = pd.read_csv(f"{ROOT}/data/charges_12m.csv")
df["start_local"] = pd.to_datetime(df.start_local, format="mixed")
df = df[df.kwh > 0].sort_values(["user_id", "start_local"]).reset_index(drop=True)
h, dow = df.start_local.dt.hour, df.start_local.dt.dayofweek
key = list(zip(dow, h))
df["y"] = [int(is_pico[k]) for k in key]
df["idx"] = [idx_val[k] for k in key]
df["weekend"] = (dow >= 5).astype(int)
df["evening_wd"] = ((dow < 5) & (h >= 17)).astype(int)
df["is_dc"] = df.charger_type.fillna("").str.startswith("dc").astype(int)
df["is_roaming_pay"] = df.payment_method.fillna("").str.startswith("Roaming").astype(int)
df["has_sub"] = (df.has_sub.astype(str) == "t").astype(int)
ang = 2 * np.pi * h / 24
df["s"], df["c"] = np.sin(ang), np.cos(ang)
df["log_dur"] = np.log1p(df.duration.clip(lower=0))
df["log_kwh"] = np.log1p(df.kwh)

g = df.groupby("user_id")
df["n_prev"] = g.cumcount()
nz = df.n_prev.replace(0, np.nan)
prev_mean = lambda col: (g[col].cumsum() - df[col]) / nz
for col in ["y", "idx", "is_dc", "s", "c", "weekend", "evening_wd", "log_dur", "log_kwh"]:
    df[f"prev_{col}"] = prev_mean(col)
df["prev_conc"] = np.sqrt(df.prev_s ** 2 + df.prev_c ** 2)
for col in ["y", "s", "c", "weekend", "log_dur"]:
    df[f"last_{col}"] = g[col].shift()

cut = df.start_local.max() - pd.Timedelta(days=91)
loc_rate = df[df.start_local < cut].groupby("location_id").y.mean()
df["loc_rate"] = df.location_id.map(loc_rate)
df["prev_loc_rate"] = g.loc_rate.transform(lambda x: x.expanding().mean().shift()).fillna(df.y.mean())

u = pd.read_csv(f"{ROOT}/data/users_attrs.csv")
u["created_at"] = pd.to_datetime(u.created_at, format="mixed")
df = df.merge(u[["user_id", "created_at", "created_from", "car_year", "car_make", "first_plan"]], on="user_id", how="left")
df["is_new"] = df.created_at >= df.start_local.min() + pd.Timedelta(hours=8)
df["via_lyft"] = (df.created_from == 4).astype(int)
df["via_hertz"] = (df.created_from == 2).astype(int)
df["rideshare_plan"] = df.first_plan.fillna("").str.contains("Rideshare").astype(int)
df["car_age"] = (df.created_at.dt.year - df.car_year).clip(-1, 15)
df["car_unknown"] = df.car_age.isna().astype(int)
df["car_age"] = df.car_age.fillna(df.car_age.median())
df["tesla"] = df.car_make.fillna("").str.strip().eq("Tesla").astype(int)

BASE = ["prev_y", "last_y", "prev_is_dc", "prev_s", "prev_c", "n_prev", "prev_loc_rate", "is_roaming_pay", "has_sub"]
HIST = BASE + ["prev_idx", "prev_conc", "prev_weekend", "prev_evening_wd", "last_s", "last_c", "last_weekend", "prev_log_dur", "prev_log_kwh", "last_log_dur"]
USER = HIST + ["via_lyft", "via_hertz", "rideshare_plan", "car_age", "car_unknown", "tesla"]
SETS = {"base": BASE, "historial": HIST, "historial+usuario": USER, "historial+usuario+dia": USER + ["weekend"]}


def X(x, cols):
    return x[cols].assign(n_prev=np.log1p(x.n_prev))


def models():
    return [("logistica", make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000))),
            ("NB", GaussianNB()),
            ("KNN", make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=101))),
            ("GB (techo, no es de la materia)", HistGradientBoostingClassifier(random_state=0))]


for lo, hi in [(1, 3), (3, 10)]:
    d = df[df.is_new & (df.n_prev >= lo) & (df.n_prev < hi)]
    tr, te = d[d.start_local < cut], d[d.start_local >= cut]
    print(f"\nnuevos, cargas previas {lo}-{hi - 1}: train={len(tr)} test={len(te)} positivos={te.y.mean():.3f} | baseline={roc_auc_score(te.y, te.prev_y):.3f}")
    for sname, cols in SETS.items():
        res = []
        for mname, m in models():
            m.fit(X(tr, cols), tr.y)
            res.append(f"{mname}={roc_auc_score(te.y, m.predict_proba(X(te, cols))[:, 1]):.3f}")
        print(f"  {sname:<24} " + " ".join(res))

d = df[df.is_new & (df.n_prev >= 1) & (df.n_prev < 3)]
tr = d[d.start_local < cut]
m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000)).fit(X(tr, USER), tr.y)
coef = pd.Series(m[-1].coef_[0], index=USER).sort_values(key=abs, ascending=False)
print("\ncoeficientes estandarizados (logistica, historial+usuario, 1-2 previas):")
print(coef.round(3).head(12).to_string())
