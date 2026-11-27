import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import *
from fig1 import P1374, FEAR, EMO27

BRAIN_CMAP = ['#FBEDEC', '#F2C9C5', '#E59A93', '#D06A62', '#B83B3B']


def strip(ax, x, y, w, h, vals, ec=BRAIN, ls='-', z=5):
    """One voxel pattern drawn as a row of shaded cells."""
    n = len(vals)
    cw = w / n
    for i, v in enumerate(vals):
        k = int(np.clip(v, 0, 0.999) * len(BRAIN_CMAP))
        ax.add_patch(Rectangle((x + i * cw, y), cw, h, fc=BRAIN_CMAP[k], ec='none', zorder=z))
    ax.add_patch(Rectangle((x, y), w, h, fc='none', ec=ec, lw=0.6, ls=ls, zorder=z + 1))


def fig5():
    W, H = 180, 128
    fig, ax = canvas(W, H)
    rng = np.random.default_rng(5)
    NV = 18
    measured = rng.uniform(0, 1, NV)

    # ---------------- a: fit the encoding model ----------------
    panel(ax, 1, H - 1, 'a')
    T(ax, 7, H - 3.6, 'Fit an encoding model for each participant', size=8, w='bold', ha='left')
    y1 = H - 17
    tensor(ax, 7, y1 - 5, 13, 10, 'training\nvideos', size=6.2)
    arrow(ax, 20.5, y1, 24.5, y1)
    trapezoid(ax, 25, y1 - 5.5, 11, 11, 'VideoMAE', size=5.8)
    snow(ax, 34.6, y1 + 4.2, 1.0)
    arrow(ax, 36.5, y1, 40.5, y1)
    tensor(ax, 41, y1 - 4, 14, 8, 'N × 64K', fc=HEAD_F, ec=HEAD, c=HEAD, size=6.4)
    T(ax, 48, y1 - 6.4, 'head output', size=5.6, c=HEAD)
    arrow(ax, 55.5, y1, 59.5, y1)
    block(ax, 59.5, y1 - 4.5, 17, 9, 'encoding', 'ridge, per person', fc='white', ec=INK, size=6.4, subsize=5.0)
    fire(ax, 75.5, y1 + 4.0, 0.65)
    arrow(ax, 77, y1, 80, y1)
    tensor(ax, 80.5, y1 - 4, 14, 8, 'N × voxels', fc='white', ec=BRAIN, c=BRAIN, ls=(0, (2.2, 1.2)), size=6.0)
    T(ax, 87.5, y1 - 6.4, 'predicted', size=5.6, c=BRAIN)
    img(ax, 'mni_axial.png', 62.5, y1 - 21, 11, 11)
    arrow(ax, 68, y1 - 9.6, 68, y1 - 5.0, c=BRAIN, lw=0.9)
    T(ax, 75, y1 - 15.5, 'target: measured\nvoxels of the\nsame videos', size=5.6, c=BRAIN, ha='left', linespacing=1.15)
    T(ax, 7, y1 - 14.5, 'Same fit as the head model\nof analysis 4. Ratings are\nnot used in this step.',
      size=5.6, c=GREY, ha='left', va='top', linespacing=1.2)

    # ---------------- b: identification ----------------
    bx = 100
    panel(ax, bx - 3, H - 1, 'b')
    T(ax, bx + 3, H - 3.6, 'Which video was seen?', size=8, w='bold', ha='left')
    T(ax, bx + 3, H - 7.6, 'compare the measured pattern with the predicted pattern of every test video',
      size=5.4, c=GREY, ha='left')
    yb = H - 17
    stack(ax, ['cowen_1374_f3.png', 'cowen_1374_f4.png'], bx + 2, yb - 5, 9, dx=1.2, dy=1.2)
    T(ax, bx + 7, yb - 7.6, 'test video', size=5.4, c=GREY)
    strip(ax, bx + 14, yb - 1.4, 22, 3.2, measured)
    T(ax, bx + 25, yb + 3.6, 'measured fMRI', size=5.6, c=BRAIN)
    tests = [('cowen_1374_f3.png', 0.41, True), ('cowen_0366_f2.png', 0.12, False),
             ('cowen_0055_f2.png', 0.05, False), (None, 0.18, False)]
    for k, (nm, r, ok) in enumerate(tests):
        yy = yb - 4 - k * 6.2
        pred = np.clip(measured * (0.8 if ok else 0.15) + rng.uniform(0, 1, NV) * (0.25 if ok else 0.85), 0, 1)
        if nm:
            img(ax, nm, bx + 39.5, yy - 2.3, 5, 5, lw=0.4)
        else:
            ax.add_patch(Rectangle((bx + 39.5, yy - 2.3), 5, 5, fc='#E4E4E4', ec='#9A9A9A', lw=0.4, zorder=5))
        strip(ax, bx + 46, yy - 1.4, 20, 3.2, pred, ls=(0, (2, 1)))
        T(ax, bx + 67.5, yy + 0.2, f'r = {r:.2f}', size=5.6, c=INK if ok else GREY, ha='left', w='bold' if ok else 'normal')
        if ok:
            rbox(ax, bx + 38.8, yy - 3.0, 38.4, 6.3, fc='none', ec=INK, lw=0.7, r=0.8, z=9)
    T(ax, bx + 57, yb + 3.6, 'predicted, one per test video', size=5.6, c=BRAIN)
    arrow(ax, bx + 36.5, yb + 0.2, bx + 38.6, yb - 3.0, lw=0.6)
    T(ax, bx + 56, yb - 28.4, '...', size=7, c=GREY)
    T(ax, bx + 3, yb - 33.0, 'correct if its own prediction has the highest r.\nchance = 1 / number of test videos (MC: 1 / 72)',
      size=5.6, ha='left', va='top', linespacing=1.2)
    line(ax, [3, W - 3], [H - 55, H - 55], c='#DDDDDD', lw=0.6)

    # ---------------- c: emotion estimate ----------------
    yc = H - 57
    panel(ax, 1, yc, 'c')
    T(ax, 7, yc - 2.6, 'Estimate the ratings from the best-matching candidate videos', size=8, w='bold', ha='left')
    T(ax, 7, yc - 6.6, 'candidates: Cowen videos outside the test set, its source groups and the MC 72; they need head output '
                       'and ratings, not fMRI', size=5.4, c=GREY, ha='left')
    y3 = yc - 21
    strip(ax, 7, y3 - 1.6, 22, 3.2, measured)
    T(ax, 18, y3 + 5.0, 'measured fMRI\nof the test video', size=5.6, c=BRAIN, linespacing=1.15)
    arrow(ax, 29.5, y3, 34, y3, lw=0.6)
    cands = [0.36, 0.33, 0.31, 0.12]
    base = np.array(P1374)
    profs = []
    for k, r in enumerate(cands):
        yy = y3 + 6 - k * 5.4 if k < 3 else y3 - 15
        ax.add_patch(Rectangle((35, yy - 2), 4.2, 4.2, fc='#E4E4E4', ec='#9A9A9A', lw=0.4, zorder=5))
        lab = f'#{k + 1}' if k < 3 else '#200'
        T(ax, 37.1, yy + 0.1, lab, size=4.6, c=GREY)
        T(ax, 40.4, yy + 0.1, f'r = {r:.2f}', size=5.2, c=INK if k < 3 else GREY, ha='left')
        p = np.clip(base * rng.uniform(0.5, 1.2, 27) + rng.uniform(0, 0.12, 27) * (rng.random(27) < 0.35), 0, 1) \
            if k < 3 else np.clip(rng.uniform(0, 0.4, 27) * (rng.random(27) < 0.3), 0, 1)
        profs.append(p)
        bars(ax, 51, yy - 2, p, w=0.55, gap=0.15, hmax=6.0, colors=['#CFC6E6' if k < 3 else '#E6E6E6'] * 27,
             hi=FEAR if k < 3 else None)
    T(ax, 37.1, y3 - 9.6, '...', size=6, c=GREY)
    rbox(ax, 33.8, y3 - 11.2, 39.5, 20.6, fc='none', ec=RATE, lw=0.7, r=0.8, ls=(0, (2, 1.2)), z=9)
    T(ax, 53.5, y3 + 11.6, 'top N candidates by r (N: decision record 7)', size=5.4, c=RATE)
    T(ax, 51, y3 - 18.0, 'bars: Cowen ratings of each candidate', size=5.0, c=GREY, ha='left')
    arrow(ax, 74, y3, 80, y3)
    T(ax, 77, y3 + 2.4, 'mean', size=5.6, c=RATE)
    est = np.mean(profs[:3], axis=0)
    ex = 82
    for k, (lab, vals, col, cl) in enumerate((('estimate (mean of top N)', est, '#9C8CCB', '#7A6AB0'),
                                              ('measured (Cowen raters)', P1374, '#BDB3D9', RATE))):
        yy = y3 + 2 - k * 12
        T(ax, ex, yy + 8.0, lab, size=5.8, c=cl, ha='left')
        bars(ax, ex, yy, vals, w=1.0, gap=0.35, hmax=6.5, colors=[col] * 27, hi=FEAR)
    T(ax, ex + FEAR * 1.35 + 0.5, y3 - 12.0, 'fear', size=5.4, c=RATE)
    T(ax, ex + 39, y3 + 4.5, 'the test video\'s own\nrating is not used', size=5.4, c=GREY, ha='left', linespacing=1.15)
    T(ax, ex + 39, y3 - 4.0, 'across test videos:\nPearson r between\nestimate and rating,\nper emotion',
      size=5.6, ha='left', linespacing=1.15)
    line(ax, [3, W - 3], [y3 - 21.0, y3 - 21.0], c='#DDDDDD', lw=0.6)

    # ---------------- d: what is reported ----------------
    yd = y3 - 23.0
    panel(ax, 1, yd, 'd')
    T(ax, 7, yd - 2.6, 'Reported for each participant and voxel range', size=8, w='bold', ha='left')
    items = [('i', 'identification accuracy and rank', 'against chance'),
             ('ii', 'estimate r for each of 27 emotions', 'main brain-only result'),
             ('iii', 'the same with random head lists', 'same layers, same number of heads'),
             ('iv', 'fMRI → 27 ratings (direct ridge)', 'reference, not an upper bound')]
    for i, (k, a, b) in enumerate(items):
        x = 7 + (i % 2) * 62
        y = yd - 9.5 - (i // 2) * 7.5
        badge(ax, x + 1.8, y, k, c=INK if k == 'ii' else GREY, r=2.1, size=5.6)
        T(ax, x + 5, y + 1.1, a, size=6.0, ha='left')
        T(ax, x + 5, y - 1.8, b, size=5.4, c=GREY, ha='left')
    T(ax, 133, yd - 7.0, 'voxel range: decision record 7\n(visual and association region\ngroups, whole brain as reference,\nrecommended)',
      size=5.2, c=GREY, ha='left', va='top', linespacing=1.2)
    T(ax, 7, 2.4, 'HK: six run-grouped outer folds.  MC: refit on the development videos, tested on 72 videos '
                  '(5 repeats averaged).  Values illustrative.', size=5.2, c=GREY, ha='left')
    save(fig, 'emobrain_brain_decoding')
    return fig


if __name__ == '__main__':
    fig5()
