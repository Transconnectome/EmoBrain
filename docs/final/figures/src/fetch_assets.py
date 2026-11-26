"""Download the example Cowen & Keltner (2017) videos, extract frames, and render brain assets.

Videos come from the authors' public preview site (bsil.berkeley.edu). They are used only as
illustrative frames. The network must allow bsil.berkeley.edu and bsil.studentorg.berkeley.edu.
"""
import os, subprocess, urllib.request, numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, 'assets'); os.makedirs(A, exist_ok=True)
for v in (1374, 366, 55):
    f = f'{v:04d}'
    mp4 = os.path.join(A, f'cowen_{f}.mp4')
    if not os.path.exists(mp4):
        urllib.request.urlretrieve(f'https://bsil.berkeley.edu/wp-content/uploads/2017/09/{f}.mp4', mp4)
    cap = cv2.VideoCapture(mp4); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    for k, i in enumerate(np.linspace(0.1 * n, 0.9 * n, 6).astype(int)):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(i)); ok, fr = cap.read()
        if not ok: continue
        h, w = fr.shape[:2]; s = min(h, w); y0 = (h - s) // 2; x0 = (w - s) // 2
        cv2.imwrite(os.path.join(A, f'cowen_{f}_f{k}.png'), cv2.resize(fr[y0:y0 + s, x0:x0 + s], (448, 448), interpolation=cv2.INTER_AREA))
subprocess.run(['python3', os.path.join(HERE, 'render_brain.py')], check=True, cwd=A)
subprocess.run(['python3', os.path.join(HERE, 'prep_assets.py'), A], check=True)
print('assets ready in', A)
