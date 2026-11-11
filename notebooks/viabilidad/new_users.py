exec(open(sys.argv[2]).read().split("d = df[df.n_prev >= 3]")[0])
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
us = pd.read_csv(sys.argv[3]); us["created_at"] = pd.to_datetime(us.created_at, format="mixed")
w0 = df.start_local.min()
new_ids = set(us[us.created_at >= w0 + pd.Timedelta(hours=8)].user_id)
df["has_sub"] = (df.has_sub.astype(str) == "t").astype(int)
df["prev_loc_rate"] = df.prev_loc_rate.fillna(df.offpeak.mean())
df["is_new"] = df.user_id.isin(new_ids)
print(f"inicio ventana {w0.date()} | usuarios con cargas: {df.user_id.nunique()} | altas en ventana con cargas: {df[df.is_new].user_id.nunique()}")
print(f"tasa valle usuarios nuevos: {df[df.is_new].offpeak.mean():.3f} vs resto {df[~df.is_new].offpeak.mean():.3f}")
feats = ["prev_off_rate", "last_off", "prev_dc_rate", "prev_s", "prev_c", "n_prev", "prev_loc_rate", "is_roaming_pay", "has_sub"]
X = lambda x: x[feats].assign(n_prev=np.log1p(x.n_prev))
for lo, hi in [(1, 3), (3, 10)]:
    d = df[df.is_new & (df.n_prev >= lo) & (df.n_prev < hi)]
    tr, te = d[d.start_local < cut], d[d.start_local >= cut]
    r = {"baseline": roc_auc_score(te.offpeak, te.prev_off_rate)}
    for name, mdl in [("logistica", make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))), ("NB", GaussianNB()), ("KNN", make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=101)))]:
        mdl.fit(X(tr), tr.offpeak); r[name] = roc_auc_score(te.offpeak, mdl.predict_proba(X(te))[:, 1])
    rng = np.random.default_rng(0); m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(X(tr), tr.offpeak)
    te = te.assign(p=m.predict_proba(X(te))[:, 1]); uids = te.user_id.unique(); diffs = []
    gb = {k: v for k, v in te.groupby("user_id")}
    for _ in range(300):
        s = pd.concat([gb[u] for u in rng.choice(uids, len(uids))])
        diffs.append(roc_auc_score(s.offpeak, s.p) - roc_auc_score(s.offpeak, s.prev_off_rate))
    lo95, hi95 = np.percentile(diffs, [2.5, 97.5])
    print(f"NUEVOS n_prev [{lo},{hi}) train={len(tr)} test={len(te)} usuarios_test={te.user_id.nunique()} pos={te.offpeak.mean():.3f}: " + " ".join(f"{k}={v:.3f}" for k, v in r.items()) + f" | dif logistica-baseline IC95 [{lo95:.3f}, {hi95:.3f}]")
d = df[df.is_new & (df.n_prev >= 1) & (df.n_prev < 3)]
tr, te = d[d.start_local < cut], d[d.start_local >= cut]
m = LogisticRegression(max_iter=2000).fit(X(tr), tr.offpeak)
te = te.assign(p=m.predict_proba(X(te))[:, 1], b=te.prev_off_rate + np.random.default_rng(0).uniform(0, 1e-6, len(te)))
u = te.sort_values("start_local").groupby("user_id").head(1)
print(f"campaña: usuarios={len(u)} tasa valle={u.offpeak.mean():.3f}")
for k in [0.10, 0.20, 0.30]:
    n = int(len(u) * k); tm, tb = u.nlargest(n, "p").offpeak.sum(), u.nlargest(n, "b").offpeak.sum()
    print(f"top {k:.0%} n={n}: modelo {tm/n:.1%} baseline {tb/n:.1%} azar {u.offpeak.mean():.1%} | +{(tm/tb-1):.0%}")
nm = us[(us.created_at >= w0)].set_index("user_id").created_at
print(f"altas por mes con al menos una carga: ~{df[df.is_new].user_id.nunique()/((df.start_local.max()-w0).days/30):.0f}")
