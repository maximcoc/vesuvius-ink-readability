"""Render a band around a tifxyz segment straight from the scan volume, so the sheet check and the clutter index can run
on the organisers' own segments.

A tifxyz segment (x.tif, y.tif, z.tif: float32 scan coordinates on a grid at `scale` of the canvas, -1 = no data;
meta.json) is upsampled bilinearly to the full canvas; normals come from the grid derivatives. The scan volume (OME-Zarr
level 0, axes z, y, x) is sampled trilinearly at P + k n for k = -half .. half voxels. Output: (2 half + 1, H, W)
uint8, mesh at layer `half`, 0 where the segment has no data. The sign of the normal follows the grid orientation
(cross product of the column and row derivatives); the sheet check does not depend on it.

The standard ink render of a segment has about 28 layers, too few to see the neighbouring sheets; the sheet check
needs about 40 (half = 20).

A remote volume (https URL of an OME-Zarr v2 array, as in the Vesuvius Challenge open-data bucket) is fetched first,
only the chunks the band touches, into a local sparse copy.

Usage:
    python -m readability.tifxyz SEGMENT.tifxyz VOLUME OUT.zarr [--half 20] [--cache DIR]
VOLUME is a local zarr group (array 0) or an https URL to it.
"""
import argparse
import json
import os
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import zarr
from PIL import Image
from scipy import ndimage


def read(seg):
    """Returns X, Y, Z (grid, float32), valid (grid, bool) and the grid scale."""
    X, Y, Z = (np.asarray(Image.open(os.path.join(seg, f'{c}.tif')), np.float32) for c in 'xyz')
    meta = json.load(open(os.path.join(seg, 'meta.json')))
    valid = (X != -1) & (Y != -1) & (Z != -1) & np.isfinite(X) & np.isfinite(Y) & np.isfinite(Z)
    return X, Y, Z, valid, float(meta['scale'][0])


def _normals(X, Y, Z, valid):
    P = np.stack([np.where(valid, c, np.nan) for c in (X, Y, Z)])
    dr, dc = np.gradient(P, axis=1), np.gradient(P, axis=2)
    n = np.cross(dc, dr, axis=0)
    n /= np.linalg.norm(n, axis=0, keepdims=True)
    ok = valid & np.all(np.isfinite(n), axis=0)
    return np.where(ok, n, 0).astype(np.float32), ok


class Surface:
    """Full-canvas positions and normals of a tifxyz segment, computed tile by tile."""

    def __init__(self, seg):
        X, Y, Z, valid, self.scale = read(seg)
        self.grid = np.stack([X, Y, Z])
        self.n, self.ok = _normals(X, Y, Z, valid)
        self.H, self.W = int(round(X.shape[0] / self.scale)), int(round(X.shape[1] / self.scale))

    def tile(self, r0, r1, c0, c1):
        """positions P (3, h, w) as x, y, z; normals (3, h, w); valid (h, w)"""
        rr, cc = np.meshgrid(np.arange(r0, r1) * self.scale, np.arange(c0, c1) * self.scale, indexing='ij')
        co = [rr, cc]
        ok = ndimage.map_coordinates(self.ok.astype(np.float32), co, order=1, mode='constant') > 0.999
        P = np.stack([ndimage.map_coordinates(g, co, order=1, mode='nearest') for g in self.grid])
        n = np.stack([ndimage.map_coordinates(g, co, order=1, mode='nearest') for g in self.n])
        nn = np.linalg.norm(n, axis=0)
        ok &= nn > 0.5
        n /= np.maximum(nn, 1e-6)
        return P, n, ok


def chunks_needed(surf, half, chunk=128, step=4):
    """set of level-0 chunk indices (iz, iy, ix) touched by the band"""
    need = set()
    for r0 in range(0, surf.H, 512):
        for c0 in range(0, surf.W, 512):
            P, n, ok = surf.tile(r0, min(r0 + 512, surf.H), c0, min(c0 + 512, surf.W))
            P, n = P[:, ::step, ::step][:, ok[::step, ::step]], n[:, ::step, ::step][:, ok[::step, ::step]]
            if P.shape[1] == 0:
                continue
            for k in list(range(-half, half + 1, step)) + [half]:
                f = np.floor((P + k * n)[::-1]).astype(np.int64)
                for d in np.ndindex(2, 2, 2):
                    idx = (f + np.array(d)[:, None]) // chunk
                    need.update(map(tuple, np.unique(idx.T, axis=0).tolist()))
    return need


def fetch(url, need, cache, workers=16):
    """download the zarr metadata and the needed chunks of level 0 into cache (a local sparse zarr v2 group)"""
    url = url.rstrip('/')
    keys = ['.zgroup', '.zattrs', '0/.zarray'] + [f'0/{iz}/{iy}/{ix}' for iz, iy, ix in sorted(need) if min(iz, iy, ix) >= 0]

    def get(key):
        dst = os.path.join(cache, key)
        if os.path.exists(dst) and os.path.getsize(dst) > 0:
            return os.path.getsize(dst)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        for _ in range(3):
            try:
                data = urllib.request.urlopen(f'{url}/{key}', timeout=120).read()
                open(dst, 'wb').write(data)
                return len(data)
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return 0
            except Exception:
                pass
        raise RuntimeError(f'failed {key}')

    with ThreadPoolExecutor(workers) as ex:
        return len(keys), sum(ex.map(get, keys))


def render(surf, A, half=20, tile=256):
    """A: zarr array (z, y, x). Returns (2 half + 1, H, W) uint8 with the mesh at layer half."""
    L = 2 * half + 1
    out = np.zeros((L, surf.H, surf.W), np.uint8)
    for r0 in range(0, surf.H, tile):
        for c0 in range(0, surf.W, tile):
            r1, c1 = min(r0 + tile, surf.H), min(c0 + tile, surf.W)
            P, n, ok = surf.tile(r0, r1, c0, c1)
            if not ok.any():
                continue
            q = P[:, ok][:, None, :] + np.arange(-half, half + 1, dtype=np.float32)[None, :, None] * n[:, ok][:, None, :]
            zyx = q[::-1]
            lo = np.maximum(np.floor(zyx.reshape(3, -1).min(1)).astype(int), 0)
            hi = np.minimum(np.floor(zyx.reshape(3, -1).max(1)).astype(int) + 2, A.shape)
            if np.any(hi <= lo):
                continue
            sub = np.asarray(A[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]])
            v = ndimage.map_coordinates(sub, [zyx[i] - lo[i] for i in range(3)], order=1, mode='constant', cval=0)
            blk = np.zeros((L, r1 - r0, c1 - c0), np.uint8)
            blk[:, ok] = np.clip(np.rint(v), 0, 255).astype(np.uint8)
            out[:, r0:r1, c0:c1] = blk
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('segment')
    ap.add_argument('volume')
    ap.add_argument('out')
    ap.add_argument('--half', type=int, default=20)
    ap.add_argument('--cache', default=None, help='local sparse copy of a remote volume (default: OUT + .volume)')
    a = ap.parse_args()
    surf = Surface(a.segment)
    vol = a.volume
    if vol.startswith('http'):
        cache = a.cache or a.out.rstrip('/') + '.volume'
        need = chunks_needed(surf, a.half)
        nk, nb = fetch(vol, need, cache)
        print(f'fetched {nk} objects ({len(need)} chunks), {nb / 1e9:.2f} GB in {cache}', flush=True)
        vol = cache
    A = zarr.open_group(vol, mode='r')['0']
    R = render(surf, A, a.half)
    g = zarr.open_group(a.out, mode='w')
    g.create_array('0', shape=R.shape, chunks=(R.shape[0], 128, 128), dtype='uint8')[:] = R
    print(f'{a.out}: {R.shape} uint8, mesh at layer {a.half}, segment pixels {(R[a.half] > 0).mean():.1%}')


if __name__ == '__main__':
    main()
