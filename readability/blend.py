"""Injection of real letters, at reduced contrast, into ink-free papyrus of another scroll.

A letter source crop (R: Ls layers, oriented so that the reading side is the reversed layer order; lab: ink labels;
cert: where labels are trustworthy) is blended into a window of a background render (66 layers, mesh at layer 33):

    out = m + alpha (R - m) + sqrt(1 - alpha^2) (B' - m)

per layer, with m the source layer mean. B' is the background layer matched to the source layer: the depth offset is
fixed by the two surface layers and refined by +-4 layers (maximum correlation of the mean depth profiles), and B' is
rescaled to the source layer's mean and standard deviation on the joint papyrus. Ink contrast scales by alpha while
texture variance stays constant. The background window is chosen from masks only (maximum joint papyrus coverage).
"""
import numpy as np
from scipy.signal import fftconvolve


def window_from_masks(B, A):
    """position (y, x) of the window of B maximising the overlap of papyrus (B[33] > 0) with mask A"""
    sc = fftconvolve((B[33] > 0).astype(np.float32), A[::-1, ::-1].astype(np.float32), mode='valid')
    return np.unravel_index(int(np.argmax(sc)), sc.shape)


def make(R, lab, cert, B, alphas, pos=None, bg_surface=33, max_shift=4):
    """R (Ls, H, W) uint8 source; lab, cert (H, W) bool; B (66, Hb, Wb) background render.
    Returns ({alpha: uint8 (Ls, H, W)}, J, info, Bw, s) or None when the joint papyrus is too small."""
    Ls, H, W = R.shape
    sc_src = int(round((Ls - 1) / 2 + 0.01))                            # 12 for 24 layers, 14 for 28
    off = int(round(bg_surface - 0.5 - (Ls - 1) / 2))                   # 21 for 24 layers, 19 for 28
    A = (R[sc_src] > 0) & cert
    yb, xb = window_from_masks(B, A) if pos is None else pos
    Bw = B[:, yb:yb + H, xb:xb + W]
    J = (R[sc_src] > 0) & (Bw[bg_surface] > 0)
    if J.sum() < 1000 or (J & cert & lab).sum() < 500:
        return None
    pr = np.array([R[i][J].mean() for i in range(Ls)])
    pb = np.array([Bw[k][J].mean() for k in range(Bw.shape[0])])
    corr = {s: np.corrcoef(pr[2:Ls - 2], pb[2 + off + s:Ls - 2 + off + s])[0, 1] for s in range(-max_shift, max_shift + 1)}
    s = max(corr, key=corr.get)
    Rf = R.astype(np.float32)
    m = np.empty(Ls, np.float32)
    Bm = np.empty_like(Rf)
    for i in range(Ls):
        rk = Rf[i][J]
        bl = Bw[off + i + s].astype(np.float32)
        bk = bl[J]
        m[i] = rk.mean()
        Bm[i] = (bl - bk.mean()) * (rk.std() / max(bk.std(), 1e-3)) + m[i]
    mm = m[:, None, None]
    out = {}
    for a in alphas:
        o = np.clip(np.rint(mm + a * (Rf - mm) + np.sqrt(max(0.0, 1 - a * a)) * (Bm - mm)), 1, 255).astype(np.uint8)
        o[:, ~J] = 0
        out[a] = o
    info = dict(y=int(yb), x=int(xb), shift=int(s), joint_in_cert=float((J & cert).sum() / max(1, A.sum())))
    return out, J, info, Bw, s
