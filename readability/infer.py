"""Float tiled inference for ink_9um-format checkpoints (Reader v2, Reader V3, the villa ink_9um models).

Reproduces the published `vesuvius.ink_detection.inference.infer` command with `--overlap 0.5 --blend-mode hann
--direction reverse`: tile size from the checkpoint (Reader v2 128 px, Reader V3 384 px), stride = tile / 2, Hann
weights, `normalize_robust` per 17 x tile x tile patch, layers reversed (the reading side of our renders). It keeps the
float probability and logit instead of the 8-bit map. Checked at correlation 1.0000 against the published command for
both Reader v2 and Reader V3 (REPORT.md, rounds 4 and 18).

    from readability.infer import load_model, infer
    model = load_model('reader-v3.pth')
    prob, logit = infer(stack17, model)          # stack17: (17, H, W) uint8, file order
"""
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import torch
import zarr
from vesuvius.ink_detection.config import InkConfig
from vesuvius.ink_detection.models.checkpoint import load_checkpoint, select_inference_weights
from vesuvius.ink_detection.models.model import make_model
from vesuvius.ink_detection.inference.inference_runtime import TargetModel
from vesuvius.ink_detection.inference.infer import compute_importance_map_2d
from vesuvius.image_proc.intensity.normalization import normalize_robust

D = 17
POOL = ThreadPoolExecutor(16)


def load_model(ck):
    payload = load_checkpoint(ck)
    config = InkConfig.from_mapping(payload['config'])
    base = make_model(config)
    base.load_state_dict(select_inference_weights(payload, source=ck)[1])
    m = TargetModel(base, input_pad_depth_to=config.model.input_pad_depth_to).cuda().eval()
    m.tile = int(config.model.crop_size[1])
    m.hann = np.asarray(compute_importance_map_2d(patch_size=(m.tile, m.tile), mode='hann').cpu(), np.float32)
    return m


def _positions(n, p, st):
    if n <= p:
        return [0]
    q = list(range(0, n - p + 1, st))
    if q[-1] != n - p:
        q.append(n - p)
    return q


def infer(V, model, batch=None):
    """V: 17-layer window in file order (17, H, W), H and W at least one tile. Returns float32 (prob, logit) maps;
    prob 0 and logit -20 where no tile was run (all-zero tiles are skipped)."""
    P = model.tile
    st = P // 2
    batch = batch or max(4, 64 * 128 * 128 // (P * P))
    V = np.ascontiguousarray(V[::-1]).astype(np.float32)                # reading side, as --direction reverse
    _, H, W = V.shape
    if H < P or W < P:
        raise ValueError(f'window {H} x {W} smaller than the {P} px tile')
    tiles = [(y, x) for y in _positions(H, P, st) for x in _positions(W, P, st) if V[:, y:y + P, x:x + P].any()]
    accp = np.zeros((H, W), np.float32)
    accl = np.zeros((H, W), np.float32)
    wt = np.zeros((H, W), np.float32)
    for i in range(0, len(tiles), batch):
        tb = tiles[i:i + batch]
        xs = list(POOL.map(lambda t: normalize_robust(np.ascontiguousarray(V[:, t[0]:t[0] + P, t[1]:t[1] + P])), tb))
        X = torch.from_numpy(np.stack(xs).astype(np.float32))[:, None].cuda()
        with torch.no_grad(), torch.autocast('cuda', dtype=torch.float16):
            lg = model(X).float()[:, 0].cpu().numpy()
        pr = 1 / (1 + np.exp(-lg))
        for (y, x), l, p in zip(tb, lg, pr):
            accp[y:y + P, x:x + P] += p * model.hann
            accl[y:y + P, x:x + P] += l * model.hann
            wt[y:y + P, x:x + P] += model.hann
    ok = wt > 0
    prob = np.zeros((H, W), np.float32)
    logit = np.full((H, W), -20, np.float32)
    prob[ok] = accp[ok] / wt[ok]
    logit[ok] = accl[ok] / wt[ok]
    return prob, logit


if __name__ == '__main__':
    if len(sys.argv) < 5:
        sys.exit('usage: python -m readability.infer RENDER.zarr LAYER_START OUT.npz CHECKPOINT')
    z, s, out, ck = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
    p, l = infer(np.asarray(zarr.open_group(z, mode='r')['0'][s:s + D]), load_model(ck))
    np.savez_compressed(out, prob=p, logit=l)
    print(out, p.shape)
