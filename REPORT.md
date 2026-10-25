# Scan readability at 9 µm: tools and measurements for the eligible scrolls

Draft of 25 October 2026. Code and results: https://github.com/maximcoc/vesuvius-ink-readability. Author: Massimo Cocuzza.

This report gives three checks to run on a 9 µm scan before searching it, and the measurements that test them on the eligible scrolls:
- a **sheet check**, which says whether a segment stays on one papyrus sheet and now runs directly on the organisers' tifxyz segments;
- a **clutter index**, which measures the fine-scale texture of a render without labels;
- a **readability bench**, which measures how faint real ink can be before an ink model loses it, on any background and with any ink_9um-format model.

The findings:
- **The detection limit, for the models tested.** Reader v2 and Reader V3 reach AUC 0.65 at 74-76% of PHerc. 1447's ink contrast. No change we tried to the models or their inputs gained 0.03 AUC, though several intervals still include that bar.
- **Readability follows the texture of the render, for 1447-type ink.** With PHerc. 1447 letters, injected-ink readability follows the fine-scale texture of the render at periods of about 55-120 µm. The Spearman correlation is −0.75 to −0.97 in every variant we ran, including within one scan campaign. With PHerc. 0841 letters the relation is weaker and depends on the crop window (−0.35 to −0.80). Total grey-level variance does not predict readability.
- **The campaign comparison is not settled.** Whether the July 2025 9.362 µm / 113 keV campaign as a whole reads worse remains open.
  - With matched renders the gap is +0.01 to +0.05 AUC, depending on the letter source and the crop window.
  - Part of the gap we first measured came from our own renders.
  - Making the backgrounds 8% coarser or finer, the size of the voxel difference, moves readability by as much as that gap. So the gap cannot be put down to the campaign's papyrus texture.
- **The searches.** We found no candidate in 200 cm² of PHerc. 800, nor in 261 cm² of PHerc. 0268, where our surfaces sat on a distinct sheet over only 14% of the papyrus.

Private draft for review; it contains no labels and no revealed text.

## The tools

| tool | question it answers | input | checked against |
| --- | --- | --- | --- |
| `readability.tifxyz` | renders a 41-layer band around a segment, straight from the scan | a tifxyz segment and the scan volume (local zarr or the open-data URL; only the chunks the band touches are fetched) | the official surface volumes of three PHerc. 0841 and six PHerc. 800 segments: per-layer r 0.964-0.976 |
| `readability.sheets` | does the surface sit on one distinct sheet, and where not? | any surface-volume render of about 40 layers or more | reproduces round 22: 0268 14%, 800 63-67% |
| `readability.clutter` | how much fine-scale texture is in this render? | any surface-volume render | injected-ink readability in rounds 12-27 (below) |
| `readability.bench` | how faint can real ink be before this model misses it on this papyrus? | letter crops built locally from labelled data, background renders, an ink_9um-format checkpoint | reproduces rounds 18, 20 and 25 exactly (PHerc. 1203: 0.689 and 0.721) |
| `readability.infer` | float tiled inference | an ink_9um-format checkpoint | the published command, correlation 1.0000 for Reader v2 and V3 |
| `readability.texture` | is fine-scale texture inside the sheets or at their edges? | a render | round 19 |

**Sheet check on the organisers' segments.** The organisers' August guide asks people to check by eye that a segmentation stays on one sheet. `readability.tifxyz` plus `readability.sheets` does this automatically and draws a map:
- green: a distinct sheet centred within ±2 layers of the mesh;
- yellow: a distinct sheet centred further away, which is normal when the mesh follows a sheet face;
- red: papyrus without a distinct sheet.

Results on the organisers' segments and on ours:
- **Official PHerc. 0841 segments (three):** a valid sheet on 82-83% of the papyrus.
- **Official PHerc. 800 segments (six, auto-grown, the only official segments of an eligible scroll besides 1447):** 67% (45-79% by segment).
- **Our own surfaces of PHerc. 800:** 63%. The organisers' auto-grown segments and ours are about equally well placed, and in both about a third of the papyrus shows no distinct sheet at 8.64 µm.
- **Standard ink renders (28 or 31 layers):** the shares are 8-10 points lower, because sheets near the edge of the band cannot close. That is why the adapter renders 41 layers.
- **Our PHerc. 0268 surfaces:** a distinct sheet on only 14%, so a search there says little.

The valid share reflects both the segment and the scan, so the tool reports the depth contrast beside it. The median contrast between sheet and gap is about 60 grey levels on 0841, 26-39 on 800 and 16-18 on 0268. On every set, the tracked sheet centre lies within ±2 layers of the mesh on about a third of the valid pixels. Segments usually follow a sheet face rather than its centre, so that share describes the segment and is not a quality score. An example map is `docs/sheets_map_0841_w00.png`.

## Setup

Every number here comes from our own chain on one NVIDIA GB10 workstation. Each test had a written pass/kill rule before its computation, in a dated log published with the code (`docs/PREREGISTRATION_LOG.md`). We ran 32 rounds between 12 and 25 October 2026. Rules amended before results, and analyses made after seeing the data, are flagged where they are used.

**Data.** All volumes are public Vesuvius Challenge scans:
- **Positives:**
  - PHerc. 343: the letters of the first First Letters award, found by Erwin Nieuwlaar;
  - PHerc. 1447: Youssef Nader's dataset;
  - both at 8.64 µm / 116 keV / 1.2 m;
  - PHerc. 0841: the organisers' labels of 2026-09-18, at 9.366 µm / 113 keV / 1.2 m, plus a 2.403 µm / 77 keV / 0.22 m scan.
- **Searched or measured at 8.64 µm / 116 keV:** PHerc. 800, 0268 and 1218.
- **Measured at 9.362 µm / 113 keV:** nine scrolls of the ESRF campaign of July 2025 (0125, 0191, 0211, 0257, 0358, 0813, 0826, 1203, 1545). Per the organisers' paper, these volumes are 4.681 µm acquisitions at 1.2 m exported with 2× binning. We did not find their phase-retrieval and filter settings documented.

**Chain.** We rebuilt the surfaces ourselves rather than reuse published meshes:
1. axis, distance field, tracks and spiral fit per scroll;
2. hole-free snapping of single windings;
3. renders of 66 layers around each surface (layer 33 is the mesh; the ink sits on the outer face);
4. ink models on a 17-layer window.

We did not use the organisers' Lasagna flattening. On PHerc. 343 the chain re-finds the awarded letters: 12-13 of the 16 covered letter boxes, against 10-15% of random boxes.

**Models.** We compared:
- the villa ink_9um seeds 42 and 43 (Elian Rafael);
- dnative (Erwin Nieuwlaar's fine-tune on PHerc. 0139);
- Hecate (Giorgio Angelotti);
- Youssef Nader's ink-8um-v8in;
- Domenico Russo's Reader v2 and, from 19 October, his Reader V3.

Reader v2 was best on the independent 1447 test (AUC 0.844 and 0.774 on windings w058 and w060) and ran every search. Reader V3 re-ran the main tests and searches.

**Faint-ink benches.** Real letters are blended into ink-free papyrus of another scroll, layer by layer (m = layer mean, I = ink render, B = background, matched in depth and in mean and variance):

    out = m + α (I − m) + √(1 − α²) (B − m)

What the blend does and does not model:
- At α = 1 the output is the source render itself, masked to the papyrus the two renders share.
- Below 1, with equal texture variances, the background supplies 1 − α² of the texture: 28% at α 0.85 and 51% at 0.7.
- Equivalently, α sets an ink-to-clutter ratio: full-strength ink under foreign clutter of relative amplitude √(1 − α²)/α, which is 0.62 at α 0.85 and 1.02 at 0.7.
- The blend cannot represent ink that acts through registration with the fibres, thinner ink with another depth profile, or gain differences between scans.

The benches:
- **T1 (main bench):** the 1447 letters in held-out PHerc. 800 papyrus, three crops of 820 × 4400 px, α from 1 to 0, with 1,000 paired bootstrap resamples over 19 letter components and 160 tiles of 256 px.
- **Readability test:** three letter rows of 1447, or three crops of 0841, blended at α 1, 0.85 and 0.7 into three windings of each of 12 scrolls.
- With 1447 letters the 9.362 µm backgrounds get letters about 8% too large; with 0841 letters the mismatch moves to the 8.64 µm backgrounds.

**Definitions:**
- **AUC:** pooled pixel AUC of label pixels against all other papyrus pixels, inside the labels' certainty mask (where the labelled dataset marks its labels as trustworthy) and the joint papyrus. It is computed from 2048-bin logit histograms. Two variants appear once each: per-winding AUC, and tile-level AUC (the phase test).
- **Detection limit:** α₀.₆₅, the contrast at which pooled T1 AUC falls to 0.65 (linear interpolation).
- **Box test:** a letter box is lit if its mean response exceeds its surrounding ring by 0.3; random boxes give the false-light rate.
- **Campaigns:** "116 keV" = 8.64 µm / 116 keV / 1.2 m; "113 keV" = the nine 9.362 µm / 113 keV / 1.2 m scrolls of July 2025.

The 1447 and 0841 labels are used under their licences and are not redistributed. The 1447 dataset card says the labels were drawn on the w058 and w060 renders and refined for fine-tuning. It does not say whether model predictions guided them; if they did, AUC partly measures agreement with that model family.

## Prior work and what is new

Public work in September and October 2026 had already searched most of these scrolls with the same models and found no text. Our searches repeat part of that coverage. The pages below were read on 24 and 25 October 2026.

**Earlier searches, tests and tools**
- **Searches with no text found:**
  - about 600 windings on ten scrolls ([Jashann/vesuvius-scrolling](https://github.com/Jashann/vesuvius-scrolling));
  - 340 meshes on eight ([pscamillo/vesuvius-eligible-meshes](https://github.com/pscamillo/vesuvius-eligible-meshes), screened in [rodriguescarson/eligible-scroll-atlas](https://github.com/rodriguescarson/eligible-scroll-atlas));
  - PHerc. 800 ([nerln](https://github.com/nerln/vesuvius-first-letters-pherc0800));
  - 0846A including its 2.4 µm band ([ArcheyChen](https://github.com/ArcheyChen/vesuvius-eligible-scouting));
  - 1218 and 1545 ([Bullo27](https://github.com/Bullo27/first-letters-survey)).
- **"Measure Before You Hunt"** ([flummoxjr/gp13-ink-detectability](https://github.com/flummoxjr/gp13-ink-detectability), August 2026): a label-free scan-quality index on 14 scrolls. It finds the same campaign split, but rates the 113 keV scans as the better ones and says "scan quality is not readability". It also has a sheet-separability axis, an ink-mass ceiling on detached fragments and a lead K-edge screen.
- **[moisescorreo/vesuvius-uncertainty-bench](https://github.com/moisescorreo/vesuvius-uncertainty-bench):**
  - injection power curves on 1203 and 0009B;
  - benchmarks at 116 keV (PHerc. 0343P) and 113 keV (PHerc. 0500P2), with labels transferred from the organisers' fine-scan predictions;
  - no checkpoint beating a substrate-only baseline at 116 keV (AUC 0.577).
- **[TAUIL-Abd-Elilah/9um-reader-letter-shape](https://github.com/TAUIL-Abd-Elilah/9um-reader-letter-shape):**
  - Fine-tuning Reader v2 with a shape loss leaves AUC unchanged (0.856) but raises a letter-scale score from 0.126 to 0.181.
  - In a blind read on PHerc. 0841, the fine-tuned 9 µm reader gave 3 of 8 letters and the 2.4 µm map 6 of 8.
- **[Svyable/scrollq](https://github.com/Svyable/scrollq):** a scan-health board over 64 volumes, explicitly not a readability score.
- **Surface quality checks listed on the organisers' [community projects](https://scrollprize.org/community_projects) page (read 25 October 2026):**
  - [TIFXYZ Doctor](https://github.com/aviad12g/tifxyz-doctor) (Aviad Cohen) checks the integrity, metadata and geometry of tifxyz grids: topology, edge lengths, folded triangles, normal-offset steps.
  - windcheck (Josep Carreras) finds where a traced surface passes through itself, from mesh geometry alone.
  - [vesuvius-automesh](https://github.com/spencerdavis-tx/vesuvius-automesh) gates its own automatically traced Scroll 3 windows by render QC and a topology check.
  - [Herculaneum Scroll Tools](https://github.com/axiosdevs/herculaneum-scroll-tools) audits the volume-level surface predictions against the CT, not segments.
  - None of them tests a segment against the sheet structure of the scan along its normals, which is what our sheet check does. It complements the geometry checks rather than replacing them.
- **[aviad12g/vesuvius-depth-order-control](https://github.com/aviad12g/vesuvius-depth-order-control):** Hecate lights more pixels on depth-shuffled input, so candidates must be judged by shape.
- **The organisers:**
  - They scan at 2.4 µm, 77-78 keV and 22 cm, after letters appeared in Scroll 4 only at that resolution ([21 December 2025](https://scrollprize.substack.com/p/finallyletters-in-scroll-4)).
  - Their paper on PHerc. 1667 ([arXiv 2606.29085](https://arxiv.org/html/2606.29085)) calls the 9.362 µm data "pixel-limited". It attributes blur to decoherence by the papyrus's cell structure, which grows with propagation distance (their rule: about 0.5 m at 4.6 µm pixels).
  - Their [open problems](https://scrollprize.org/2026_open_problems) ask why 9 µm / 110 keV scans read worse, and for scan-quality metrics. Their Appendix B notes that ink information may live at very small scales.

**New here:**
1. A readability bench with real letters from two scans (1447 at 116 keV, 0841 at 113 keV), read by two models on 12 eligible scrolls.
2. A label-free texture index validated against that bench for 1447-type ink, within one campaign and with matched renders. The band where readability information lives: periods of 55-120 µm. Total variance and gp13's index do not predict readability.
3. A measured voxel-size effect: making a background 8% coarser costs these models up to 0.06 AUC.
4. The sheet check, now runnable on the organisers' tifxyz segments. As far as we found, it is the only public check of a segment against the sheet structure in the CT; the existing checks look at mesh geometry and metadata.
5. A noise-versus-clutter budget at stroke scale.
6. Reader V3 halves false lights at the same sensitivity.
7. An ideal-linear-observer benchmark (Hotelling on 3D patches, cross-fitted by winding) on the same bench: at chance, so the ink signature at 9 µm is non-linear and the networks are not leaving linear evidence behind.
8. The clutter power law: the papyrus texture of every scroll falls as about f^−2 at periods of 60-250 µm and steeper below 60 µm (the resolution roll-off); the ink maps fall as f^−4. By Burgess's size law this prices every "aggregate over a larger area" idea on 9 µm maps at one to two orders of magnitude below a stroke-scale detector.
9. A reconstruction-setting test on the same acquisition (PHerc. 0139 original against two re-retrievals): the setting moves the clutter index by 2× and the readers by 0.05-0.08 AUC, so scan-quality indices and campaign comparisons depend on unpublished retrieval parameters.
10. A same-letters, same-papyrus comparison of the 2.403 µm and 9.366 µm scans of PHerc. 0841: ink readable at 2.4 µm down to about 55% of the contrast that the 9 µm reader needs (six letter units, wide interval).

**Independent confirmations of earlier work:**
- no pixel-AUC gain from fine-tuning at 9 µm (TAUIL, Jashann);
- no ink-mass or lead signal (gp13 on fragments; ours on 1447 in the scroll);
- the 113 keV scans differ from the 116 keV ones (gp13, which reads them the other way);
- finer voxels help (the organisers' Scroll 4 result, TAUIL's blind read; not measured here).

## Detection limit

For the models tested, PHerc. 1447 ink in PHerc. 800 papyrus is seen down to about three quarters of its contrast.

| model | AUC at α 1 | 0.85 | 0.7 | 0.5 | α₀.₆₅ |
| --- | --- | --- | --- | --- | --- |
| Reader V3 | 0.826 | 0.725 | 0.623 | 0.542 | 0.74 |
| Reader v2 | 0.808 | 0.708 | 0.612 | 0.536 | 0.76 |
| dnative | 0.786 | 0.652 | 0.577 | 0.527 | 0.85 |
| ink_9um seed 42 | 0.695 | 0.605 | 0.544 | 0.507 | 0.92 |
| ink_9um seed 43 | 0.691 | 0.589 | 0.533 | 0.493 | 0.94 |

- **The cut-off matters.** For Reader v2 and V3 the limit is α 0.67 and 0.64 at AUC 0.60, 0.76 and 0.74 at 0.65, and 0.84 and 0.81 at 0.70.
- **The model matters.** The limit spreads from 0.74 to 0.94 across the five models; training on native 8.64 µm data (Reader v2) beat simulated 9 µm data (ink_9um).
- **Evidence falls faster than contrast.** In d′ terms Reader v2 gives 1.24, 0.78, 0.39 and 0.14 at α 1, 0.85, 0.7 and 0.5, so d′ ∝ α^3.3.
  - A linear detector under this blend would lose evidence only in proportion to α. But the optimal linear detector sees nothing here (next bullet), so the steep fall is not an inefficiency relative to a linear optimum.
  - **The ideal linear observer is at chance (round 28).** A Hotelling (Fisher) discriminant on 3D patches of the standardised 17-layer window (15×15 or 21×21 px, covariance from signal-free papyrus, fitted on one winding's letters and scored on the other's) gives AUC 0.48 at every α, against 0.83 for Reader V3 at α 1; a quadratic Gabor-energy observer gives 0.51. The observer is sound: on its own training blends it reaches 0.58-0.63, on new letters of the same winding 0.57-0.61, and its α 0 and shifted-label controls sit at 0.47-0.50. What it learns in-sample is mostly a brightness offset that changes sign between windings. So at 9 µm there is no linear template of ink; the networks' evidence is non-linear fine structure (phase randomisation destroys it, below), and no linear detector of this patch size can replace them.
  - Float logits give the same AUCs as the stored 8-bit maps.
- **Reader V3 is cleaner, not more sensitive.** At the threshold that finds half the letters it lights 7.5% of blank papyrus, against 14.6% for Reader v2. Its gain at α 0.7-0.5 is +0.008 [−0.022, +0.030].
- **The PHerc. 343 fade test agrees.** Reader v2 lights 75% of the 343 letter boxes at full strength, 50% at α 0.7 and 25% at 0.5, against 10-15% of random boxes. Reader v2 was trained on fragment 343P, so this curve is optimistic.
- **No change we tried moved it.** None reached its pass bar (+0.02 to +0.05 AUC at α 0.7-0.5; see Negative results):
  - fine-tuning on faint stamps;
  - weight averaging;
  - depth and model ensembles;
  - fine-tuning on real 1447 letters;
  - Reader V3.

  Several intervals still include the bar, so those are inconclusive rather than excluded. A shape-level loss (TAUIL) may still help at letter scale.

The bound for searches is limited:
- A Reader v2 or V3 search that finds nothing is weak evidence against ink fainter than about three quarters of 1447's contrast, and only in the area searched.
- Our visual candidate rule was not calibrated by blind injection, so this is not a detection probability.
- The limit is measured with one ink source (1447, 19 letter components) in one background scroll (800).

## Readability across scrolls and renders

Injected-ink readability at α 0.85 varies by 0.11-0.14 AUC between the 12 scrolls. The fine-scale texture of each render predicts it.

| scroll | campaign | clutter index | 1447 letters, Reader v2 | 1447, V3 | 0841 letters, Reader v2 | 0841, V3 |
| --- | --- | --- | --- | --- | --- | --- |
| 0268 | 116 keV | 0.102 | 0.755 | 0.762 | 0.740 | 0.767 |
| 0800 | 116 keV | 0.085 | 0.737 | 0.758 | 0.762 | 0.786 |
| 1218 | 116 keV | 0.111 | 0.709 | 0.714 | 0.744 | 0.754 |
| 0191 | 113 keV | 0.124 | 0.715 | 0.703 | 0.717 | 0.722 |
| 1203 | 113 keV | 0.114 | 0.691 | 0.689 | 0.713 | 0.709 |
| 0826 | 113 keV | 0.128 | 0.688 | 0.680 | 0.721 | 0.704 |
| 0125 | 113 keV | 0.142 | 0.687 | 0.678 | 0.714 | 0.727 |
| 0211 | 113 keV | 0.139 | 0.689 | 0.676 | 0.726 | 0.718 |
| 0358 | 113 keV | 0.146 | 0.673 | 0.673 | 0.708 | 0.655 |
| 0813 | 113 keV | 0.143 | 0.687 | 0.667 | 0.705 | 0.702 |
| 0257 | 113 keV | 0.157 | 0.668 | 0.656 | 0.666 | 0.652 |
| 1545 | 113 keV | 0.154 | 0.646 | 0.653 | 0.634 | 0.642 |

AUC at α 0.85, round 21; the 116 keV rows use careful-fit renders, the 113 keV rows survey renders (see "The campaign comparison" below). Every number, with α 1 and 0.7 and intervals against PHerc. 800, is in `results/per_scroll.csv`.

The same comparison on 11 survey renders with a matched pipeline (Reader V3, AUC at α 0.85; the clutter index of the background windows differs with the letter source's window and depth):

| survey renders | campaign | 1447 letters: clutter | AUC | 0841 letters: clutter | AUC |
| --- | --- | --- | --- | --- | --- |
| 0268 (t072-t074) | 116 keV | 0.109 | 0.750 | 0.135 | 0.704 |
| 1218 (t036-t038) | 116 keV | 0.117 | 0.708 | 0.116 | 0.730 |
| 0191 | 113 keV | 0.124 | 0.703 | 0.116 | 0.744 |
| 1203 | 113 keV | 0.114 | 0.689 | 0.108 | 0.721 |
| 0826 | 113 keV | 0.128 | 0.680 | 0.123 | 0.715 |
| 0125 | 113 keV | 0.142 | 0.678 | 0.146 | 0.737 |
| 0211 | 113 keV | 0.140 | 0.676 | 0.139 | 0.719 |
| 0358 | 113 keV | 0.146 | 0.673 | 0.147 | 0.677 |
| 0813 | 113 keV | 0.143 | 0.667 | 0.156 | 0.713 |
| 0257 | 113 keV | 0.157 | 0.656 | 0.162 | 0.665 |
| 1545 | 113 keV | 0.154 | 0.653 | 0.154 | 0.644 |

- **The clutter index predicts readability:**
  - The index is the share of near-surface papyrus variance in a difference-of-Gaussians band (σ 1 and 3 px, peak period about 75 µm), on the ink side of the mesh.
  - Its Spearman correlation with AUC is −0.80 to −0.97 in the four tests over 12 scrolls, −0.67 to −0.93 within the nine 113 keV scrolls, and −0.71 and −0.95 over the 11 survey renders with a matched pipeline.
  - Leave-one-scroll-out, a linear fit on the index predicts AUC to 0.015-0.030, against 0.031-0.047 for the mean.
  - With 1447 letters the relation held in every variant, down to −0.75 within the nine scrolls with crops cut to 720 rows (round 26).
  - With 0841 letters it fell to −0.40 (p 0.12) with the cut crops, so for that ink source it depends on the window.
- **The information sits at 55-120 µm (round 27):**
  - Variance shares in bands peaking near 60, 75 and 120 µm predict about equally well.
  - A band near 30 µm predicts less, and bands at 180 µm and coarser do not.
  - Plain gradient energy does about as well as our index, while total variance (|ρ| ≤ 0.66) and normalised variance do not.
  - This is the band where the 113 keV texture excess sits (below), but the link is still a correlation.
- **gp13's index does not predict injected readability.** Its structural SNR gives ρ −0.36 to −0.53 over the 12 scrolls (permutation p 0.08-0.24) and −0.20 to +0.23 within the nine 113 keV scrolls.
- **No quiet zones were detected inside PHerc. 800.** In 80 positions across its 20 windings, local AUC varies by 0.086 (10th-90th percentile), below the 0.10 rule.
- **PHerc. 0268 is not a reliable reading.** Its renders show a distinct sheet on only 14% of the papyrus, because sheet and gap differ by about 16 grey levels instead of 33.

**The campaign comparison.** In the round-21 table, the nine 113 keV scrolls read worse on average than the three 116 keV ones in all four tests, by 0.048-0.077 AUC.
- **Scroll-level test:** with the scroll as unit, the exact permutation test over all 220 splits gives p 0.0045-0.009 at α 0.85, and 0.009-0.027 at α 0.7. The groups separate fully in three of four tests at α 0.85, and in none at α 0.7.
- **But the comparison was confounded by our own renders:**
  - The 116 keV backgrounds were careful fits.
  - The 113 keV ones were short survey bands with holes.
  - Even at α 1, where the blend returns the source render, 1447 letters read by Reader V3 scored 0.84 on the careful renders and 0.80 on survey renders.
- **Matched renders (round 25).** Survey renders of 1218 and 0268, read like the nine:
  - **1447 letters:** the gap survives (0.729 against 0.675, +0.054; 1218 and 0268 rank first and second of 11, exact p 0.018).
  - **0841 letters:** it vanishes (0.717 against 0.704, +0.013, p 0.36).
  - The pre-registered verdict is MIXED.
- **Voxel size (round 26).** We resampled the survey renders by the 8% voxel difference, band-limited, both ways, and reran the bench. The letter crops were cut to 720 rows and the native renders rerun the same way:

  | letters | native gap | 116 keV made coarser | 113 keV made finer |
  | --- | --- | --- | --- |
  | 1447 | +0.041 | −0.026 | +0.005 |
  | 0841 | +0.031 | −0.062 | +0.041 |

  - An 8% change of voxel size moves readability by as much as the campaign gap.
  - The pre-registered verdicts were PARTIAL (the gap closes when the 116 keV scrolls are made coarser, not when the 113 keV ones are made finer) and MIXED (0841 letters read best on 8.64 µm grids, 1447 letters only partly).
  - Cutting the crops also moved the 0841 gap from +0.013 to +0.031, so such gaps carry about ±0.02 from analysis choices alone.
- **Not separated:** the campaigns also differ in papyri, date, energy, binning and reconstruction, and the comparison is three scrolls against nine. Round 30 shows that the reconstruction alone can move the clutter index by 2× and the AUC by 0.05-0.08, so an unpublished retrieval difference between the campaigns could account for the whole gap.

What holds:
- With 1447-type ink, readability follows the measured texture of the render in both campaigns, and the campaign label adds little once texture is known.
- Coarser voxels cost these models readability.

What does not hold is a clean campaign effect. Voxel size, the models' domain, our renders and the crop window each move the gap by 0.01-0.06.

The index predicts the readability of injected ink; whether it predicts native readability across scrolls is untested. It is a property of the released volume, not of the papyrus: re-reconstructing the same acquisition with weaker phase retrieval doubles it (round 30).

## Why the ink is hard to see

**Noise is small at stroke scale.**
- In void voxels, noise variance is 1.0-1.3% of the papyrus variance in a band of σ 3-15 px (26-130 µm). In the finest band (σ 1-3 px) its share is larger: 18% at 8.64 µm and 6% at 9.362 µm.
- Doubling the noise lowers T1 AUC from 0.808 to 0.794, as much as lowering the ink contrast to α_eq = 0.979. Read through the blend, that makes noise a share x = (1/α_eq² − 1)/k = 0.04 of the total interference (k = 1 for doubled noise). Denoising the 9.362 µm scans changed AUC by +0.000 to −0.026.
- At these voxel sizes more dose or a denoiser is unlikely to lift the ink. The noise share at finer voxels is unmeasured.

**Reader v2 uses fine spatial arrangement.**
- A Gaussian blur of σ 2 px (17 µm) lowers AUC to 0.703 and σ 4 px to 0.564; removing everything coarser than 16 px only to 0.773.
- Keeping each tile's amplitude spectrum but randomising its phase drops tile-level AUC from 0.877 to 0.492.
- So the amplitude spectrum alone is not what the network uses. These tests probe a network trained on sharp data, so they also include domain shift.

**That detail is near the resolution limit.**
- The 10-90% width of the outer sheet edge is 25-35 µm (2.8-4.1 voxels). This is an upper bound on the scanner's blur, since roughness, tilt and registration widen it.
- It is 2.8 voxels in both campaigns (26 and 24 µm).

**No extra mass under the ink.**
- With whole letters, depth-integrated attenuation under 1447 letters is −4.3% [−7.2, −1.2] of the local sheet mass. This statistic was chosen after the pre-registered one gave an invalid +10-14%.
- Given that analysis uncertainty, a carbon-film excess of 15% or more is excluded; one of 6-15% is not, and no positive control was run.
- Lead was not converted to an areal density.

**The clutter is red, so bigger targets are not easier.**
- Papyrus renders of the 12 scrolls have power-law spectra with β 2.5-3.7 over periods 25-250 µm: about 2.0-2.5 at 60-250 µm (the texture proper) and 3-6 below 60 µm (the resolution roll-off). The Reader V3 map on blank papyrus has β 4.08 [4.06, 4.10].
- For a linear statistic at fixed per-pixel contrast, d′ scales as D^(1 − β/2) with the target size D (Burgess 2001). On these maps a 1 mm letter keeps 9% of a 100 µm stroke's d′, and a 6.5 mm line 1%. Aggregation over layout cannot recover faint text here (rounds 3, 7 and 29).

**Geometry does not carry it.**
- The gap to the next winding does not follow the strokes (AUC 0.552, against 0.519-0.528 with shifted labels).
- Bright specks are as common on the verso as on the recto in all 14 scrolls checked (ratio 0.94-1.11).

**The 113 keV texture excess is inside the sheets.**
- Over 36 renders, the fine-scale fraction inside the sheets is 1.35 times higher in the nine 113 keV scrolls than in the 116 keV ones. At the edges it is 1.17 times higher, with equal fringe amplitude (0.075 and 0.074) and equal edge width in voxels.
- Raw CT slices show no extra ring energy (113/116 ratio 0.73), and the spectral ratio does not follow a single power law.
- This is a structured background at 40-90 µm periods in the reconstructed volumes. Object and acquisition are not separated.
- A plausible acquisition cause is the organisers' decoherence: the 9.362 µm volumes are binned 4.681 µm acquisitions at 1.2 m, beyond their own rule of about 0.5 m at that pixel size. Binning and aliasing were not tested.
- **The retrieval setting moves everything (round 30).** PHerc. 0139 exists as the released volume and as two re-retrievals of the same acquisition (pag0, pag50). On two labelled segments the re-retrievals have twice the clutter index (0.056 → 0.111 / 0.125), three times the gradient energy and the void-noise share (0.028 → 0.084 / 0.095), five to eight times the edge fringe and sharper sheet edges (1.0 against 2.4 layers), and both readers lose 0.05-0.08 AUC on them (intervals exclude 0; the models were trained on the original, so the loss is not a verdict on the setting itself). So a reconstruction setting changes the clutter index and the AUC by as much as the whole campaign gap. The retrieval parameters of the released volumes are not published; a difference between campaigns cannot be excluded.

**A different protocol at 9.4 µm was not shown to help (round 24, MIXED).**
- On the same PHerc. 0841 papyrus we compared two 9.37 µm volumes: the 113 keV / 1.2 m scan, and a copy of the 2.403 µm / 77 keV / 0.22 m scan box-filtered and resampled to that grid (not a native acquisition).
- The copy has 8-15% less interior texture. Reader V3 read native ink equally well (ΔAUC −0.001 and +0.004 on two segments), Reader v2 slightly better (+0.014 and +0.026).
- This was full-strength ink on two segments of one scroll, without intervals.

## Searches

We found no candidate.

| scroll | region searched | area | with a valid tracked sheet | outcome |
| --- | --- | --- | --- | --- |
| PHerc. 800 | 20 hole-free windings (e050-e069), z 11000-12500 | 199.9 cm² | 63%, about 126 cm² | No candidate with Reader v2, Reader V3, the villa models or Nader's model. One weak lead under the rule: a single 6 mm cluster of stroke-like shapes in e053, with no second line |
| PHerc. 0268 | 16 windings (T067-T082), z 6610-8110 | 260.9 cm² | 14%, about 38 cm² | No candidate with Reader v2 or V3. The best tiles show blobs that repeat on the blind side and 12 layers deeper, along fibre bands, cracks and folds |
| PHerc. 1218 | 4 windings around a survey lead, z 10890-12390 | 4 × about 5 cm × 13 mm | | Lead closed: the response follows bright, porous material in the CT (local correlation 0.57), not lines |
| 11 survey scrolls | 53 windings in 4 mm bands | short strips | | No line of letter-like strokes; a Hecate lead on 1203 closed |
| PHerc. 0175B | 2 pseudo-windings | none valid | | Not measurable: the sheets look fused |

A region counted as a candidate only if all of these held:
- stroke-like marks formed at least two parallel lines 3-7 mm apart on the reading side;
- the marks appeared at two neighbouring depths;
- they were absent 12 layers deeper and on the blind side;
- no material anomaly in the CT explained them.

The PHerc. 800 search repeats a public null (nerln) on different windings. It says nothing about ink fainter than about three quarters of 1447's contrast or about unsearched windings.

PHerc. 800 also has six official auto-grown segments, published on 7 September 2026 (about 20 cm², z 10860-13243, inside our searched band). We searched our own surfaces and did not read those segments with the ink models; the sheet check on them is in "The tools".

## Negative results

Each row below was judged by a rule written before its computation, unless marked otherwise:
- **Trying to lower the limit:** eight changes to the models or their inputs, plus a model-free reference. None reached its bar, but four intervals still include it, so those are inconclusive, not excluded.
- **Other signatures, or places where ink would be easier:** the rest of the rows.
- One false-positive filter came out partial, two protocol comparisons came out mixed, and one source of labels exists only on paper.

Round numbers are in brackets; AUC gains are at α 0.7-0.5 on T1 unless stated.

| route | idea (round) | pass criterion | outcome |
| --- | --- | --- | --- |
| Model | Fine-tune Reader v2 on faint 343 ink stamped into 800 papyrus (4) | gain ≥ +0.03, no loss at full strength | KILL, inconclusive: +0.014 [−0.037, +0.074]; −0.050 at full strength |
| Model | Average original and fine-tuned weights, WiSE-FT (5) | as round 4 | KILL, inconclusive: +0.020 [−0.010, +0.054] |
| Model | Fine-tune on real 1447 letters, cross-fitted by winding (6) | gain ≥ +0.05 for both seeds | KILL, excluded: −0.001 [−0.031, +0.028] and −0.008 |
| Model | Ensembles over depth windows and over four model families (10) | gain ≥ +0.02 | KILL: depth +0.004 [−0.006, +0.015], excluded; families −0.009 [−0.047, +0.029], inconclusive |
| Model | A newer reader, Reader V3 (18) | gain ≥ +0.03 | KILL, at the bar: +0.008 [−0.022, +0.030]; false lights halved |
| Model | Evidence lost in 8-bit maps or box tests (5) | d′ exponent ≤ 2 from float logits | KILL: identical AUCs, d′ ∝ α^3.3 |
| Model | Ideal linear observer (Hotelling on 15-21 px × 17-layer patches, cross-fitted by winding) beats the networks at faint contrast (28) | HO − V3 ≥ +0.03 at α 0.7-0.5, interval above 0 | DATA LIMIT: −0.099 [−0.153, −0.029]; AUC 0.48 at every α; in-sample 0.58-0.63; one visual control not met because the observer sees nothing, verified post hoc |
| Processing | Re-align renders to the sheet centre or edges (1) | +2 letter boxes or better retention | KILL: every lock loses boxes |
| Processing | Cross-scroll matched filter on depth profiles; notch along the fibres (1) | boxes ≥ 2× random on both scrolls | KILL: d′ 0.17-0.26, no boxes |
| Processing | In-plane deconvolution of the renders before inference (Richardson-Lucy or Wiener at the measured PSF, σ 0.8-1.6 px; variant chosen on T1b) (31) | gain ≥ +0.03, no loss at full strength | KILL: −0.001 [−0.027, +0.028] for V3 with RL σ 1.6; +0.003 for v2; false lights 0.077 → 0.062 |
| Signal | Areal mass excess under ink (9) | AUC ≥ 0.60 on both 1447 windings | KILL: AUC 0.44-0.50 (mass bound post hoc, see Why) |
| Signal | Lead-bearing specks on the inked face (5) | letter/random ≥ 2, or recto/verso ≥ 1.5 | KILL: 0.92 and 1.16; recto/verso 0.94-1.11 in 14 scrolls |
| Signal | Strokes change the gap to the next winding (8) | AUC ≥ 0.58 or ≤ 0.42, same sign on 343 | KILL: 0.552; opposite sign on 343 |
| Signal | Ink set off onto the facing winding (1, 2) | facing correlation ≥ 3× non-facing | KILL: equal both ways (r 0.08-0.14) |
| Signal | A dual-energy pair already in the open data (8) | two scans ≥ 10 keV apart, voxel sizes within 1.5× | CLOSED (not a test): only 0846A and 1203 have a second scan, at 2.4 µm |
| Signal | More dose, or a denoiser (5, 13) | noise share x (see Why) ≥ 0.38 to pass, ≤ 0.15 to kill | KILL: x = 0.04; denoising +0.000 to −0.026 |
| Signal | The 113 keV texture is a reconstruction artefact: rings or a filter tilt (23) | ring share ≥ 2×, or one shared power-law tilt | KILL for these two kinds: ring ratio 0.73; no power law (R² 0.54) |
| Layout | Class averaging of letter-sized patches (3) | reproducibility at α 0.7 above blank + 3 SD | KILL: below blank papyrus |
| Layout | Column periodicity over 1.5 m of arc (7) | ≥ 80% detection at α 0.85, ≤ 2% false | KILL: 0 of 50 detected even at full strength |
| Layout | Could any statistic aggregated over a larger area help? Power-law exponent β of the Reader V3 map on blank papyrus (29) | layout excluded if β ≥ 2 with the interval above 2 | LAYOUT EXCLUDED: β 4.08 [4.06, 4.10] on 800, 4.04 on 0268; for a linear statistic at fixed per-pixel contrast d′ falls to 0.09 of a stroke's at 1 mm and 0.01 at the line pitch |
| Filter | Depth fingerprint of letters against false lights (10, 11) | test AUC ≥ 0.80, ≤ 10% of lights pass | PARTIAL: AUC 0.73-0.75, but 29-57% of lights pass |
| Where | Ink easier where the recto faces a gap (5) | open minus fused AUC ≥ +0.08 | KILL, excluded: −0.045 [−0.100, +0.018] |
| Where | Ink easier in less dense or thinner sheet (12) | low minus high tertile AUC ≥ +0.05 | KILL, inconclusive: +0.023 [−0.065, +0.103] |
| Where | Quiet zones inside PHerc. 800 (12) | local AUC spread ≥ 0.10 | KILL: 0.086 |
| Where | Searched bands fall in margins or the wrong radius (5, 10) | desk check | Not a test: bands are 5.7-9.7 cm from the ends; known finds span the radius |
| Where | A scroll that reads clearly better than 800 (12, 14, 21, 22) | AUC at α 0.85 ≥ 800 + 0.05 | KILL: best was 0268 at +0.017, on surfaces that rarely sat on distinct sheets; the raw-CT proxy failed calibration |
| Scan | A different 9 µm protocol reads better (24) | V3 gain ≥ +0.03 with less texture | MIXED: V3 −0.001 and +0.004; texture 8-15% lower |
| Scan | The campaign gap is our render pipeline (25) | two 116 keV survey-render scrolls vs the nine | MIXED: gap +0.054 with 1447 letters, +0.013 with 0841 letters |
| Scan | The campaign gap is voxel size (26) | resampling closes at least half of the gap both ways | PARTIAL: it closes one way only; mechanism MIXED, with 0841 letters reading best on 8.64 µm grids |
| Scan | The 2.403 µm scan reads fainter ink than the 9.366 µm scan of the same PHerc. 0841 letters (canonical 2 µm model against Reader V3, same blank papyrus) (32) | α₀.₆₅ lower by ≥ 0.15 and the difference at α 0.5 with the interval above 0 | PARTIAL: α₀.₆₅ 0.55 against 0.77 (met), difference at α 0.5 +0.103 [−0.043, +0.238] over six letter units (not met); the 2.403 µm reader at 85% contrast equals the 9.366 µm reader at full strength |
| Scan | A different reconstruction of the same 9.362 µm acquisition reads better: PHerc. 0139 original against the organisers' pag0 and pag50 re-retrievals, two labelled segments (30) | a re-retrieval gains ≥ +0.03 AUC with the interval above 0 for both models | WORSE OR AMBIGUOUS: −0.05 to −0.08 for both models (intervals exclude 0), but every public model was trained on the original reconstruction; label-free, the re-retrievals have 2× the clutter index, 3× the void noise, 5-8× the edge fringe and sharper edges (1.0 vs 2.4 layers) |
| Labels | Opened pieces of eligible rolls as in-domain labels (1) | ≥ 3 rolls with reachable pieces | PASS on paper (0268, 0358, 0826), but no scans or images today |

## Recommendations for the next scans

In order of how directly our data support them:

1. **Check that every segment sits on one sheet before searching it.** On PHerc. 0268 our surfaces found a distinct sheet on only 14% of the papyrus, and the search there says little. The check now runs on the organisers' tifxyz segments in minutes.
2. **Rank renders by fine-scale texture before searching.** The index (or plain gradient energy) predicts injected-ink readability across and within campaigns for 1447-type ink, less reliably for 0841-type ink. Validated on injected ink only, it is a screening tool, not a guarantee.
3. **Finer voxels: measured on one scroll (round 32).** The same PHerc. 0841 letters, blended at reduced contrast into the same blank papyrus of w00 at each voxel size, read by the organisers' canonical 2 µm model on the 2.403 µm scan and by Reader V3 on the 9.366 µm scan: AUC 0.65 is reached at 55% of the letters' contrast at 2.403 µm against 77% at 9.366 µm, and the 2.403 µm reader at 85% contrast matches the 9.366 µm reader at full strength. The comparison mixes voxel size with energy, distance and reader, and its bootstrap rests on six letter units (interval at α 0.5: +0.10 [−0.04, +0.24]), so it is a measurement with a wide uncertainty, not a closed verdict. Letters appeared in Scroll 4 only at 2.4 µm, and TAUIL's blind read found 6 of 8 letters at 2.4 µm against 3 of 8 with a fine-tuned 9 µm reader. Our other data are consistent with this:
   - the evidence the models use sits near the resolution limit;
   - noise is small at 9 µm;
   - making a background 8% coarser cost the models up to 0.06 AUC.

   For the eligible scrolls this prices the 2.4 µm route: a 9 µm null bounds ink above about 75% of 1447's contrast, and the 2.403 µm scans of PHerc. 1203 and 0846A would see ink down to roughly half of that, if 0841 generalises.
4. **Publish the retrieval parameters of every released volume, and sweep them once.** A re-retrieval of PHerc. 0139 with weaker phase retrieval doubled the clutter index and cost the readers 0.05-0.08 AUC; stronger smoothing lowered clutter at the price of sharpness (edges 2.4 against 1.0 layers). If the projections are kept, a δ/β sweep on one labelled 9 µm scroll, read by a model trained at each setting, would price that trade for the models in use. Until the parameters are known, scan-quality indices and campaign comparisons carry this confound.
5. **Separate object from acquisition with one calibration piece.** Scan a blank carbonised piece and a graded ink wedge over a small protocol matrix (for example 77, 100 and 113 keV; 0.2, 0.6 and 1.2 m; 2.4, 4.7 and 9.4 µm). This would settle whether the 113 keV texture comes from the papyri or the set-up, and give α a physical unit. Opened pieces of 0268, 0358 and 0826 in Naples frames could also give in-domain labels, as PHerc. 1667's Fragment 5 did.
6. **Lead K-edge subtraction only where XRF finds lead in the writing.** Two scans bracketing 88.0 keV cancel the attenuation of carbon, but about a tenth of the phase term survives between 86 and 90 keV, so phase retrieval or a short distance is needed. In-situ XRF screening of library scrolls has been proposed ([PLOS ONE, 2026](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0353485)).
7. **Other contrast mechanisms are speculative.** Neutron plus X-ray tomography and dark-field imaging could in principle separate soot from char, but resolution and sensitivity at these scales are unproven.

What our tests argue against, at 8.64-9.362 µm:
- more dose, a denoiser, or a deconvolution at the measured PSF;
- fine-tuning on small label sets for pixel AUC;
- layout statistics (columns, class averages) on ink maps: the maps' clutter spectrum falls as f^−4, so at fixed per-pixel contrast a statistic over a letter, a line or a column has one to two orders of magnitude less d′ than one over a stroke (Burgess's size law, round 29).

A different energy or distance at 9 µm was not shown to help, but our test of it was weak.

## Limitations and corrections

Thirteen errors or weak points changed what we could claim or how we state it. Each was logged when found.

| what went wrong | effect | what we did |
| --- | --- | --- |
| The retention metric (α50) equals 0.5 for any linear detector in our blend | An early bound for 0268 was too strong | Withdrawn; bounds come from box tests and T1 AUC |
| The pre-registered mass statistic weighted about 2,500 letter fragments per winding equally | A spurious +10-14% excess | Recomputed with whole letters (−4.3%), marked post hoc; the bound widened to ≥ 15% |
| The first sheet-edge finder failed on multi-sheet profiles | No usable edges for sheet-locking | Replaced by a run-based tracker before any score |
| The planned letter boxes merged on 1447's sparse labels | The box test was unusable there | Redefined before our runs; one criterion was set after seeing published predictions and is flagged |
| The round-4 bench backgrounds lay next to the training windings | It favoured fine-tuned models | Added T1b with backgrounds at least five windings away |
| 0175B renders were too short, then off distinct sheets | No valid measurement | The scroll stays unmeasured |
| Our 0268 surfaces rarely sat on distinct sheets | The 0268 search and its readability rank were over-read in our first draft | Both demoted; the sheet check comes first |
| The sharpness match of round 21 used edge widths that partly reflect sheet geometry | Only one letter source was actually blurred | Reported as a weak test |
| The first window of the protocol test held no labelled pixel on one segment | No result for that segment in the first run | Rerun on the labelled half, logged before the rerun |
| The 113 keV scans were dated August 2025 from their volume ids | A wrong date in the first draft | Corrected to July 2025 |
| The campaign comparison used careful fits for one group and survey bands for the other | Part of the reported 0.05-0.08 gap came from our renders | Round 25 with matched renders; the claim is now qualified |
| Our first draft called gp13's index "the opposite" of ours from ρ −0.45 without an interval | Overstated | Now with permutation p and intervals: no evidence either way |
| The voxel-size test's resampled renders were shorter than the letter crops | The first run stopped | Crops cut to 720 rows and natives rerun in the same round, logged before any AUC |

**Limitations**
- **Few real ink sources:** 343 and 1447 at 116 keV, 0841 at 113 keV. 1447 gives 19 letter components, so intervals on AUC differences are ±0.03-0.08.
- **Injected ink only:** all readability results use injected ink; the blend cannot separate weaker ink from texture interference.
- **Visual candidates:** decisions on search maps are visual, and the rule was not calibrated by blind injection.
- **Small searched area:** the searches cover a small fraction of each roll.
- **Model limits:** the ideal-observer benchmark is linear (Hotelling up to 21 px); a non-linear ideal observer is not computable here, so headroom is bounded only from the linear side. The limit may move with better networks (it spreads 0.74-0.94 across public ones).
- **Unnormalised contrast:** α is relative to 1447's grey levels. It is not an attenuation or ink-load unit.
- **Analysis choices:** the crop window alone moves group gaps by about ±0.02 AUC, and the voxel grid by up to 0.06.
- **Letter-source texture:** the letter crops come from the official renderers (Nader's 1447 surfaces, the organisers' 0841 surface volumes), whose fine-scale spectra are steeper (β about 4.0-4.1 over 25-250 µm) than our renders of the eligible scrolls (2.5-3.7). An injected letter therefore carries a smoother fine texture into a rougher background; round 21 matched the sheet-edge width, not the spectrum. The verdicts compare backgrounds under the same letters, so this shifts absolute AUCs rather than comparisons.
- **Pipeline:** we did not use Lasagna flattening, and our surfaces differ from the organisers' segments. The sheet-check thresholds were tuned on our renders at about 9 µm.

## Sources and code

- **Data:** [Vesuvius Challenge open data](https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com) (CC BY-NC 4.0): CT volumes, segments and surface volumes, the PHerc. 0841 labels of 2026-09-18; the PHerc. 1447 dataset ink-8um-pherc1447-surfaces by Youssef Nader (CC BY-NC).
- **Models and inference:**
  - [ScrollPrize/villa](https://github.com/ScrollPrize/villa) for ink_9um, dnative and the inference command;
  - Domenico Russo's [Reader v2](https://github.com/DomRusso2/reader-v2) and [Reader V3](https://github.com/DomRusso2/reader-v3) ([checkpoint](https://huggingface.co/domenicor046/reader-v3));
  - Youssef Nader's ink-8um-v8in;
  - Giorgio Angelotti's Hecate.
- **Organisers:**
  - [prizes](https://scrollprize.org/prizes), [open problems](https://scrollprize.org/2026_open_problems), [past winners](https://scrollprize.org/winners);
  - the [first First Letters award](https://scrollprize.substack.com/p/50k-first-letters-prize-awarded-for);
  - [letters in Scroll 4 at 2.4 µm](https://scrollprize.substack.com/p/finallyletters-in-scroll-4).
- **Literature:**
  - Angelotti et al., [arXiv 2606.29085](https://arxiv.org/html/2606.29085), 2026, on the reading of PHerc. 1667 and its scan parameters;
  - Brun et al., Revealing metallic ink in Herculaneum papyri, PNAS 113 (2016) 3751-3754;
  - Tack et al., [Scientific Reports 6:20763](https://pmc.ncbi.nlm.nih.gov/articles/PMC4745103/), 2016, on lead in Herculaneum ink;
  - Seiler et al., [PLOS ONE](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0353485), 2026, on screening library scrolls for lead.
- **Prior work** is cited as read on 24 October 2026. gp13's per-scroll index comes from table 1.2 of its `report/sections/01_index.md`.
- **Code and log:**
  - The tools, configurations and result files are in this repository (MIT licence for the code).
  - The dated test log is `docs/PREREGISTRATION_LOG.md`.
  - The 1447 and 0841 labels, and masks derived from them, are not redistributed; `readability.crops` rebuilds the crops from the original datasets.
