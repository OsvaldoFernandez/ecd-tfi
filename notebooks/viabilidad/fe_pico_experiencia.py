import sys
src = open("notebooks/viabilidad/fe_pico.py").read().split("for lo, hi in [(1, 3), (3, 10)]:")[0]
exec(src)
wd = df[df.weekend == 0]
d = wd[wd.is_new & (wd.n_prev >= 1) & (wd.n_prev < 3)]
tr, te = d[d.start_local < cut], d[d.start_local >= cut]
m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000)).fit(X(tr, HIST), tr.y)
te = te.assign(p=m.predict_proba(X(te, HIST))[:, 1])
grupos = {
    "auto del año o 1 año (car_age<=1)": (te.car_unknown == 0) & (te.car_age <= 1),
    "auto de 3+ años al darse de alta": (te.car_unknown == 0) & (te.car_age >= 3),
    "sin auto informado": te.car_unknown == 1,
    "alta via Lyft/Hertz": (te.via_lyft + te.via_hertz) > 0,
}
for k, msk in grupos.items():
    s = te[msk]
    if s.y.nunique() < 2 or len(s) < 100:
        print(f"{k}: n={len(s)} insuficiente"); continue
    print(f"{k}: n={len(s)} usuarios={s.user_id.nunique()} pico={s.y.mean():.3f} baseline={roc_auc_score(s.y, s.prev_y):.3f} logistica={roc_auc_score(s.y, s.p):.3f} dif={roc_auc_score(s.y, s.p)-roc_auc_score(s.y, s.prev_y):+.3f}")
us = df[df.is_new].groupby("user_id").agg(car_age=("car_age", "first"), unk=("car_unknown", "first"))
print("distribucion car_age (usuarios nuevos con auto informado):", us[us.unk == 0].car_age.value_counts(bins=[-2, 0, 1, 2, 4, 8, 16]).sort_index().to_dict())
