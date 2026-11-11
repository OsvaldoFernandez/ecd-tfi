import sys
src = open("notebooks/viabilidad/fe_pico.py").read().split("for lo, hi in [(1, 3), (3, 10)]:")[0]
exec(src)
wd = df[df.weekend == 0]
for lo, hi in [(1, 3), (1, 10)]:
    d = wd[wd.is_new & (wd.n_prev >= lo) & (wd.n_prev < hi)]
    tr, te = d[d.start_local < cut], d[d.start_local >= cut]
    z = te[te.prev_y == 0]
    for mname, m in models()[:3]:
        m.fit(X(tr, HIST), tr.y)
        p = m.predict_proba(X(z, HIST))[:, 1]
        print(f"previas {lo}-{hi-1}, usuarios sin pico previo: n={len(z)} usuarios={z.user_id.nunique()} positivos={z.y.mean():.3f} | baseline=0.500 {mname}={roc_auc_score(z.y, p):.3f}")
    m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000)).fit(X(tr, HIST), tr.y)
    zz = z.assign(p=m.predict_proba(X(z, HIST))[:, 1]).sort_values("start_local").groupby("user_id").head(1)
    for k in [0.1, 0.2, 0.3]:
        n = int(len(zz) * k)
        print(f"   campaña top {k:.0%} (n={n} de {len(zz)}): modelo {zz.nlargest(n, 'p').y.mean():.1%} vs al azar {zz.y.mean():.1%} -> x{zz.nlargest(n, 'p').y.mean()/zz.y.mean():.1f}")
    print(f"   share de usuarios de prueba sin pico previo: {te.groupby('user_id').prev_y.first().eq(0).mean():.1%}")
