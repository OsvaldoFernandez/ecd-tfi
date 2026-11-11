import sys
src = open("notebooks/viabilidad/fe_pico.py").read().split("for lo, hi in [(1, 3), (3, 10)]:")[0]
exec(src)
wd = df[df.weekend == 0].copy()
gw = wd.groupby("user_id")
wd["n_prev_wd"] = gw.cumcount()
nzw = wd.n_prev_wd.replace(0, np.nan)
wd["prev_y_wd"] = (gw.y.cumsum() - wd.y) / nzw
wd["last_y_wd"] = gw.y.shift()
HW = HIST + ["prev_y_wd", "last_y_wd"]
for lo, hi in [(1, 3), (3, 10)]:
    d = wd[wd.is_new & (wd.n_prev >= lo) & (wd.n_prev < hi)].copy()
    d["prev_y_wd"] = d.prev_y_wd.fillna(d.prev_y); d["last_y_wd"] = d.last_y_wd.fillna(d.last_y)
    tr, te = d[d.start_local < cut], d[d.start_local >= cut]
    b1, b2 = roc_auc_score(te.y, te.prev_y), roc_auc_score(te.y, te.prev_y_wd)
    print(f"\nhabiles, nuevos, previas {lo}-{hi-1}: train={len(tr)} test={len(te)} usuarios_test={te.user_id.nunique()} positivos={te.y.mean():.3f} | baseline={b1:.3f} baseline_habiles={b2:.3f}")
    for sname, cols in {"base": BASE, "historial": HIST, "historial+habiles": HW, "historial+habiles+usuario": HW + USER[len(HIST):]}.items():
        res = []
        for mname, m in models():
            m.fit(X(tr, cols), tr.y); res.append(f"{mname.split(' ')[0]}={roc_auc_score(te.y, m.predict_proba(X(te, cols))[:, 1]):.3f}")
        print(f"  {sname:<27} " + " ".join(res))
    rng = np.random.default_rng(0); m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000)).fit(X(tr, HW), tr.y)
    te = te.assign(p=m.predict_proba(X(te, HW))[:, 1]); gb = {k: v for k, v in te.groupby("user_id")}; uids = list(gb); diffs = []
    for _ in range(300):
        s = pd.concat([gb[u] for u in rng.choice(uids, len(uids))]); diffs.append(roc_auc_score(s.y, s.p) - roc_auc_score(s.y, s.prev_y_wd))
    print(f"  dif logistica(historial+habiles) - baseline_habiles: IC95 [{np.percentile(diffs, 2.5):.3f}, {np.percentile(diffs, 97.5):.3f}]")
