"""Readability bench: how well does an ink model see real letters, at reduced contrast, on each scroll's papyrus?

For every scroll, every background render and every letter-source crop, the crop is blended into a window of the render
(readability.blend) at each alpha; the model reads the blend (readability.infer); pixel AUC is pooled per scroll and
alpha (label pixels against other papyrus inside the certainty mask and the joint papyrus, from 2048-bin logit
histograms). Reported: AUC per scroll, the difference to a reference scroll at alpha_ref with a paired bootstrap
(letter components shared across scrolls, 256 px tiles per scroll), the clutter index of the blank windows and its
Spearman correlation with AUC.

Usage:  python -m readability.bench CONFIG.json OUT.json
CONFIG: {"checkpoint": "reader-v3.pth", "window_start": 2, "alphas": [1.0, 0.85, 0.7], "alpha_ref": 0.85,
         "background_surface": 33,                      # mesh layer of the background renders (20 for a 41-layer tifxyz band)
         "sources": ["crops/a.npz", ...],            # npz with R (Ls, H, W) uint8 (reading side = reversed order),
                                                       # lab and cert (H, W) bool
         "scrolls": {"800": ["renders/e050.zarr", ...], ...}, "reference": "800", "bootstrap": 1000}
"""
import json
import sys

import numpy as np
from scipy import ndimage
from scipy.stats import spearmanr

from readability.blend import make
from readability.clutter import clutter_index
from readability.infer import load_model, infer

NBIN = 2048


def _bins(l):
    return np.clip(((l + 20) / 30 * NBIN).astype(int), 0, NBIN - 1)


def auc_h(hp, hn):
    cn = np.cumsum(hn) - hn
    return float((hp * (cn + 0.5 * hn)).sum() / max(1e-12, hp.sum() * hn.sum()))


def run(cfg):
    import zarr
    model = load_model(cfg['checkpoint'])
    S, alphas, aref = cfg['window_start'], [float(a) for a in cfg['alphas']], float(cfg.get('alpha_ref', 0.85))
    SB = int(cfg.get('background_surface', 33))                 # mesh layer of the background renders
    srcs = []
    for p in cfg['sources']:
        z = np.load(p)
        srcs.append((z['R'], z['lab'].astype(bool), z['cert'].astype(bool)))
    HL, HT, clut = {}, {}, {}
    for sc, renders in cfg['scrolls'].items():
        HL[sc] = {a: {} for a in alphas}
        HT[sc] = {a: {} for a in alphas}
        cl = []
        for bi, rp in enumerate(renders):
            B = np.asarray(zarr.open_group(rp, mode='r')['0'][:])
            for ci, (R, lab, cert) in enumerate(srcs):
                r = make(R, lab, cert, B, alphas, bg_surface=SB)
                if r is None:
                    continue
                out, J, info, Bw, s = r
                cl.append(clutter_index(Bw, surface=SB + s, mask=J))
                pos, neg = lab & cert & J, ~lab & cert & J
                comp, _ = ndimage.label(lab)
                lid = ci * 100000 + comp[pos]
                yy, xx = np.indices(lab.shape)
                tid = (bi * 100 + ci) * 100000 + ((yy // 256) * 100 + xx // 256)[neg]
                ut, inv = np.unique(tid, return_inverse=True)
                for a in alphas:
                    b = _bins(infer(out[a][S:S + 17], model)[1])
                    bp, bn = b[pos], b[neg]
                    for u in np.unique(lid):
                        HL[sc][a].setdefault(int(u), np.zeros(NBIN))
                        HL[sc][a][int(u)] += np.bincount(bp[lid == u], minlength=NBIN)
                    h = np.zeros((len(ut), NBIN))
                    np.add.at(h, (inv, bn), 1)
                    for u, row in zip(ut, h):
                        HT[sc][a][int(u)] = row
        clut[sc] = float(np.mean(cl)) if cl else float('nan')
        print(f'{sc}: clutter index {clut[sc]:.4f}', flush=True)
    res = {'auc': {sc: {str(a): auc_h(sum(HL[sc][a].values()), sum(HT[sc][a].values())) for a in alphas} for sc in HL},
           'clutter': clut}
    ref, nb, rng = cfg.get('reference'), int(cfg.get('bootstrap', 1000)), np.random.default_rng(0)
    if ref in HL:
        res['diff_vs_ref'] = {}
        for sc in HL:
            if sc == ref:
                continue
            common = sorted(set(HL[sc][aref]) & set(HL[ref][aref]))
            LA = np.array([HL[sc][aref][c] for c in common])
            LR = np.array([HL[ref][aref][c] for c in common])
            TA = np.array(list(HT[sc][aref].values()))
            TR = np.array(list(HT[ref][aref].values()))
            bs = []
            for _ in range(nb):
                ci = rng.integers(len(common), size=len(common))
                bs.append(auc_h(LA[ci].sum(0), TA[rng.integers(len(TA), size=len(TA))].sum(0)) -
                          auc_h(LR[ci].sum(0), TR[rng.integers(len(TR), size=len(TR))].sum(0)))
            lo, hi = np.percentile(bs, [2.5, 97.5])
            res['diff_vs_ref'][sc] = [res['auc'][sc][str(aref)] - res['auc'][ref][str(aref)], float(lo), float(hi)]
    ks = [k for k in HL if np.isfinite(clut[k])]
    if len(ks) >= 3:
        rho, p = spearmanr([clut[k] for k in ks], [res['auc'][k][str(aref)] for k in ks])
        res['spearman_clutter_auc'] = [float(rho), float(p)]
    return res


def main():
    if len(sys.argv) != 3:
        sys.exit('usage: python -m readability.bench CONFIG.json OUT.json')
    res = run(json.load(open(sys.argv[1])))
    for sc, a in sorted(res['auc'].items(), key=lambda kv: -max(kv[1].values())):
        print(sc, ' '.join(f'{k}:{v:.3f}' for k, v in a.items()), f'clutter {res["clutter"][sc]:.4f}')
    if 'spearman_clutter_auc' in res:
        print('Spearman(clutter, AUC) = %.2f (p %.3f)' % tuple(res['spearman_clutter_auc']))
    json.dump(res, open(sys.argv[2], 'w'), indent=1, default=float)


if __name__ == '__main__':
    main()
