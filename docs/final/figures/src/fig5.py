import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import *
from fig1 import P1374, FEAR, EMO27


def fig5():
    W, H = 180, 92
    fig, ax = canvas(W, H)

    # ---------------- a: fit two mappings ----------------
    panel(ax, 1, H - 1, 'a')
    T(ax, 7, H - 3.6, 'Fit two mappings separately, then freeze them', size=8, w='bold', ha='left')
    # lane 1: VCE readout
    y1 = 74
    T(ax, 7, y1 + 8.8, 'VCE training videos (no brain)', size=6.6, c=MODEL, w='bold', ha='left')
    tensor(ax, 7, y1 - 5, 13, 10, 'VCE\nvideos', size=6.2)
    arrow(ax, 20.5, y1, 24.5, y1)
    trapezoid(ax, 25, y1 - 5.5, 11, 11, 'VideoMAE', size=5.8)
    snow(ax, 34.6, y1 + 4.2, 1.0)
    arrow(ax, 36.5, y1, 40.5, y1)
    tensor(ax, 41, y1 - 4, 14, 8, 'N × 64K', fc=HEAD_F, ec=HEAD, c=HEAD, size=6.4)
    T(ax, 48, y1 - 6.4, 'true head output', size=5.6, c=HEAD)
    arrow(ax, 55.5, y1, 59.5, y1)
    block(ax, 60, y1 - 4.5, 13, 9, 'readout', 'per emotion', fc=RATE_F, ec=RATE, size=6.6, subsize=5.4)
    fire(ax, 72, y1 + 4.0, 0.65)
    arrow(ax, 73.5, y1, 77.5, y1)
    tensor(ax, 78, y1 - 4, 11, 8, 'N × 1', fc=RATE_F, ec=RATE, c=RATE, size=6.4)
    T(ax, 83.5, y1 - 6.4, 'VCE rating', size=5.6, c=RATE)
    # lane 2: brain ridge
    y2 = 52
    T(ax, 7, y2 + 9.0, 'HK training folds, one participant', size=6.6, c=BRAIN, w='bold', ha='left')
    img(ax, 'mni_axial.png', 7, y2 - 6, 12, 12)
    arrow(ax, 19.5, y2, 23.5, y2, c=BRAIN)
    tensor(ax, 24, y2 - 4, 15, 8, 'N × voxels', fc=BRAIN_F, ec=BRAIN, c=BRAIN, size=6.2)
    arrow(ax, 39.5, y2, 43.5, y2)
    block(ax, 44, y2 - 4.5, 13, 9, 'ridge', 'per person', fc=BRAIN_F, ec=BRAIN, size=6.6, subsize=5.4)
    fire(ax, 56, y2 + 4.0, 0.65)
    arrow(ax, 57.5, y2, 61.5, y2)
    tensor(ax, 62, y2 - 4, 14, 8, 'N × 64K', fc=HEAD_F, ec=HEAD, c=HEAD, size=6.4)
    T(ax, 69, y2 - 6.4, 'target: true head output', size=5.6, c=HEAD)
    T(ax, 7, y2 - 13.0, 'Ratings are never used to fit the ridge; the readout never sees fMRI.', size=5.6, c=GREY, ha='left')

    # ---------------- b: brain-only test ----------------
    bx = 98
    panel(ax, bx - 3, H - 1, 'b')
    T(ax, bx + 3, H - 3.6, 'Test on a held-out video: fMRI only', size=8, w='bold', ha='left')
    yb = 70
    img(ax, 'mni_axial.png', bx + 2, yb - 6, 12, 12)
    arrow(ax, bx + 14.5, yb, bx + 18, yb, c=BRAIN)
    block(ax, bx + 18.5, yb - 4.5, 11, 9, 'ridge', fc=BRAIN_F, ec=BRAIN, size=6.6)
    snow(ax, bx + 28.3, yb + 4.0, 1.0)
    arrow(ax, bx + 30, yb, bx + 33.5, yb)
    tensor(ax, bx + 34, yb - 4, 14, 8, 'N × 64K', fc='white', ec=HEAD, c=HEAD, ls=(0, (2.2, 1.2)), size=6.4)
    T(ax, bx + 41, yb - 6.4, 'reconstructed', size=5.6, c=HEAD)
    arrow(ax, bx + 48.5, yb, bx + 52, yb)
    block(ax, bx + 52.5, yb - 4.5, 12.5, 9, 'readout', fc=RATE_F, ec=RATE, size=6.6)
    snow(ax, bx + 63.8, yb + 4.0, 1.0)
    arrow(ax, bx + 65.5, yb, bx + 69, yb)
    T(ax, bx + 74.5, yb, '27\nratings', size=6.0, c=RATE, linespacing=1.1)
    # example: predicted vs measured profile for video 1374
    ex = bx + 2
    ey = 34
    img(ax, 'cowen_1374_f3.png', ex, ey + 2, 13, 13)
    T(ax, ex + 6.5, ey - 0.4, 'video 1374', size=5.6, c=GREY)
    rng = np.random.default_rng(9)
    pred = np.clip(np.array(P1374) * 0.7 + rng.normal(0.05, 0.04, 27), 0.01, None)
    for k, (lab, vals, col) in enumerate((('measured (Cowen raters)', P1374, RATE), ('predicted from fMRI', pred, '#9C8CCB'))):
        yy = ey + 9 - k * 10.5
        T(ax, ex + 16.5, yy + 8.2, lab, size=5.8, c=RATE if k == 0 else '#7A6AB0', ha='left')
        bars(ax, ex + 16.5, yy, vals, w=1.25, gap=0.5, hmax=11, colors=[col] * 27)
    T(ax, ex + 16.5 + FEAR * 1.75 + 0.6, ey - 4.2, 'fear', size=5.6, c=RATE)
    T(ax, W - 3, ey - 6.8, 'predicted values illustrative', size=5.2, c=GREY, ha='right', st='italic')

    # ---------------- c: what is reported ----------------
    panel(ax, 1, 31, 'c')
    T(ax, 7, 28.4, 'Reported for each emotion and participant', size=8, w='bold', ha='left')
    items = [('i', 'true head output → readout', 'does the VCE readout transfer to Cowen?'),
             ('ii', 'fMRI → reconstructed vs true output', 'reconstruction accuracy'),
             ('iii', 'fMRI → reconstructed → readout', 'main brain-only prediction'),
             ('iv', 'fMRI → 27 ratings (direct ridge)', 'reference, not an upper bound'),
             ('v', 'reconstruction → readout refit on Cowen', 'matched-target control')]
    for i, (k, a, b) in enumerate(items):
        col, row = i % 2 if i < 4 else 0, i // 2
        x = 7 + (i % 2) * 45 if i < 4 else 7
        y = 22 - (i // 2) * 7.5
        badge(ax, x + 1.8, y, k, c=INK if k == 'iii' else GREY, r=2.1, size=5.6)
        T(ax, x + 5, y + 1.1, a, size=6.0, ha='left')
        T(ax, x + 5, y - 1.8, b, size=5.4, c=GREY, ha='left')
    T(ax, 52, 7.0, 'HK: six run-grouped outer folds.  MC: refit on 2,108 videos, tested once on 72 videos × 5 repeats.',
      size=5.4, c=GREY, ha='left', va='top')
    save(fig, 'emobrain_brain_decoding')
    return fig


if __name__ == '__main__':
    fig5()
