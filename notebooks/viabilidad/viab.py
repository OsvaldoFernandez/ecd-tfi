import sys, numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
df = pd.read_csv(sys.argv[1]); df["start_local"] = pd.to_datetime(df.start_local, format="mixed")
n0 = len(df)
df = df[(df.kwh > 0)].sort_values(["user_id", "start_local"]).reset_index(drop=True)
h = df.start_local.dt.hour
df["offpeak"] = ((h >= 22) | (h < 6)).astype(int)
df["is_dc"] = df.charger_type.fillna("").str.startswith("dc").astype(int)
df["is_roaming_pay"] = df.payment_method.fillna("").str.startswith("Roaming").astype(int)
g = df.groupby("user_id")
df["n_prev"] = g.cumcount()
df["prev_off_rate"] = (g.offpeak.cumsum() - df.offpeak) / df.n_prev.replace(0, np.nan)
df["last_off"] = g.offpeak.shift()
df["prev_dc_rate"] = (g.is_dc.cumsum() - df.is_dc) / df.n_prev.replace(0, np.nan)
ang = 2 * np.pi * h / 24
df["s"], df["c"] = np.sin(ang), np.cos(ang)
for k in ["s", "c"]:
    df[f"prev_{k}"] = (g[k].cumsum() - df[k]) / df.n_prev.replace(0, np.nan)
df["days_since_last"] = (df.start_local - g.start_local.shift()).dt.total_seconds() / 86400
cut = df.start_local.max() - pd.Timedelta(days=91)
loc_rate = df[df.start_local < cut].groupby("location_id").offpeak.mean()
df["loc_off_rate"] = df.location_id.map(loc_rate)
df["prev_loc_rate"] = g.loc_off_rate.transform(lambda x: x.expanding().mean().shift())
print(f"filas: {n0} -> kwh>0: {len(df)} | usuarios: {df.user_id.nunique()}")
print(f"tasa offpeak global: {df.offpeak.mean():.3f}")
uc = g.size()
print(f"usuarios con >=5 cargas: {(uc>=5).sum()} ({uc[uc>=5].sum()} cargas) | >=10: {(uc>=10).sum()}")
print("offpeak por charger_type:", df.groupby(df.is_dc.map({0:'ac',1:'dc'})).offpeak.mean().round(3).to_dict())
d = df[df.n_prev >= 3].dropna(subset=["prev_loc_rate", "days_since_last"])
tr, te = d[d.start_local < cut], d[d.start_local >= cut]
print(f"train: {len(tr)} ({tr.offpeak.mean():.3f} pos) | test: {len(te)} ({te.offpeak.mean():.3f} pos), corte {cut.date()}")
print(f"AUC baseline last_off: {roc_auc_score(te.offpeak, te.last_off):.3f}")
print(f"AUC baseline prev_off_rate: {roc_auc_score(te.offpeak, te.prev_off_rate):.3f}")
feats = ["prev_off_rate", "last_off", "prev_dc_rate", "prev_s", "prev_c", "n_prev", "days_since_last", "prev_loc_rate", "is_roaming_pay"]
X = lambda x: x[feats].assign(n_prev=np.log1p(x.n_prev), days_since_last=np.log1p(x.days_since_last))
m = LogisticRegression(max_iter=2000).fit(X(tr), tr.offpeak)
p = m.predict_proba(X(te))[:, 1]
print(f"AUC logistica (test): {roc_auc_score(te.offpeak, p):.3f}")
ub = te.groupby("user_id").size()
w = 1 / te.user_id.map(ub)
print(f"AUC logistica ponderada por usuario: {roc_auc_score(te.offpeak, p, sample_weight=w):.3f}")
m2 = LogisticRegression(max_iter=2000).fit(X(tr).drop(columns=["prev_loc_rate"]), tr.offpeak)
print(f"AUC sin variable de ubicacion: {roc_auc_score(te.offpeak, m2.predict_proba(X(te).drop(columns=['prev_loc_rate']))[:,1]):.3f}")
print(f"top 1% usuarios aportan {ub.sort_values(ascending=False).head(max(1,len(ub)//100)).sum()/len(te):.2%} de test")
from sklearn.metrics import average_precision_score as ap
te = te.assign(p=p)
print(f"PR-AUC logistica: {ap(te.offpeak, p):.3f} | baseline rate: {ap(te.offpeak, te.prev_off_rate):.3f} | azar: {te.offpeak.mean():.3f}")
for lo, hi in [(3, 10), (10, 30), (30, 10**6)]:
    b = te[(te.n_prev >= lo) & (te.n_prev < hi)]
    print(f"n_prev [{lo},{hi}): n={len(b)} pos={b.offpeak.mean():.3f} AUC modelo={roc_auc_score(b.offpeak, b.p):.3f} baseline={roc_auc_score(b.offpeak, b.prev_off_rate):.3f}")
u = df[df.start_local < cut].groupby("user_id").agg(n=("offpeak", "size"), r=("offpeak", "mean"))
u = u[u.n >= 5]
print("distribucion de usuarios (>=5 cargas) por % offpeak:", pd.cut(u.r, [-.01, 0, .1, .3, .7, 1]).value_counts().sort_index().to_dict())
print("coeficientes:", dict(zip(feats, m.coef_[0].round(3))))
