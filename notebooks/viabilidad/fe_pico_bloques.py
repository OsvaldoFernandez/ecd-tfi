import sys
src = open("notebooks/viabilidad/fe_pico.py").read().split("for lo, hi in [(1, 3), (3, 10)]:")[0]
exec(src)
BL = [(0, 6), (6, 10), (10, 14), (14, 18), (18, 21), (21, 24)]
hh = df.start_local.dt.hour
for a, b in BL:
    df[f"b{a}"] = ((hh >= a) & (hh < b)).astype(int)
g = df.groupby("user_id")
nz = df.n_prev.replace(0, np.nan)
for a, b in BL:
    df[f"prev_b{a}"] = (g[f"b{a}"].cumsum() - df[f"b{a}"]) / nz
    df[f"last_b{a}"] = g[f"b{a}"].shift()
BLK = [f"prev_b{a}" for a, _ in BL] + [f"last_b{a}" for a, _ in BL]
wd = df[df.weekend == 0]
for lo, hi in [(1, 3), (3, 10)]:
    d = wd[wd.is_new & (wd.n_prev >= lo) & (wd.n_prev < hi)]
    tr, te = d[d.start_local < cut], d[d.start_local >= cut]
    print(f"\nhabiles, nuevos, previas {lo}-{hi-1}: test={len(te)} positivos={te.y.mean():.3f} baseline={roc_auc_score(te.y, te.prev_y):.3f}")
    for sname, cols in {"historial": HIST, "historial+bloques": HIST + BLK, "base+bloques": BASE + BLK}.items():
        res = []
        for mname, m in models():
            m.fit(X(tr, cols), tr.y); res.append(f"{mname.split(' ')[0]}={roc_auc_score(te.y, m.predict_proba(X(te, cols))[:, 1]):.3f}")
        print(f"  {sname:<20} " + " ".join(res))
    if lo == 1:
        rng = np.random.default_rng(0); m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000)).fit(X(tr, HIST + BLK), tr.y)
        te = te.assign(p=m.predict_proba(X(te, HIST + BLK))[:, 1]); gb = {k: v for k, v in te.groupby("user_id")}; uids = list(gb); diffs = []
        for _ in range(300):
            s = pd.concat([gb[u] for u in rng.choice(uids, len(uids))]); diffs.append(roc_auc_score(s.y, s.p) - roc_auc_score(s.y, s.prev_y))
        print(f"  dif logistica(historial+bloques) - baseline: IC95 [{np.percentile(diffs, 2.5):.3f}, {np.percentile(diffs, 97.5):.3f}]")
        u = te.sort_values("start_local").groupby("user_id").head(1).assign(b=lambda x: x.prev_y + np.random.default_rng(1).uniform(0, 1e-6, len(x)))
        for k in [0.1, 0.2, 0.3]:
            n = int(len(u) * k); tm, tb = u.nlargest(n, "p").y.sum(), u.nlargest(n, "b").y.sum()
            print(f"  campaña top {k:.0%} (n={n} de {len(u)} usuarios, tasa {u.y.mean():.3f}): modelo {tm/n:.1%} baseline {tb/n:.1%} -> {tm/tb-1:+.0%}")
