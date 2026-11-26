"""Derive figure assets from real Cowen frames and the fsaverage / MNI templates."""
import os, sys, numpy as np, cv2
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, 'assets')
SRC = sys.argv[1] if len(sys.argv) > 1 else None  # folder with cowen_XXXX.mp4 (optional)

def sq(f):
    h, w = f.shape[:2]; s = min(h, w); y0 = (h - s) // 2; x0 = (w - s) // 2
    return cv2.resize(f[y0:y0 + s, x0:x0 + s], (448, 448), interpolation=cv2.INTER_AREA)

# motion energy (mean absolute temporal difference of luminance) for video 1374
if SRC and os.path.exists(os.path.join(SRC, 'cowen_1374.mp4')):
    cap = cv2.VideoCapture(os.path.join(SRC, 'cowen_1374.mp4')); prev = None; acc = None; n = 0
    while True:
        ok, f = cap.read()
        if not ok: break
        g = cv2.cvtColor(sq(f), cv2.COLOR_BGR2GRAY).astype(float)
        if prev is not None:
            d = np.abs(g - prev); acc = d if acc is None else acc + d; n += 1
        prev = g
    me = cv2.GaussianBlur(acc / n, (0, 0), 6)
    me = (me - me.min()) / (me.max() - me.min() + 1e-9)
    plt.imsave(os.path.join(A, 'cowen_1374_motion.png'), me, cmap='magma')

# tubelet grid and 90 % tube mask on a real frame
fr = cv2.cvtColor(cv2.imread(os.path.join(A, 'cowen_1374_f3.png')), cv2.COLOR_BGR2RGB)
g = fr.copy(); step = 448 // 14
for k in range(1, 14):
    g[k * step - 1:k * step + 1, :] = 255; g[:, k * step - 1:k * step + 1] = 255
cv2.imwrite(os.path.join(A, 'cowen_1374_grid.png'), cv2.cvtColor(g, cv2.COLOR_RGB2BGR))
rng = np.random.default_rng(4); keep = rng.random((14, 14)) < 0.10
m = fr.copy()
for i in range(14):
    for j in range(14):
        if not keep[i, j]:
            m[i * step:(i + 1) * step, j * step:(j + 1) * step] = (m[i * step:(i + 1) * step, j * step:(j + 1) * step] * 0.15 + 200 * 0.85).astype(np.uint8)
for k in range(1, 14):
    m[k * step - 1:k * step + 1, :] = 255; m[:, k * step - 1:k * step + 1] = 255
cv2.imwrite(os.path.join(A, 'cowen_1374_tubemask.png'), cv2.cvtColor(m, cv2.COLOR_RGB2BGR))

# illustrative partition map on the real fsaverage5 surface
from nilearn import datasets, surface, plotting
fs = datasets.fetch_surf_fsaverage('fsaverage5')
mesh = surface.load_surf_mesh(fs.pial_left)
x, y, z = (mesh.coordinates if hasattr(mesh, 'coordinates') else mesh[0]).T
sulc = surface.load_surf_data(fs.sulc_left)
lab = np.zeros_like(x)
lab[(y < -72)] = 1                                                        # head unique (visual)
lab[(x < -30) & (y > -68) & (y < -30) & (z > 5) & (z < 45)] = 2            # shared (temporo-parietal)
lab[(y > 10) & (z > 0) & (x < -25)] = 3                                    # rating unique (frontal)
def render(vals, cmap, fname, vmin, vmax, thr=None):
    fig = plt.figure(figsize=(4, 3), dpi=300); ax = fig.add_subplot(111, projection='3d')
    plotting.plot_surf(fs.infl_left, surf_map=vals, bg_map=sulc, hemi='left', view='lateral', cmap=cmap,
                       vmin=vmin, vmax=vmax, bg_on_data=True, axes=ax, figure=fig, colorbar=False, threshold=thr)
    fig.savefig(os.path.join(A, fname), transparent=True, bbox_inches='tight', pad_inches=0); plt.close(fig)
render(lab, ListedColormap(['#E07B00', '#2A9D8F', '#6A4FA3']), 'cortex_partition.png', 0.5, 3.5, thr=0.5)
render(sulc, 'Greys', 'cortex_sulc.png', -2, 2)
print('assets ok')
