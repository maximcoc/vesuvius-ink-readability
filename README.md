# Scan readability checks for the Vesuvius Challenge

Massimo Cocuzza, October 2026. Report: [REPORT.md](REPORT.md).

Three checks to run on a 9 µm scan before searching it for ink, and the measurements on the eligible scrolls that test them. The full report, with every number, is [REPORT.md](REPORT.md); the dated test log is [docs/PREREGISTRATION_LOG.md](docs/PREREGISTRATION_LOG.md).

- **Does my segment sit on one sheet?** `readability.tifxyz` renders a 41-layer band around an organisers' tifxyz segment straight from the scan volume. `readability.sheets` then measures how much of the segment follows a distinct papyrus sheet and draws a map. The organisers' August guide asks for this check by eye.
- **How much fine texture hides ink in this render?** `readability.clutter` gives a label-free index of fine-scale texture (periods around 75 µm). Across the eligible scrolls it predicts the readability of injected ink.
- **How faint can ink be before my model misses it here?** `readability.bench` blends real letters at reduced contrast into any background renders, reads them with any ink_9um-format model, and reports AUC per scroll with bootstrap intervals.

## Main results

- **Sheet check:**
  - On the three official PHerc. 0841 segments a valid sheet was found on 82-83% of the papyrus. On the six official PHerc. 800 segments it was found on 67% (45-79% by segment), against 63% for our own 800 surfaces. Our renderer matches the official surface volumes at r 0.964-0.976 per layer.
  - On our own PHerc. 0268 surfaces it was found on only 14%, against 63% on PHerc. 800, so our 0268 search says little.
  - The standard 28-layer ink render is too thin for the check: 72-74% on the same segments.
- **Detection limit, for the models tested:** Reader v2 and Reader V3 (Domenico Russo) reach AUC 0.65 at 74-76% of PHerc. 1447's ink contrast. The limit spreads from 0.74 to 0.94 across five public models. No change we tried gained 0.03 AUC. The ideal linear observer (Hotelling on 3D patches, cross-fitted by winding) is at chance on the same bench, so the ink signature at 9 µm is non-linear and the networks are not leaving linear evidence behind.
- **Readability follows render texture, for 1447-type ink:**
  - With PHerc. 1447 letters, the clutter index predicts injected-ink readability: Spearman −0.75 to −0.97 in every variant, including within one campaign.
  - With PHerc. 0841 letters the relation is weaker and depends on the crop window (−0.35 to −0.80).
  - The information sits at periods of about 55-120 µm. Plain gradient energy does about as well; total variance and an existing scan-quality index do not.
- **Campaigns:**
  - With matched renders, the 9.362 µm / 113 keV campaign reads worse by +0.01 to +0.05 AUC, depending on the letter source and crop window.
  - Part of the gap we first reported came from our own renders.
  - Making the backgrounds 8% coarser or finer, the size of the voxel difference, moves readability by as much (up to 0.06), so the gap cannot be put down to the campaign's papyrus texture.
- **Noise:** noise is about 1% of the papyrus clutter at stroke scale. Doubling it costs 0.014 AUC and denoising does not help.
- **Finer voxels, measured once:** the same PHerc. 0841 letters in the same blank papyrus read at 2.403 µm (canonical 2 µm model) and at 9.366 µm (Reader V3): AUC 0.65 at 55% of the contrast against 77%; six letter units, so a wide interval (round 32). Deconvolution at the measured PSF does nothing (round 31).
- **Clutter spectrum and reconstruction:** the ink maps' clutter falls as f^−4, so statistics aggregated over letters, lines or columns lose one to two orders of magnitude of d′ against a stroke-scale detector (round 29). Re-reconstructing the same 9.362 µm acquisition of PHerc. 0139 with weaker phase retrieval doubles the clutter index and costs the readers 0.05-0.08 AUC, so the index and campaign comparisons depend on unpublished retrieval parameters (round 30).
- **Searches:** no candidate in 200 cm² of PHerc. 800 or 261 cm² of PHerc. 0268.

Every test had a pass/kill rule written before its computation: 32 rounds between 12 and 25 October 2026. Amended rules and post-hoc analyses are flagged in the report.

## Tools

| module | what it does | typical cost |
| --- | --- | --- |
| `readability.tifxyz` | renders a band (default 41 layers) around a tifxyz segment from a local zarr volume or the open-data URL, fetching only the chunks the band touches | minutes per segment; about 1.5 GB of chunks per 0841 segment |
| `readability.sheets` | sheet check: share of papyrus with a distinct tracked sheet, centring on the mesh, depth contrast; optional map (`--map`) | about 1 min per winding (CPU) |
| `readability.clutter` | clutter index of a render window, no labels needed | seconds |
| `readability.bench` | injection readability bench: real letters at contrast α in any set of backgrounds, read by any ink_9um-format model; AUC per scroll, bootstrap against a reference scroll, Spearman with the clutter index | about 1 s per blend and α per model (GB10) |
| `readability.infer` | float tiled inference that reproduces the published ink_9um command (checked at r = 1.0000 for Reader v2 and V3) | GPU |
| `readability.texture` | fine-scale texture inside sheets against at their edges; edge width and fringe amplitude | 1-2 min per winding (CPU) |
| `readability.crops` | builds the letter-source crops locally from labelled datasets | minutes |

## Install

Python 3.12+ with `numpy`, `scipy`, `zarr>=3`, `pillow` and `torch` (CUDA), plus the `vesuvius` package from [ScrollPrize/villa](https://github.com/ScrollPrize/villa), used to load ink_9um-format checkpoints. Download the checkpoints from their own pages: [Reader v2](https://github.com/DomRusso2/reader-v2) and [Reader V3](https://huggingface.co/domenicor046/reader-v3).

```bash
pip install -r requirements.txt
```

## Quick start

**Sheet check on an organisers' segment.** The volume can be a local zarr group or the open-data URL; with a URL the needed chunks are cached next to the output.

```bash
python -m readability.tifxyz PHerc0841/segments/20260220213127-w00/mesh/20260220213127-on-20250821151531-9.366um.tifxyz https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com/PHerc0841/volumes/20250821151531-9.366um-1.2m-113keV-masked.zarr w00_41.zarr
```

```bash
python -m readability.sheets w00_41.zarr --map --min-papyrus 0.1
```

The map `w00_41.zarr.sheets.png` is a quarter-size image of the segment:
- green: a distinct sheet centred within ±2 layers of the mesh;
- yellow: a distinct sheet whose centre is further from the mesh (normal when the mesh follows a sheet face);
- red: papyrus without a distinct sheet (fused or crushed sheets, gaps, or a surface that left the sheet);
- grey: not checked.

[docs/sheets_map_0841_w00.png](docs/sheets_map_0841_w00.png) is the map of the official PHerc. 0841 w00 segment.

**Clutter index and texture of a render.** Our renders have 66 layers with the mesh at layer 33 and the ink on the lower-index side. For other renders, set `--surface` and `--side`.

```bash
python -m readability.clutter renders/e050.zarr renders/t033.zarr --rows 500:1320
```

```bash
python -m readability.texture renders/e050.zarr --rows 500:1320 --voxel 8.64
```

**Readability bench.**

```bash
python -m readability.bench configs/example_bench.json out.json
```

Letter-source crops for the bench are built locally, because the labels may not be redistributed:

```bash
python -m readability.crops official PHerc0841/segments/20260220213127-w00/surface-volumes/9.366um-1.2m-113keV-volume-20250821151531.zarr PHerc0841/segments/20260220213127-w00/ink-labels/2.403um-volume-20260319124803/20260918 reader-v2-step040000.pth crops/0841_w00.npz
```

## Results

`results/` holds the numbers behind every table of the report (AUCs, clutter indices, bootstrap intervals, sheet and texture statistics), with an index in [results/README.md](results/README.md). It contains no labels and no image data.

## Data, labels and licences

- **Code:** MIT ([LICENSE](LICENSE)).
- **Scans:** [Vesuvius Challenge open data](https://scrollprize.org/data) (CC BY-NC 4.0). Derived numbers in `results/` follow the same terms.
- **Labels:** the PHerc. 1447 labels (Youssef Nader, ink-8um-pherc1447-surfaces) and the PHerc. 0841 labels (the organisers' ink labels of 2026-09-18) are not redistributed. `readability.crops` rebuilds the crops from the original datasets.

## Credits and prior work

- **Models and code:**
  - Reader v2 and Reader V3 by Domenico Russo;
  - dnative by Erwin Nieuwlaar;
  - Hecate by Giorgio Angelotti;
  - the ink_9um seeds by Elian Rafael;
  - ink-8um-v8in by Youssef Nader;
  - the inference code by the Vesuvius Challenge team ([villa](https://github.com/ScrollPrize/villa)).
- **Data:**
  - the PHerc. 1447 surfaces and labels by Youssef Nader;
  - the PHerc. 343 letters, first found by Erwin Nieuwlaar;
  - the PHerc. 0841 segments and labels by the organisers.
- **Prior work:** related work by others is listed and compared in the report. The closest are:
  - "Measure Before You Hunt" ([gp13](https://github.com/flummoxjr/gp13-ink-detectability));
  - the [uncertainty bench](https://github.com/moisescorreo/vesuvius-uncertainty-bench);
  - [9um-reader-letter-shape](https://github.com/TAUIL-Abd-Elilah/9um-reader-letter-shape);
  - [scrollq](https://github.com/Svyable/scrollq).
- **How the sheet check differs from existing surface checks.** [TIFXYZ Doctor](https://github.com/aviad12g/tifxyz-doctor) and windcheck check a segment's mesh geometry and metadata (topology, folds, self-intersections). [vesuvius-automesh](https://github.com/spencerdavis-tx/vesuvius-automesh) gates its own traced windows. `readability.sheets` instead tests the segment against the sheet structure of the scan along its normals, so it complements them.
- **AI assistance:** this work was carried out with an AI assistant (Claude) under the author's direction. The author set the questions, approved each test and its pass/kill rule before it ran, and reviewed the results.
