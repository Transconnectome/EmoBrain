import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from fig1 import fig1
from fig2 import fig2
from fig3 import fig3a, fig3b
from fig4 import fig4a, fig4b
from fig5 import fig5, fig3c
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
figs = {k: f() for k, f in [('1', fig1), ('2', fig2), ('3a', fig3a), ('3b', fig3b), ('3c', fig3c), ('4a', fig4a), ('4b', fig4b), ('5', fig5)]}
with PdfPages(os.path.join(OUT, 'emobrain_methods_figures.pdf')) as pdf:
    for k in ('2', '3a', '3b', '4a', '4b', '5'):
        pdf.savefig(figs[k])
with PdfPages(os.path.join(OUT, 'emobrain_head_interpretation.pdf')) as pdf:
    for k in ('3a', '3b'):
        pdf.savefig(figs[k])
print('ok')
