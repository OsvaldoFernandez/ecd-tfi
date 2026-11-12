import sys
import json
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

ROOT = sys.argv[1]
OUT = f"{ROOT}/data/pico"
FILES = {
    "X": "X_demanda_neta_mw.csv",
    "Y": "Y_lmp_usd_mwh.csv",
    "Z": "Z_gco2_kwh.csv",
}
M = {k: pd.read_csv(f"{OUT}/{f}", index_col=0) for k, f in FILES.items()}
dias, horas = M["X"].index.tolist(), M["X"].columns.tolist()
flat = pd.DataFrame({k: m.values.ravel() for k, m in M.items()})
norm = (flat - flat.min()) / (flat.max() - flat.min())

print("correlaciones entre matrices (168 horas de la semana):")
print(flat.corr().round(2).to_string())

z = (flat - flat.mean()) / flat.std()
pca = PCA().fit(z)
print("\nvarianza explicada:", pca.explained_variance_ratio_.round(3))
load = pd.DataFrame(pca.components_.T, index=flat.columns, columns=[f"CP{i+1}" for i in range(len(M))])
print(load.round(3).to_string())

pc1 = load.CP1 * np.sign(load.CP1.sum())
assert (pc1 > 0).all()
w = pc1 / pc1.sum()
print("\npesos a partir de CP1:", w.round(4).to_dict())

idx = (norm * w).sum(axis=1)
q75, q25 = idx.quantile(0.75), idx.quantile(0.25)
franja = np.where(idx >= q75, "pico", np.where(idx <= q25, "valle", "intermedio"))
I = pd.DataFrame(idx.values.reshape(7, 24), index=dias, columns=horas)
F = pd.DataFrame(franja.reshape(7, 24), index=dias, columns=horas)
I.round(3).to_csv(f"{OUT}/indice_pico.csv")
F.to_csv(f"{OUT}/franja_pico_valle.csv")
print("\nindice (x100):")
print((I * 100).round(0).astype(int).to_string())
print("\nfranjas:")
print(F.replace({"pico": "P", "valle": "v", "intermedio": "."}).to_string())

json.dump({
    "dias": dias, "horas": [int(h) for h in horas],
    "matrices": {k: m.values.round(2).tolist() for k, m in M.items()},
    "pesos_acp": w.round(4).to_dict(),
    "cargas_cp1": load.CP1.round(4).to_dict(),
    "varianza_explicada": pca.explained_variance_ratio_.round(4).tolist(),
    "correlaciones": flat.corr().round(3).to_dict(),
}, open(f"{OUT}/matrices.json", "w"), ensure_ascii=False)
