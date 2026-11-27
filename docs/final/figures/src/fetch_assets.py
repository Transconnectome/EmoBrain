"""Render the brain assets (fsaverage5 surface and MNI152 template, both bundled with nilearn).

No stimulus video is downloaded: video frames in the figures are schematic boxes (kit.frame_icon).
"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, 'assets'); os.makedirs(A, exist_ok=True)
subprocess.run([sys.executable, os.path.join(HERE, 'render_brain.py')], check=True, cwd=A)
subprocess.run([sys.executable, os.path.join(HERE, 'prep_assets.py')], check=True)
print('assets ready in', A)
