exec(open(sys.argv[2]).read().split("d = df[df.n_prev >= 3]")[0])
df["has_sub"] = (df.has_sub.astype(str) == "t").astype(int)
df["prev_loc_rate"] = df.prev_loc_rate.fillna(df.offpeak.mean())
feats = ["prev_off_rate", "last_off", "prev_dc_rate", "prev_s", "prev_c", "n_prev", "prev_loc_rate", "is_roaming_pay", "has_sub"]
X = lambda x: x[feats].assign(n_prev=np.log1p(x.n_prev))
d = df[(df.n_prev >= 1) & (df.n_prev < 3)]
tr, te = d[d.start_local < cut], d[d.start_local >= cut]
m = LogisticRegression(max_iter=2000).fit(X(tr), tr.offpeak)
te = te.assign(p=m.predict_proba(X(te))[:, 1], b=te.prev_off_rate + np.random.default_rng(0).uniform(0, 1e-6, len(te)))
u = te.sort_values("start_local").groupby("user_id").head(1)
print(f"usuarios en prueba (1ra carga del periodo de prueba, 1-2 previas): {len(u)} | tasa valle {u.offpeak.mean():.3f}")
print(f"AUC a nivel usuario: modelo {roc_auc_score(u.offpeak, u.p):.3f} baseline {roc_auc_score(u.offpeak, u.b):.3f}")
P = u.offpeak.sum()
for k in [0.05, 0.10, 0.20, 0.30]:
    n = int(len(u) * k)
    tm, tb = u.nlargest(n, "p").offpeak.sum(), u.nlargest(n, "b").offpeak.sum()
    print(f"top {k:.0%} (n={n}): aciertos modelo {tm} ({tm/n:.1%}) vs baseline {tb} ({tb/n:.1%}) vs azar {n*u.offpeak.mean():.0f} | recall modelo {tm/P:.1%} baseline {tb/P:.1%}")
first = df.groupby("user_id").start_local.min()
w = first[(first >= df.start_local.min() + pd.Timedelta(days=90))]
print(f"usuarios cuya 1ra carga en la extraccion es posterior a los primeros 90 dias: {len(w)} en {(df.start_local.max()-df.start_local.min()-pd.Timedelta(days=90)).days} dias -> ~{len(w)/((df.start_local.max()-df.start_local.min()).days-90)*30:.0f}/mes")
