"""Derive figure assets from the fsaverage / MNI templates. Video frames are drawn as schematics (kit.frame_icon)."""
import os
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, 'assets')

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
