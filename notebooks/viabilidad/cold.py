exec(open(sys.argv[2]).read().split("d = df[df.n_prev >= 3]")[0])
df["has_sub"] = (df.has_sub.astype(str) == "t").astype(int)
d = df[(df.n_prev >= 1) & (df.n_prev < 3)].copy()
d["prev_loc_rate"] = d.prev_loc_rate.fillna(df.offpeak.mean())
d["days_since_last"] = d.days_since_last.fillna(0)
tr, te = d[d.start_local < cut], d[d.start_local >= cut]
feats = ["prev_off_rate", "last_off", "prev_dc_rate", "prev_s", "prev_c", "n_prev", "days_since_last", "prev_loc_rate", "is_roaming_pay", "has_sub"]
X = lambda x: x[feats].assign(days_since_last=np.log1p(x.days_since_last))
m = LogisticRegression(max_iter=2000).fit(X(tr), tr.offpeak)
p = m.predict_proba(X(te))[:, 1]
print(f"n_prev 1-2 -> test n={len(te)} usuarios={te.user_id.nunique()} pos={te.offpeak.mean():.3f}")
print(f"AUC baseline prev_off_rate: {roc_auc_score(te.offpeak, te.prev_off_rate):.3f}")
print(f"AUC logistica: {roc_auc_score(te.offpeak, p):.3f}")
from sklearn.ensemble import HistGradientBoostingClassifier
g2 = HistGradientBoostingClassifier().fit(X(tr), tr.offpeak)
print(f"AUC gradient boosting (referencia, no es de la materia): {roc_auc_score(te.offpeak, g2.predict_proba(X(te))[:,1]):.3f}")
q = te.days_since_last * 24
print(f"test con <1h desde la carga anterior: {(q<1).mean():.1%} | <6h: {(q<6).mean():.1%}")
for thr in [1, 6]:
    trf, tef = tr[tr.days_since_last*24 >= thr], te[te.days_since_last*24 >= thr]
    ml = LogisticRegression(max_iter=2000).fit(X(trf), trf.offpeak)
    mg = HistGradientBoostingClassifier().fit(X(trf), trf.offpeak)
    print(f"excluyendo <{thr}h: n={len(tef)} pos={tef.offpeak.mean():.3f} baseline={roc_auc_score(tef.offpeak, tef.prev_off_rate):.3f} logistica={roc_auc_score(tef.offpeak, ml.predict_proba(X(tef))[:,1]):.3f} GB={roc_auc_score(tef.offpeak, mg.predict_proba(X(tef))[:,1]):.3f}")
full = df[df.n_prev >= 3].dropna(subset=["prev_loc_rate", "days_since_last"])
full = full[full.days_since_last*24 >= 6]
trF, teF = full[full.start_local < cut], full[full.start_local >= cut]
fF = [f for f in feats if f != "has_sub"]
XF = lambda x: x[fF].assign(days_since_last=np.log1p(x.days_since_last))
mg = HistGradientBoostingClassifier().fit(XF(trF), trF.offpeak)
ml = LogisticRegression(max_iter=2000).fit(XF(trF), trF.offpeak)
print(f"n_prev>=3 excluyendo <6h: n={len(teF)} baseline={roc_auc_score(teF.offpeak, teF.prev_off_rate):.3f} logistica={roc_auc_score(teF.offpeak, ml.predict_proba(XF(teF))[:,1]):.3f} GB={roc_auc_score(teF.offpeak, mg.predict_proba(XF(teF))[:,1]):.3f}")
