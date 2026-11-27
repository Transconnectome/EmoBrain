"""Rebuild all EmoBrain methods figures.

Real inputs:
  - fsaverage5 surface and MNI152 template (bundled with nilearn)
  - captions and Cowen & Keltner (2017) ratings of video 1374 are typed into the figure code
Video frames are drawn as schematic boxes (kit.frame_icon); no stimulus video is used.
Run fetch_assets.py once, then this script.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matplotlib.backends.backend_pdf import PdfPages
from kit import OUT
from fig1 import fig1
from fig2 import fig2
from fig5 import fig5
from figs34 import fig3a, fig3b, fig3c, fig4a, fig4b

figs = {k: f() for k, f in [('1', fig1), ('2', fig2), ('3a', fig3a), ('3b', fig3b), ('3c', fig3c),
                             ('4a', fig4a), ('4b', fig4b), ('5', fig5)]}
with PdfPages(os.path.join(OUT, 'emobrain_methods_figures.pdf')) as pdf:
    for k in ('2', '3a', '3b', '4a', '4b', '5'):
        pdf.savefig(figs[k])
with PdfPages(os.path.join(OUT, 'emobrain_head_interpretation.pdf')) as pdf:
    for k in ('3a', '3b'):
        pdf.savefig(figs[k])
print('figures written to', OUT)
