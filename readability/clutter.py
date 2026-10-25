"""Clutter index of a surface-volume render: the share of near-surface papyrus variance in a fine-scale band.

For each of the seven layers on the ink side of the mesh (surface-6 .. surface, or surface .. surface+6 with
--side above), the in-plane difference of Gaussians d = G(sigma 1 px) - G(sigma 3 px) is taken; the index is the mean
over layers of var(d) / var(v) on papyrus pixels (non-zero at the surface layer). The band peaks at a period of 8.5 px,
about 75 um at 9 um voxels. Lower is quieter. It needs no labels.

Validation (REPORT.md): Spearman -0.80 to -0.97 with injected-ink readability over 12 eligible scrolls (two ink
sources x two models), -0.71 and -0.95 over 11 survey renders with a matched pipeline, -0.67 to -0.93 within the nine
113 keV scrolls. Plain gradient energy does about as well; total variance does not predict (round 27). It is a
property of the render (window, depth, voxel size), not of the scroll as a whole.

Usage:
    python -m readability.clutter RENDER.zarr [RENDER.zarr ...] [--surface 33] [--side below|above]
                                  [--rows 500:1320] [--cols 0:4400]
"""
import argparse

import numpy as np
import zarr
from scipy import ndimage


def clutter_index(V, surface=33, mask=None, side='below'):
    """V: (L, H, W) render window. Returns the clutter index (float)."""
    if mask is None:
        mask = V[surface] > 0
    if mask.sum() < 1000:
        return float('nan')
    vals = []
    for k in (range(surface - 6, surface + 1) if side == 'below' else range(surface, surface + 7)):
        x = V[k].astype(np.float32)
        d = ndimage.gaussian_filter(x, 1) - ndimage.gaussian_filter(x, 3)
        vals.append(d[mask].var() / max(x[mask].var(), 1e-6))
    return float(np.mean(vals))


def _slice(s):
    a, b = (s.split(':') + [''])[:2]
    return slice(int(a) if a else None, int(b) if b else None)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('renders', nargs='+')
    ap.add_argument('--surface', type=int, default=33, help='index of the mesh layer (33 in a 66-layer render)')
    ap.add_argument('--side', choices=('below', 'above'), default='below',
                    help='which side of the mesh carries the ink (below = lower layer indices, as in our renders)')
    ap.add_argument('--rows', default=':')
    ap.add_argument('--cols', default=':')
    a = ap.parse_args()
    for p in a.renders:
        A = zarr.open_group(p, mode='r')['0']
        if a.side == 'below':
            V, s0 = np.asarray(A[a.surface - 6:a.surface + 1, _slice(a.rows), _slice(a.cols)]), 6
        else:
            V, s0 = np.asarray(A[a.surface:a.surface + 7, _slice(a.rows), _slice(a.cols)]), 0
        print(f'{p}\tclutter index {clutter_index(V, surface=s0, side=a.side):.4f}')


if __name__ == '__main__':
    main()
