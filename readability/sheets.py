"""Sheet check: does a surface-volume render sit on distinct papyrus sheets?

A run-based sheet tracker follows, per pixel, the papyrus run nearest the mesh layer along the depth profile
(7 x 7 in-plane mean; papyrus = above the midpoint of the pixel's own 20th and 80th percentiles, which must differ by at
least 25 grey levels; the run centre is regularised by a 31 px median filter; sub-voxel inner and outer edges). A pixel
is valid when a run 3-30 layers thick with gaps on both sides is found. Reported per render:
  valid   share of papyrus pixels with a valid tracked sheet;
  near    share of valid pixels whose sheet centre lies within +-2 layers of the mesh layer;
  contrast  median depth contrast (p80 - p20, grey levels) and the share of pixels reaching 25.
On our renders PHerc. 800 gives valid 63%, PHerc. 0268 14% (depth contrast 33 against 16): searches and readability
measurements on renders like the latter should not be trusted (REPORT.md, round 22). The official PHerc. 0841 segments,
rendered with readability.tifxyz, give 82-83% (depth contrast about 60). Read valid together with the depth contrast:
it depends on the scan as well as on the segment.

Usage:  python -m readability.sheets RENDER.zarr [RENDER.zarr ...] [--surface 33] [--map] [--min-papyrus 0.5]
For an organisers' tifxyz segment, first render a 41-layer band with `python -m readability.tifxyz` (the standard
28-layer ink render is too thin to show the neighbouring sheets).
"""
import argparse

import numpy as np
import zarr
from scipy import ndimage


def track(R, guess):
    """R: (L, H, W) sub-stack; guess: layer index of the mesh in R. Returns a dict: rise and fall (sub-voxel inner and
    outer edges), valid, mask (papyrus at the mesh layer), contrast (p80 - p20), threshold T and the smoothed stack Vs."""
    V = ndimage.uniform_filter(R.astype(np.float32), (1, 7, 7))
    L = V.shape[0]
    mask = R[guess] > 0
    p20, p80 = np.percentile(V, 20, axis=0), np.percentile(V, 80, axis=0)
    T = (p20 + p80) / 2
    ok = mask & (p80 - p20 >= 25)
    B = V > T[None]
    rs = np.zeros(V.shape, np.int16)
    re = np.zeros(V.shape, np.int16)
    for k in range(1, L):
        rs[k] = np.where(B[k] & B[k - 1], rs[k - 1], k)
    re[L - 1] = L - 1
    for k in range(L - 2, -1, -1):
        re[k] = np.where(B[k] & B[k + 1], re[k + 1], k)
    ks = np.arange(L, dtype=np.float32)[:, None, None]

    def pick(g):
        kstar = np.argmin(np.where(B, np.abs(ks - g[None]), 1e9), 0)[None]
        return np.take_along_axis(rs, kstar, 0)[0].astype(np.int32), np.take_along_axis(re, kstar, 0)[0].astype(np.int32)

    s, e = pick(np.full(V.shape[1:], guess, np.float32))
    s, e = pick(ndimage.median_filter(np.where(ok, (s + e) / 2, guess), 31).astype(np.float32))
    sm1, ep1 = np.clip(s - 1, 0, L - 1), np.clip(e + 1, 0, L - 1)
    tk = lambda i: np.take_along_axis(V, i[None], 0)[0]
    vs, vsm, ve, vep = tk(s), tk(sm1), tk(e), tk(ep1)
    zi = sm1 + np.clip((T - vsm) / np.where(np.abs(vs - vsm) > 1e-3, vs - vsm, 1e-3), 0, 1)
    ze = e + np.clip((ve - T) / np.where(np.abs(ve - vep) > 1e-3, ve - vep, 1e-3), 0, 1)
    th = ze - zi
    valid = ok & (s > 0) & (e < L - 1) & (th >= 3) & (th <= 30)
    return dict(rise=zi, fall=ze, valid=valid, mask=mask, contrast=p80 - p20, T=T, Vs=V)


def check(path, surface=None, chunk=2000, map_out=None, min_papyrus=0.5):
    """Sheet statistics of a render (zarr group with array 0). surface: mesh layer (default: middle layer).
    map_out: optional PNG, a quarter-size map (green: valid sheet centred within +-2 layers of the mesh; yellow: valid
    sheet centred further away, normal when the mesh follows a sheet face; red: papyrus without a valid sheet; grey: not
    checked; black: no data)."""
    A = zarr.open_group(path, mode='r')['0']
    L = A.shape[0]
    if surface is None:
        surface = L // 2
    k0, k1 = max(0, surface - 19), min(L, surface + 21)
    if k1 - k0 < 30:
        print(f'warning: {path} has {k1 - k0} layers around the mesh; the check needs about 40 '
              '(render a thicker band, e.g. python -m readability.tifxyz)')
    npap = nval = nnear = 0
    contrast = []
    qa = np.zeros(A.shape[1:], np.uint8) if map_out else None
    for x0 in range(0, A.shape[2], chunk):
        R = np.asarray(A[k0:k1, :, x0:x0 + chunk])
        if qa is not None:
            qa[:, x0:x0 + R.shape[2]][R[surface - k0] > 0] = 4
        if R.shape[2] < 200 or (R[surface - k0] > 0).mean() < min_papyrus:
            continue
        t = track(R, surface - k0)
        val, mask, centre = t['valid'], t['mask'], (t['rise'] + t['fall']) / 2
        near = val & mask & (np.abs(centre - (surface - k0)) <= 2)
        npap += int(mask.sum())
        nval += int((val & mask).sum())
        nnear += int(near.sum())
        contrast.append(t['contrast'][mask][::97])
        if qa is not None:
            q = qa[:, x0:x0 + R.shape[2]]
            q[mask] = 3
            q[val & mask] = 2
            q[near] = 1
    c = np.concatenate(contrast) if contrast else np.array([np.nan])
    if qa is not None:
        from PIL import Image
        pal = np.array([[0, 0, 0], [0, 170, 0], [230, 190, 0], [200, 30, 30], [110, 110, 110]], np.uint8)
        Image.fromarray(pal[qa[::4, ::4]]).save(map_out)
    return dict(valid=nval / max(npap, 1), near=nnear / max(nval, 1), contrast_median=float(np.median(c)),
                contrast_share_25=float(np.mean(c >= 25)), papyrus_checked=npap)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('renders', nargs='+')
    ap.add_argument('--surface', type=int, default=None, help='mesh layer (default: the middle layer; 33 in our renders)')
    ap.add_argument('--map', action='store_true', help='also write RENDER.sheets.png, a quarter-size map')
    ap.add_argument('--min-papyrus', type=float, default=0.5, help='skip 2000 px strips with less papyrus than this')
    a = ap.parse_args()
    for p in a.renders:
        r = check(p, a.surface, map_out=p.rstrip('/') + '.sheets.png' if a.map else None, min_papyrus=a.min_papyrus)
        print(f'{p}	valid {r["valid"]:.1%}	near {r["near"]:.1%}	depth contrast median {r["contrast_median"]:.1f} '
              f'(share >= 25: {r["contrast_share_25"]:.0%})	papyrus checked {r["papyrus_checked"]:,} px')


if __name__ == '__main__':
    main()
