import os; os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/assets') if os.path.basename(os.getcwd()) != 'assets' else None
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from nilearn import datasets, surface, plotting
fs = datasets.fetch_surf_fsaverage('fsaverage5')
mesh = surface.load_surf_mesh(fs.pial_left)
coords = mesh.coordinates if hasattr(mesh, 'coordinates') else mesh[0]
sulc = surface.load_surf_data(fs.sulc_left)
x, y, z = coords.T
print('ranges', round(x.min()), round(x.max()), round(y.min()), round(y.max()), round(z.min()), round(z.max()))
vis = (y < -72)
assoc = (x < -30) & (y > -68) & (y < -30) & (z > 5) & (z < 45)

def render(vals, cmap, fname, vmin, vmax, thr=None):
    fig = plt.figure(figsize=(4, 3), dpi=300)
    ax = fig.add_subplot(111, projection='3d')
    plotting.plot_surf(fs.infl_left, surf_map=vals, bg_map=sulc, hemi='left', view='lateral', cmap=cmap,
                       vmin=vmin, vmax=vmax, bg_on_data=True, axes=ax, figure=fig,
                       colorbar=False, threshold=thr)
    fig.savefig(fname, transparent=True, bbox_inches='tight', pad_inches=0)
    plt.close(fig)

render(None, 'gray', 'cortex_plain.png', 0, 1)
lab = np.zeros_like(x); lab[vis] = 1; lab[assoc] = 2
render(lab, ListedColormap(['#1B9E77', '#C2477A']), 'cortex_vis_assoc.png', 0.5, 2.5, thr=0.5)
lab1 = np.zeros_like(x); lab1[assoc] = 1
render(lab1, ListedColormap(['#C0504D']), 'cortex_roi.png', 0.5, 1.5, thr=0.5)
rng = np.random.default_rng(0)
m = np.exp(-((y + 85) / 18) ** 2) * 0.9 + np.exp(-(((y + 50) / 15) ** 2 + ((z - 25) / 18) ** 2)) * 0.6 + 0.05 * rng.standard_normal(len(x))
render(m, 'YlOrRd', 'cortex_map.png', 0.3, 1.0, thr=0.3)
t1 = datasets.load_mni152_template(resolution=1)
d = t1.get_fdata()
for nm, sl in (('mni_axial', np.rot90(d[:, :, 95])), ('mni_sagittal', np.rot90(d[60, :, :]))):
    plt.imsave(nm + '.png', sl, cmap='gray', vmin=np.percentile(sl, 1), vmax=np.percentile(sl, 99.5))
print('done', d.shape)
