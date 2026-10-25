"""Where does a render's fine-scale texture sit: inside the sheets or at their edges?

Using the sheet tracker (readability.sheets), the voxels of the tracked sheet on layers surface-13 .. surface+13 are
split into an edge shell (within 1.5 layers of the inner or outer edge) and the interior (more than 2 layers inside both
edges). For each class: F = sum d^2 / sum (v - class mean)^2, d = in-plane G(sigma 1) - G(sigma 3). Also, on open outer
faces (no papyrus within 6 layers beyond the outer edge), the mean normalised depth profile across the edge, with its
10-90% width and the fringe amplitude A = overshoot inside + undershoot outside.
In our data the nine 113 keV / 9.362 um scrolls have F interior 1.35 times the 116 keV / 8.64 um ones, with equal edge
fringes and widths (REPORT.md, round 19).

Usage:  python -m readability.texture RENDER.zarr [RENDER.zarr ...] [--surface 33] [--rows 500:1320] [--voxel 8.64]
"""
import argparse

import numpy as np
import zarr
from scipy import ndimage

from readability.sheets import track

TS = np.arange(-6, 6.001, 0.25)


def _interp(V, z):
    z = np.clip(z, 0, V.shape[0] - 1.001)
    k = np.floor(z).astype(int)
    f = z - k
    n = np.arange(V.shape[1])
    return V[k, n] * (1 - f) + V[k + 1, n] * f


def texture(path, surface=33, rows=slice(None), chunk=2000):
    A = zarr.open_group(path, mode='r')['0']
    k0, k1 = surface - 19, surface + 21
    g = surface - k0
    acc = {c: [0.0, 0.0] for c in ('edge', 'interior')}
    prof = []
    for x0 in range(0, A.shape[2], chunk):
        R = np.asarray(A[k0:k1, rows, x0:x0 + chunk]).astype(np.float32)
        if R.shape[2] < 200 or (R[g] > 0).mean() < 0.5:
            continue
        t = track(R, g)
        zi, ze, val, T, Vs = t['rise'], t['fall'], t['valid'], t['T'], t['Vs']
        for kk in range(g - 13, g + 14):
            x = R[kk]
            d = ndimage.gaussian_filter(x, 1) - ndimage.gaussian_filter(x, 3)
            dist = np.minimum(np.abs(kk - zi), np.abs(kk - ze))
            for c, m in (('edge', val & (dist <= 1.5)), ('interior', val & (kk > zi + 2) & (kk < ze - 2))):
                if m.sum() > 100:
                    v = x[m]
                    acc[c][0] += float((d[m] ** 2).sum())
                    acc[c][1] += float(((v - v.mean()) ** 2).sum())
        e0 = np.ceil(ze).astype(int)
        beyond = np.stack([np.take_along_axis(Vs, np.clip(e0 + j, 0, Vs.shape[0] - 1)[None], 0)[0] for j in range(1, 7)])
        opn = val & (e0 + 6 < Vs.shape[0]) & (beyond < T[None]).all(0) & (ze - zi >= 5)
        if opn.sum() < 50:
            continue
        idx = np.nonzero(opn)
        sub = np.random.default_rng(x0).permutation(len(idx[0]))[:20000]
        yy, xx = idx[0][sub], idx[1][sub]
        P = Vs[:, yy, xx]
        zf, zr = ze[yy, xx], zi[yy, xx]
        ks = np.arange(P.shape[0])[:, None]
        inner = (ks >= np.ceil(zr + 2)[None]) & (ks <= np.floor(zf - 2)[None])
        plateau = np.nanmedian(np.where(inner, P, np.nan), 0)
        void = np.median(np.stack([_interp(P, zf + t_) for t_ in (4, 5, 6)]), 0)
        ok = np.isfinite(plateau) & (plateau - void > 10)
        if ok.sum() >= 50:
            prof.append(np.stack([(_interp(P, zf + t_) - void) / (plateau - void) for t_ in TS])[:, ok])
    out = {f'F_{c}': acc[c][0] / max(acc[c][1], 1e-9) for c in acc}
    if prof:
        pm = np.concatenate(prof, 1).mean(1)
        t90 = TS[np.nonzero(pm >= 0.9)[0].max()] if (pm >= 0.9).any() else np.nan
        t10 = TS[np.nonzero(pm >= 0.1)[0].max()] if (pm >= 0.1).any() else np.nan
        over = max(0.0, float(pm[(TS >= -3) & (TS <= 0)].max() - 1))
        under = max(0.0, float(-pm[(TS >= 0) & (TS <= 4)].min()))
        out.update(edge_width_layers=float(t10 - t90), fringe_amplitude=over + under)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('renders', nargs='+')
    ap.add_argument('--surface', type=int, default=33)
    ap.add_argument('--rows', default=':')
    ap.add_argument('--voxel', type=float, default=None, help='voxel size in um, to print the edge width in um')
    a = ap.parse_args()
    r0, r1 = (a.rows.split(':') + [''])[:2]
    rows = slice(int(r0) if r0 else None, int(r1) if r1 else None)
    for p in a.renders:
        r = texture(p, a.surface, rows)
        w = r.get('edge_width_layers', float('nan'))
        wu = f' = {w * a.voxel:.0f} um' if a.voxel else ''
        print(f'{p}\tF interior {r["F_interior"]:.3f}\tF edge {r["F_edge"]:.3f}\tedge width {w:.2f} layers{wu}'
              f'\tfringe {r.get("fringe_amplitude", float("nan")):.3f}')


if __name__ == '__main__':
    main()
