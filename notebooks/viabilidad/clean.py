exec(open(sys.argv[2]).read().split("d = df[df.n_prev >= 3]")[0])
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
df["has_sub"] = (df.has_sub.astype(str) == "t").astype(int)
df["prev_loc_rate"] = df.prev_loc_rate.fillna(df.offpeak.mean())
feats = ["prev_off_rate", "last_off", "prev_dc_rate", "prev_s", "prev_c", "n_prev", "prev_loc_rate", "is_roaming_pay", "has_sub"]
X = lambda x: x[feats].assign(n_prev=np.log1p(x.n_prev))
for lo, hi in [(1, 3), (3, 10), (10, 30), (30, 10**6), (1, 10**6)]:
    d = df[(df.n_prev >= lo) & (df.n_prev < hi)]
    tr, te = d[d.start_local < cut], d[d.start_local >= cut]
    r = {"baseline": roc_auc_score(te.offpeak, te.prev_off_rate)}
    for name, mdl in [("logistica", make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))),
                      ("NB", GaussianNB()),
                      ("KNN", make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=101))),
                      ("GB", HistGradientBoostingClassifier())]:
        trs = tr.sample(min(len(tr), 60000), random_state=0) if name == "KNN" else tr
        mdl.fit(X(trs), trs.offpeak)
        r[name] = roc_auc_score(te.offpeak, mdl.predict_proba(X(te))[:, 1])
    print(f"n_prev [{lo},{hi}) test n={len(te)}: " + " ".join(f"{k}={v:.3f}" for k, v in r.items()))
