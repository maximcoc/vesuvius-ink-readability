"""Build letter-source crops for the readability bench (npz with R (Ls, H, W) uint8, lab and cert (H, W) bool).

The crops contain labelled ink, so they are built locally from the original datasets and never redistributed.

1. From a surface volume with labels on the same canvas (for example Y. Nader's PHerc. 1447 surfaces, 24 layers):
       python -m readability.crops canvas SURFACE(.zarr | dir of layer tifs) LABELS.png MASK.png Y0 X0 H W OUT.npz
   R is read as stored; for those surfaces the reading side is the reversed layer order, as in our renders.

2. From an official segment whose labels live on a finer canvas (for example PHerc. 0841: 28-layer 9.366 um surface
   volume, labels of 2026-09-18 on the 2.403 um canvas):
       python -m readability.crops official SURFACE.zarr LABELS_DIR CHECKPOINT OUT.npz [--height 800 --width 4400]
   LABELS_DIR holds inklabels.zarr and supervision.zarr. The labels are box-downsampled to the surface canvas; the
   label offset (+-24 px), the reading direction and the window start (3, 5, 7) are those that maximise the model's
   pixel AUC on the native volume (this inflates absolute AUC slightly, not comparisons that use fixed masks). The
   window with the most supervised label pixels is saved, flipped if needed so that the reading side is reversed.
"""
import argparse
import glob
import os

import numpy as np
import zarr
from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def _stack(path):
    if path.endswith('.zarr'):
        return zarr.open_group(path, mode='r')['0']
    files = sorted(glob.glob(os.path.join(path, '*.tif')))
    return np.stack([np.asarray(Image.open(f)) for f in files])


def canvas_crop(surface, labels_png, mask_png, y0, x0, h, w, out):
    R = np.asarray(_stack(surface)[:, y0:y0 + h, x0:x0 + w])
    lab = np.asarray(Image.open(labels_png).convert('L'))[y0:y0 + h, x0:x0 + w] > 127
    cert = np.asarray(Image.open(mask_png).convert('L'))[y0:y0 + h, x0:x0 + w] > 0
    np.savez_compressed(out, R=R, lab=lab, cert=cert)
    print(out, R.shape, int((lab & cert).sum()), 'labelled px')


def _down(zpath, shape):
    a = np.asarray(zarr.open_group(zpath, mode='r')['0'])
    im = Image.fromarray((a > 0).astype(np.float32), mode='F').resize((shape[1], shape[0]), Image.BOX)
    return np.asarray(im) > 0.5


def _auc8(pb, lab, sup):
    hp = np.bincount(pb[lab & sup], minlength=256).astype(float)
    hn = np.bincount(pb[~lab & sup], minlength=256).astype(float)
    cn = np.cumsum(hn) - hn
    return float((hp * (cn + 0.5 * hn)).sum() / max(1e-12, hp.sum() * hn.sum()))


def _shift(a, dy, dx):
    o = np.zeros_like(a)
    ys, yd = (slice(0, a.shape[0] - dy), slice(dy, None)) if dy >= 0 else (slice(-dy, None), slice(0, a.shape[0] + dy))
    xs, xd = (slice(0, a.shape[1] - dx), slice(dx, None)) if dx >= 0 else (slice(-dx, None), slice(0, a.shape[1] + dx))
    o[yd, xd] = a[ys, xs]
    return o


def official_crop(surface, labels_dir, checkpoint, out, h=800, w=4400, m=24):
    from readability.infer import load_model, infer
    V = np.asarray(zarr.open_group(surface, mode='r')['0'])
    lab, sup = _down(f'{labels_dir}/inklabels.zarr', V.shape[1:]), _down(f'{labels_dir}/supervision.zarr', V.shape[1:])
    model = load_model(checkpoint)
    rng = np.random.default_rng(0)
    ys = rng.integers(m, V.shape[1] - m, 3_000_000)
    xs = rng.integers(m, V.shape[2] - m, 3_000_000)
    best = None
    for direction in ('reverse', 'forward'):
        for s in (3, 5, 7):
            win = V[s:s + 17] if direction == 'reverse' else V[s:s + 17][::-1]
            vals = np.floor(255 * infer(win, model)[0]).astype(np.uint8)[ys, xs]
            for dy in range(-m, m + 1, 2):
                for dx in range(-m, m + 1, 2):
                    l = lab[ys - dy, xs - dx]
                    q = sup[ys - dy, xs - dx]
                    if (l & q).sum() > 1000:
                        a = _auc8(vals, l, q)
                        if best is None or a > best[0]:
                            best = (a, direction, s, dy, dx)
    a, direction, s, dy, dx = best
    print(f'native AUC {a:.3f}: direction {direction}, start {s}, label offset ({dy:+d}, {dx:+d})')
    lab, sup = _shift(lab, dy, dx), _shift(sup, dy, dx)
    c = np.cumsum(np.cumsum(np.pad((lab & sup).astype(np.int64), ((1, 0), (1, 0))), 0), 1)
    n, y0, x0 = max((int(c[y + h, x + w] - c[y, x + w] - c[y + h, x] + c[y, x]), y, x)
                    for y in range(0, V.shape[1] - h + 1, 50) for x in range(0, V.shape[2] - w + 1, 50))
    R = V[:, y0:y0 + h, x0:x0 + w]
    if direction == 'forward':
        R = R[::-1]
    np.savez_compressed(out, R=np.ascontiguousarray(R), lab=lab[y0:y0 + h, x0:x0 + w], cert=sup[y0:y0 + h, x0:x0 + w])
    start = s if direction == 'reverse' else V.shape[0] - 17 - s
    print(f'{out}: window y {y0} x {x0}, {n} labelled px; model window start in the saved crop: {start}')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='mode', required=True)
    a1 = sub.add_parser('canvas')
    for k in ('surface', 'labels', 'mask'):
        a1.add_argument(k)
    for k in ('y0', 'x0', 'h', 'w'):
        a1.add_argument(k, type=int)
    a1.add_argument('out')
    a2 = sub.add_parser('official')
    for k in ('surface', 'labels_dir', 'checkpoint', 'out'):
        a2.add_argument(k)
    a2.add_argument('--height', type=int, default=800)
    a2.add_argument('--width', type=int, default=4400)
    a = ap.parse_args()
    if a.mode == 'canvas':
        canvas_crop(a.surface, a.labels, a.mask, a.y0, a.x0, a.h, a.w, a.out)
    else:
        official_crop(a.surface, a.labels_dir, a.checkpoint, a.out, a.height, a.width)


if __name__ == '__main__':
    main()
