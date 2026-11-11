import sys
src = open(sys.argv[2]).read().split("d = df[df.n_prev >= 3]")[0]
label = sys.argv[4]
F = pd_F = None
src = src.replace('df["offpeak"] = ((h >= 22) | (h < 6)).astype(int)',
    'import pandas as _pd\n_F = _pd.read_csv(sys.argv[5], index_col=0)\n_lab = {(d, int(c)): _F.loc[d, c] for d in _F.index for c in _F.columns}\n_D = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]\n'
    f'df["offpeak"] = [int(_lab[(_D[a], b)] == "{label}") for a, b in zip(df.start_local.dt.dayofweek, h)]')
assert "_lab" in src
exec(src)
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
us = pd.read_csv(sys.argv[3]); us["created_at"] = pd.to_datetime(us.created_at, format="mixed")
df["is_new"] = df.user_id.isin(set(us[us.created_at >= df.start_local.min() + pd.Timedelta(hours=8)].user_id))
df["has_sub"] = (df.has_sub.astype(str) == "t").astype(int)
df["prev_loc_rate"] = df.prev_loc_rate.fillna(df.offpeak.mean())
print(f"etiqueta '{label}': tasa global {df.offpeak.mean():.3f} | usuarios nuevos {df[df.is_new].offpeak.mean():.3f}")
feats = ["prev_off_rate", "last_off", "prev_dc_rate", "prev_s", "prev_c", "n_prev", "prev_loc_rate", "is_roaming_pay", "has_sub"]
X = lambda x: x[feats].assign(n_prev=np.log1p(x.n_prev))
for lo, hi in [(1, 3), (3, 10), (10, 10**6)]:
    d = df[(df.is_new if hi < 100 else True) & (df.n_prev >= lo) & (df.n_prev < hi)]
    tr, te = d[d.start_local < cut], d[d.start_local >= cut]
    r = {"baseline": roc_auc_score(te.offpeak, te.prev_off_rate)}
    for name, mdl in [("logistica", make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))), ("NB", GaussianNB()), ("KNN", make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=101)))]:
        trs = tr.sample(min(len(tr), 60000), random_state=0)
        mdl.fit(X(trs), trs.offpeak); r[name] = roc_auc_score(te.offpeak, mdl.predict_proba(X(te))[:, 1])
    print(f"  {'nuevos' if hi < 100 else 'todos'} n_prev [{lo},{hi}) test={len(te)} pos={te.offpeak.mean():.3f}: " + " ".join(f"{k}={v:.3f}" for k, v in r.items()))
