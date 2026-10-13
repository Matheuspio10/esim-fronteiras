import json, sys, numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components, shortest_path
d = json.load(open(sys.argv[1], encoding="utf-8"))["regions"]
ids = [r["id"] for r in d]; ix = {v: i for i, v in enumerate(ids)}; n = len(ids)
rows, cols = [], []
for r in d:
    for nb in r["neighbors"]:
        rows.append(ix[r["id"]]); cols.append(ix[nb["id"]])
A = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n))
nc, lab = connected_components(A, directed=False)
sizes = np.bincount(lab); print("components:", nc, sorted(sizes, reverse=True)[:10])
pos = np.zeros((n, 2))
def smacof(Dm, iters=400):
    m = len(Dm)
    if m == 1: return np.zeros((1, 2))
    # classical MDS init
    J = np.eye(m) - 1/m; B = -0.5 * J @ (Dm**2) @ J
    w, v = np.linalg.eigh(B); X = v[:, -2:] * np.sqrt(np.maximum(w[-2:], 1e-9))
    W = np.where(Dm > 0, Dm**-2.0, 0.0)
    V = -W.copy(); np.fill_diagonal(V, W.sum(1)); Vp = np.linalg.pinv(V)
    for _ in range(iters):
        dist = np.sqrt(((X[:, None] - X[None]) ** 2).sum(-1)); dist[dist == 0] = 1e-9
        Bm = -W * Dm / dist; np.fill_diagonal(Bm, 0); np.fill_diagonal(Bm, -Bm.sum(1))
        X = Vp @ Bm @ X
    return X
comps = sorted(range(nc), key=lambda c: -sizes[c])
offx = 0
for k, c in enumerate(comps):
    idx = np.where(lab == c)[0]
    Dm = shortest_path(A[idx][:, idx], directed=False, unweighted=True)
    X = smacof(Dm)
    X -= X.min(0)
    if k == 0: main_w = X[:, 0].max(); X_main_h = X[:, 1].max(); pos[idx] = X; offx = main_w + 3; offy = 0
    else:
        pos[idx] = X + [offx, offy]; offy += X[:, 1].max() + 2
        if offy > X_main_h: offy = 0; offx += 4
json.dump({str(ids[i]): [round(float(pos[i, 0]), 3), round(float(pos[i, 1]), 3)] for i in range(n)},
          open(sys.argv[2], "w"))
# quality: mean edge length vs std
el = np.array([np.linalg.norm(pos[a] - pos[b]) for a, b in zip(rows, cols)])
print("edge len mean %.2f sd %.2f max %.2f" % (el.mean(), el.std(), el.max()))
