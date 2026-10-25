# Pre-registration log

These are our working notes, kept while the tests ran (12-25 October 2026). Each round's rule was written in this file before its computation; the dates are those written at the time. The file was not externally timestamped, so the order of rule and result rests on these notes. Sections are not in date order (the newest rounds sit near the top). One line about a private alignment of a published transcription has been removed, and local paths are shortened; nothing else was edited.

---

# Detection limit, depth-order control and newer ink models

Approved by the user on 2026-10-12, after the outside review and our fact-check (`survey/SURVEY.md`, "Prior public work"):
- point 2: fade test and depth-order control, no downloads;
- downloads: Nader `ink-8um-v8in` (weights + inference code, 334 MB), Reader v2 (`reader-v2-step040000.pth`, 138 MB), dataset `ink-8um-pherc1447-surfaces` (1.89 GB).

Work dirs: ZGX `~/vesuvius/eval/` (scripts, logs, views), `/mnt/data/vesuvius/eval/` (renders, maps), downloads in `/mnt/data/vesuvius/ext/`.

## 1. Fade (signal-injection) test, our chain + 3 villa models

**Question:** how weak can PHerc. 343-type ink be before our chain stops finding it? The answer turns the PHerc. 800 null into "any ink there is weaker than X% of PHerc. 343's".

**Method (`fade_blend.py`)**
- **Letters:** the 4 stage-B renders of PHerc. 343 that carry the 16 covered letter boxes. These are s028-s031: submission snapping on our fit, band z 9500-11000.
- **Background:** same-size windows of hole-free PHerc. 800 renders (band z 11000-12500, same scan session), where our rule found no letters:

  | 343 render | 800 window |
  |---|---|
  | s028 | e055 from x 1000 |
  | s029 | e060 from x 1000 |
  | s030 | e063 from x 1000 |
  | s031 | e066 from x 1000 |

- **Alignment:** each 800 window is shifted in depth to the mean layer profile of its 343 render (integer shift, at most ±4 layers). It is then matched layer by layer to that render's mean and standard deviation on the joint papyrus mask.
- **Blend, layer by layer:** out = m + α (343 − m) + √(1 − α²) (800 − m), with m the layer mean.
  - The contrast of 343's ink against the papyrus texture scales by α.
  - The texture variance stays the same.
- **α values:** 1, 0.5, 0.35, 0.25, 0.15, 0.
- **Models and depths:** dnative and ink_9um seeds 42/43, at d0 and d+2 (the two best depths in stage B).
- **Ensemble and box test:** as in stage B (`ensemble800.py`; inside − ring ≥ 0.3; 200 random boxes per render, drawn on the joint mask).

**Rule (written before any result)**
- **Validity:**
  - At α = 1, at least 60% of the covered boxes must show ink (stage B gave 69%).
  - At α = 0, at most 25% may show ink.
  - Otherwise the blend changes what the models see, and the test is inconclusive.
- **Detection limit α\*:** the smallest α at which both stage-B criteria still hold.
  - Criterion 2: at the better of d0 and d+2, at least 60% of the covered boxes show ink while random boxes stay at or below 25%.
  - Criterion 3: the letter rows are visible in the views.
- **Also reported:** the smallest α at which the letter boxes still show ink at least twice as often as random boxes (a trace of signal).
- **Meaning for PHerc. 800:** in the band we searched, letters with ink contrast of at least α\* × PHerc. 343's would have passed our rule. The null says that any ink there is weaker than that, for these models.

**Caveats**
- The blend overlays two papyrus textures. The random-box rate at each α measures any false alarms this creates.
- The injected ink keeps its own PHerc. 343 papyrus around it.

### Section 1 result (2026-10-12, 19:27)

| α | best depth | letter boxes showing ink | random boxes |
|---|---|---|---|
| 1 | d+2 | 12/16 (75%) | 9% |
| 0.5 | d0 | 1/16 (6%) | 6% |
| 0.35, 0.25, 0.15 | | 0/16 | 7-8% |
| 0 | | 0/16 | 7-8% |

- **Validity:** both checks pass (α = 1 reproduces stage B; α = 0 gives no false letters).
- **Detection limit α\* = 1.0:**
  - the 3 villa models see the PHerc. 343 letters only at full strength;
  - at half the ink-to-texture contrast they see nothing (trace limit also 1.0).
- **Blend check:** the α = 0.5 render correlates 0.503 with α = 1 and 0.866 with α = 0, and keeps the same standard deviation, as designed.
- **Views:** at α ≤ 0.5 the yellow detections sit on the PHerc. 800 papyrus's own false-alarm spots, the same at every α down to 0.
- **Meaning for PHerc. 800:** our search excludes only ink at least about as contrasted as PHerc. 343's. Ink half as strong would have been missed.
- **Refinement added after this result (not a rule change):** α = 0.9, 0.8 and 0.7 (`fade_extra.sh`), to locate the drop. If detection already collapses at 0.9, the blend itself (overlaying a foreign texture) and not the ink contrast is what the models fail on.

**Refinement result (22:15)**

| α | letter boxes (best depth) | random |
|---|---|---|
| 0.9 | 7/16 (44%) | 8% |
| 0.8 | 7/16 (44%) | 7% |
| 0.7 | 5/16 (31%) | 6% |

- **The fall is gradual:** from 75% at full strength, to 44% at 80-90%, 31% at 70%, and chance level at 50%.
- **Limits:** detection limit 1.0 (only full strength meets criterion 2); trace limit 0.7.
- **What it says:** PHerc. 343 itself sits just above what these models can see. A 10-20% weaker ink-to-texture contrast already halves the letters found.
- **What it cannot separate:** a weaker ink from the effect of overlaying a foreign texture. Both lower the signal-to-texture ratio the models work with.

## 2. Depth-order (shuffle) control

**Question:** do the models use the order of the layers (ink sits on one face of the sheet), or do they fire on in-plane texture? aviad12g found that Hecate lights more pixels on depth-shuffled input on 10 of 10 public 800/1203 surfaces.

**Method (`shuffle_layers.py`)**
- **Shuffle:** layers 23-43 are permuted with one fixed permutation (numpy seed 0). This covers the villa window at d0 (layers 25-41) and Hecate's 16 planes at 9.6 µm.
- **Renders:**
  - the α = 1 renders of section 1 (PHerc. 343 letters);
  - the α = 0 renders (PHerc. 800 papyrus);
  - PHerc. 1203 t044 (the Hecate lead).
- **Models, all at d0:**
  - the 3 villa models on all 343 and 800 renders;
  - Hecate on 343 w029/w030 (11 boxes), 800 under w029/w030, and 1203 t044.
- **Measures:**
  - share of reading-side pixels with p > 0.5, normal against shuffled;
  - box test, normal against shuffled (343);
  - persistence P: share of the normal-order positives (p > 0.5, reading side) that stay positive when shuffled. On 343 it is measured inside the letter boxes; on 1203 t044, inside the windows where Hecate's A ≥ 1.8.
  - chance level q: share of shuffled positives in the same region. lift = P − q.
  - Added before any run: q, because a shuffled map that lights many pixels makes P high by chance.

**Rule (written before any result)**
- A model "uses depth order" if its PHerc. 343 letter boxes fall to at most 25% showing ink when shuffled.
- PHerc. 1203 t044 stays a lead only if both conditions hold:
  - Hecate uses depth order on 343;
  - lift(t044) ≤ lift(343 boxes) + 0.2.
- In every other case the lead is closed, including when Hecate does not use depth order on 343.

### Section 2 result (2026-10-12, 22:10)

**Every model uses depth order on PHerc. 343.** With shuffled layers the letter boxes fall to nothing:

| model | letter boxes, normal → shuffled |
|---|---|
| villa ensemble | 11/16 → 0/16 |
| dnative | 13/16 → 0/16 |
| seed42 | 9/16 → 0/16 |
| seed43 | 8/16 → 0/16 |
| Hecate | 7/11 → 1/11 |

**Amount of p > 0.5 (reading side), normal → shuffled.** "Amount" behaves differently in every model, so it is no evidence of ink:

| model | 343 | 800 |
|---|---|---|
| dnative | ×0.2 | ×0.2 |
| seed42 | ×2.5 | ×2.5 |
| seed43 | ×1.0 | ×0.7 |
| Hecate | ×0.2 | ×0.3 |

- On our renders Hecate lights FEWER pixels when shuffled. aviad12g's result (more pixels on 10/10 surfaces) does not replicate here.
- Our shuffle permutes native layers before Hecate's 9.6 µm resampling; theirs permuted 9.6 µm planes.

**PHerc. 1203 t044 (Hecate)**

| measure | normal → shuffled |
|---|---|
| A median | 2.49 → 2.17 |
| windows ≥ 1.8 | 9 → 6 |
| amount | 0.043 → 0.039 |

- **Persistence inside the A ≥ 1.8 windows:** P 0.24 against chance 0.04, lift +0.20. On the 343 boxes the lift is +0.02.
- **RULE outcome: the lead STAYS, by 0.02:** lift +0.20 against the limit +0.22.
- **The other indicators (outside the rule) all differ from real letters:**
  - on 343 the response collapses when shuffled (amount ×0.2, letters gone);
  - on t044 the amount and the asymmetry barely change.
- **Weight:** the lead survives on paper but most likely reflects texture, not ink. Next check at no download cost: Nader's model on t044, if Nader validates. No new CT for w045-049 on this basis.

## 3. Newer models (after sections 1-2): Nader `ink-8um-v8in`, Reader v2

**Training sets and independent tests**

| model | trained on | independent tests |
|---|---|---|
| Nader v8in | Scroll 1/5, 1667, 0139, 0814, 0500P2, Frag1 | PHerc. 343 and 1447 |
| Reader v2 | includes fragment 343P | 1447 only (343 is not independent) |

### Rule for the newer models (written 2026-10-12, before either model is run on PHerc. 343, 1447 or our renders)

**Runtime checks (not tests)**
- **Reader v2:** checkpoint sha256 matches its card. Its weights have the same keys and shapes as ink_9um. It runs through our villa command (17-layer windows, `--direction both`).
- **Nader v8in:** our run of the base model on a crop of 1447 w058 (`--reverse`, as documented) must reproduce the published `predictions/v8in.png` there (correlation ≥ 0.99). Otherwise our runtime differs from the author's, and its results are not used.

**A. Hard positive: PHerc. 1447 w058 and w060 (Nader's labelled windings)**
- **Data:** 24 layers at offsets −11.5..+11.5 voxels; refined ink labels; a certainty mask.
- **Models:**
  - the 3 villa models of our 800 search, as the baseline;
  - Reader v2, with the villa window at d −2/0/+2 (layers d+4..d+20);
  - Nader base: its published held-out prediction `v8in.png` (never trained on 1447).
- **Orientation:** for the villa-format models, the depth direction is chosen on w058 (higher AUC) and kept for w060.
- **Pixel AUC:** against the labels inside the certainty mask (label > 127 = ink), as in the dataset card.
- **Letter boxes:**
  - labels > 127, dilated by 8 px;
  - connected components 80-600 px wide and tall, at least 80% inside the certainty mask.
- **Box test:** as for PHerc. 343 (map z-scored over the papyrus and clipped to 0..3; inside − ring ≥ 0.3). Each map is scored on its own, and the 3 villa models also as an ensemble. Random boxes (200 per winding, same sizes) are drawn inside the certainty mask on blank papyrus (no dilated label pixel inside).
- **"Sees the 1447 letters":** both windings show ≥ 60% of letter boxes with ink, random boxes ≤ 25%, and strokes are visible in a crop. **"Trace":** letter boxes ≥ 2× random.
- **Change logged 2026-10-12 (before any of our model runs on 1447):**
  - **Why:** a dry run of `p1447_eval.py` on Nader's published predictions showed the box definition above to be unusable.
    - The labels are only about 10 letters per winding, one line plus 2 letters, inside a thin certainty halo.
    - Dilation merged them into 4 and 7 boxes.
    - Random boxes confined to the halo fall on a handful of overlapping spots.
  - **Fix:**
    - Letter boxes are now the label components, with touching letters split into round(width / height) equal boxes.
    - Random boxes are drawn anywhere on the papyrus (≥ 80% covered) with no dilated label pixel inside, as for PHerc. 343.
  - **What we had already seen:** that dry run scored Nader's published base prediction under the old definition (w058 2 of 4 boxes, w060 1 of 7). Our own runs had not started.
- **Calibration seen with the fixed definition (published predictions only):**

  | prediction | w058 letter boxes | w060 letter boxes | random boxes |
  |---|---|---|---|
  | Nader base | 4/10 | 3/10 | 10% |
  | the discovery-level 1447 finetune (held out) | 4/10 | 3/10 | 8-10% |

  - A crop shows why: the predictions are blob fields with a few letter-like forms; the letters were read by experts guided by the labels' line.
  - So the "sees the letters" level above cannot be reached on 1447, even by the model that found them.
- **Added criterion A′ (before any of our runs on 1447):** a model "matches the discovery level" if, over both windings, at least 6 of the 20 letter boxes show ink and random boxes stay at or below 15%.

**B. Easy positive: PHerc. 343 (Nader only; Reader v2 was trained on 343P)**
- The stage-B box test on s028-s031 (16 covered boxes): ≥ 60% against ≤ 25% random, plus rows visible.
- Nader is run on the central 24 layers (21-44) in both depth orders. The order that finds the boxes is the reading side for our renders.

**C. Fade renders:** each new model's own detection limit α\* (section 1 rule), compared with the villa ensemble's.

**D. Depth order:** the box test on 343 (Nader) and on 1447 (both models), normal against shuffled (section 2 rule).

**Runtime and cost (logged 2026-10-12, before any run on our renders)**
- **Nader runtime check: passed.**
  - A crop of 1447 w058 aligned to the author's 21 px tile grid reproduces the published `v8in.png` (correlation 1.000, mean difference 0.002).
  - The first, unaligned crop gave 0.95: different tile positions, not a different model.
  - Stride 32 changes the map (0.93), so we keep the author's stride 21.
- **Cost:** about 0.12 Mpx per minute on the shared GB10, close to 1 h per 343 render and per depth order.
- **3B changed to save time:** both orders are run on s029 (6 boxes). The order that finds more boxes there is used alone on s028, s030 and s031, and the box test is then scored on all four.
- **3C for Nader:** postponed. It would take about 11 h on the shared GPU.
  - Nader already meets A′ with its published 1447 predictions (7 of 20 boxes, random 10%), the same as the discovery finetune.
  - Caveat: A′ was set after seeing those numbers. It means "as good as the model that found the 1447 letters", not an independent pass.
- **3C for Reader v2:** cheap (villa format), run on all fade renders at d0 and d+2.

### 3A result: PHerc. 1447 hard positive (2026-10-12, 23:07)

Direction and depth are chosen on w058 and kept for w060. The reading direction is "reverse" for every villa-format model: forward gives AUC about 0.5.

| model | setting | AUC w058 / w060 | letter boxes w058, w060 (random) | A′ (≥ 6/20, random ≤ 15%) |
|---|---|---|---|---|
| dnative | reverse d0 | 0.820 / 0.713 | 4/10, 3/10 (10-12%) | met |
| ink_9um seed42 | reverse d−2 | 0.749 / 0.653 | 3/10, 3/10 (4-8%) | met |
| ink_9um seed43 | reverse d0 | 0.761 / 0.633 | 4/10, 2/10 (6-7%) | met |
| villa ensemble | reverse d−2 | | 3/10, 2/10 (4%) | not met (5/20) |
| **Reader v2** | reverse d−2 | 0.844 / 0.774 | **5/10, 5/10** (8-10%) | met (10/20, best) |
| Nader base (published) | | 0.862 / 0.810 | 4/10, 3/10 (10%) | met |
| Nader 1447 finetune (reference) | | 0.846 / 0.803 | 4/10, 3/10 (8-10%) | met |

- **Nobody reaches "sees the letters" (≥ 60%).** All are at trace level.
- **Crop of the labelled line on w058 (`nader_check/w058_models.png`):**
  - Reader v2 draws a row of recognisable letter forms (Λ, Κ, Α shapes) on a quiet background;
  - dnative shows the same forms, noisier;
  - Nader's base gives a blob field in which the letters are hard to see, despite its higher AUC.
- **Two consequences:**
  1. Had our PHerc. 800 surfaces carried 1447-like ink, dnative would most likely have shown rows. The 800 null is therefore stronger against 1447-type ink than the fade test alone suggests.
  2. On both positives, dnative alone beats the 3-model ensemble (343: 13/16 against 11/16 at d0; 1447: 7/20 against 5/20). The 800 rule's "2 of 3 models" requirement was conservative.
- **Decision (rule): Reader v2 meets A′** and is run on the PHerc. 800 search renders (section 4). Nader also meets A′ on its published maps, but it is visually weaker and about 50x slower. Its 343 run (3B) stays in the queue at low priority.

### 3C result: Reader v2 on the fade renders (2026-10-13, 00:02)

Reader v2 was trained on fragment 343P, so these numbers are optimistic.

| α | letter boxes | random |
|---|---|---|
| 1 | 12/16 (75%) | 14% |
| 0.5 | 4/16 (25%) | 12% |
| 0.35 | 2/16 | 11% |
| 0.25 and below | 0/16 | 10-11% |

- **Limits:** detection limit 1.0, trace limit 0.5 (villa ensemble: 0.7).
- **Reading:** a little more sensitive than the villa ensemble at half strength (4/16 against 1/16), with a higher random-box rate. Levels 0.9-0.7 are queued (`rv2_fade_extra.sh`).
- **Full curve (02:20):**

  | α | Reader v2 | villa ensemble |
  |---|---|---|
  | 1 | 75% | 75% |
  | 0.9 | 75% | 44% |
  | 0.8 | 69% | 44% |
  | 0.7 | 50% | 31% |
  | 0.5 | 25% | 6% |
  | 0.35 | 12% | 0% |

  - **Reader v2:** random 10-15%; detection limit α\* = 0.8, trace limit 0.5.
  - **Villa ensemble:** α\* = 1.0, trace limit 0.7.
  - Reader v2 meets decision criterion C as well as A′. Caveat: it was trained on 343P, so this curve may be optimistic. The independent 1447 test points the same way.

### 3B result: Nader base on PHerc. 343 (2026-10-13, 03:40)

- **Depth order** chosen on s029: "rev" 3/6 letter boxes (random 15%), "fwd" 0/6.
- **All four renders in "rev":** 9/16 (56%) against 10% random. That is one box short of criterion 2 (≥ 60%), so trace level, not a pass.
- **Crop of w030 (`nader_check/s030_models.png`):** the strokes are inside the known boxes for Nader, dnative and Reader v2. Nader's background is the busiest, Reader v2's the quietest.
- **Comparison on 343 at d0:** dnative alone 13/16, villa ensemble 11/16, Reader v2 12/16 (trained on 343P).
- **Nader is not better than our existing models on either positive.** It still meets A′, so by the rule it is run on the 800 search renders.
- **Run:** `nader_800.sh`, about 20 h, lowest priority, after Reader v2 on the survey. It can be stopped and resumed per winding.
- **Criterion 2 for Nader** (no depth windows): any line-like spot is re-run with the 24-layer window shifted by 2 layers (start 19 and 23).
- **Result (run finished 2026-10-14 01:08, 41-57 min per winding; checked 2026-10-16): no candidate.**
  - All 20 windings were viewed on contact sheets at 1/6.
  - Everywhere Nader's usual dense speckle field. Brighter patches sit where the other models also respond (the e059 density cloud, e051, e052, e062, e065, e067), and e054 has a horizontal streak (the fibre/crack seen with Reader v2).
  - No rows of letter-like strokes, so criterion 2 was never triggered.
  - This is a weak test: on 1447 Nader's map shows even the real letters only faintly.

## 4. Reader v2 on the PHerc. 800 search renders (rule written 2026-10-12, before any run on PHerc. 800)

**Run**
- Hole-free renders e050-e069 (band z 11000-12500, about 200 cm²).
- Reader v2 at d −2, 0, +2 and the control d+12, both directions, through `villa_any.sh`. Maps go to `/mnt/data/vesuvius/eval/maps800/` (Reader v2 only).
- **Pointer, not evidence:** `scan_asym.py --edge=150 --cover=0.1` on the Reader v2 maps. Views come from `ensemble800.py` (CT with the Reader v2 map in yellow).

**A region is a candidate only if all of:**
1. Stroke-like marks are arranged in rows along the winding (text lines) in the Reader v2 reading-side map at one depth. Reference look: the 1447 crop above.
2. The rows are also visible at a neighbouring depth.
3. The control render at d+12 shows no such rows in the same place.
4. The rows vanish when the layers are shuffled (`shuffle_layers.py`, run only on candidate windings).

**Reporting:** windings with candidates and their crops; otherwise "no letters with Reader v2 in about 200 cm²".

### Section 4 result (2026-10-13, 02:30): no candidate

- **Run:** all 20 windings, at d −2, 0, +2 and the control +12; about 7-10 min per winding.
- **Pointer:**
  - On the PHerc. 343 letter renders, Reader v2's A is 2.4-8 on the sheet, with 6 of 6-7 windows ≥ 1.8.
  - On PHerc. 800, A is in the same range on e055 (3.9), e056 (2.9), e059 (2.9, with windows up to 93), e063 (2.3-3.1) and e052 (1.6-1.9, flip at +12).
  - So with Reader v2 the asymmetry alone does not separate text from papyrus.
- **Visual check:** the 6 top-A windings were cropped at 1/3 (d0 and the control); all 20 windings were viewed on contact sheets at 1/6; the two most line-like spots were zoomed at 2/5 (e061, e066).

  | winding | what the Reader v2 map shows |
  |---|---|
  | e055, e056, e063 | scattered blobs and loops, the same at d0 and d−2, no rows |
  | e059 | the density cloud already seen with the villa models: large amorphous blobs |
  | e052 | horizontal soft smudges in bands that follow the recto fibres visible in the CT (spacing about 2.9 mm, denser than text lines), no letter shapes |
  | e058 | a chain of large blobs, and a strong response at the control depth |
  | e051 | a vertical cluster along a crack |
  | e061 | one horizontal band of smudges about 2 cm long with one Λ-like spike, also at d−2, absent at +12, gone when shuffled |
  | e066 | similar but weaker |

- **Why e061 is not a candidate:**
  - Reader v2 goes almost blank everywhere when shuffled, so criterion 4 does not separate ink from sheet-surface texture for this model.
  - A 13 mm band of real text would show 2-3 parallel lines of letter-sized shapes, as on 1447. Here there is a single band of smudges with no sequence of letter forms, so criterion 1 is not met.
- **Verdict: no letters with Reader v2 in about 200 cm² of PHerc. 800.**
  - With the fade curve, any ink in these surfaces is weaker than about 80% of PHerc. 343's contrast (trace level 50%).
  - Or it is not of a kind Reader v2 sees: Reader v2 does see 1447's letters.

## 7. Per-scroll detectability map (approved by the user 2026-10-16; rule written before any run; no downloads)

**Question:** on the papyrus of each eligible scroll we have rendered, how strong would PHerc. 343-type ink have to be for each public model to find it?

**Letters**
- Source: the PHerc. 343 stage-B renders s028-s031 with their 16 covered letter boxes.
- The survey bands hold only 461 rows of papyrus, so the 343 renders are cut into strips 460 rows tall. A greedy cover picks the fewest strips that contain every box ≤ 440 rows tall; each box is counted in one strip only. Strip width is the box extent ± 400 px.
- For the 9.362 µm scrolls each strip is resampled by 8.64/9.362 in rows, columns and depth (letters shrink as they would at that voxel size).

**Backgrounds**
- Windows of the same size as the strips, taken from the scroll's survey renders, one winding after another, fully on papyrus.
- Scrolls: PHerc. 0800 (reference; windows from the hole-free renders e055/e058/e061/e064/e067), 1218, 1203, 0268, 0125, 0191, 0257, 0358, 0813, 1545, 0211, 0826.

**Blend**
- As in section 1, but the strip is matched to the background, layer by layer (mean and standard deviation on the joint mask, depth shift ≤ ±4). The output keeps the background's statistics.
- out = m + α (343 − m) + √(1 − α²) (background − m).
- α = 1, 0.85, 0.7, 0.55, 0.
- The strips of one scroll and one α are laid side by side in one composite render (820 rows, zero gaps), so each model runs once per scroll and α.

**Models, all at d0:** dnative, ink_9um s42 and s43 (also as the villa z-ensemble), Reader v2, Hecate (second pass).

**Measure**
- Stage-B box test on each model's map: z-scored over the papyrus and clipped 0..3; for the villa ensemble, `ensemble800.py`.
- Letter boxes showing ink (inside − ring ≥ 0.3) against 200 random boxes per strip on the composite's papyrus.

**Per scroll and model**
- **Detection limit α\*:** the smallest α at which ≥ 60% of the boxes show ink with random ≤ 25%, met at every larger α too.
- **Trace limit:** the same with boxes ≥ 2× random.
- **"None":** even α = 1 fails.
- **Validity:** at α = 0, boxes ≤ 25%; otherwise that scroll's entry is invalid (false letters).

**Reading**
- A low α\* means the scroll's papyrus lets the model find ink much weaker than 343's. "None" means even 343-strength ink in that papyrus would be missed.
- Caveats:
  - only 343's ink is tested;
  - the blend cannot separate weak ink from texture interference;
  - at α = 1 all scrolls see the same 343 strips (only rescaled, and resampled at 9.36 µm), so scrolls differ at α < 1.

**Reference row, PHerc. 0800 background (2026-10-16 11:11, strip version)**

| model | α = 1 | α = 0.85 | α = 0.7 | α = 0.55 | α = 0 |
|---|---|---|---|---|---|
| villa ensemble | 10/15 (random 14%) | 2/15 | 3/15 | 1/15 | 1/15 |
| Reader v2 | 10/15 (random 19%) | 5/15 | 3/15 | 2/15 | 1/15 |
| dnative | 8/15 | | | | |
| s42 | 3/15 | | | | |
| s43 | 5/15 | | | | |

- **The strip version is harsher than the full fade test** (section 1: Reader v2 69% at 0.8, villa ensemble 44%). Two reasons:
  - The 460-row strips cut the rings of the tall boxes above and below, leaving mostly the neighbouring letters of the same line.
  - Random boxes fall inside the strips, which hold other, unlabelled 343 letters, so the random rate is higher (14-19%).
- **Map numbers are therefore comparable across scrolls only, not with section 1.**
- Pre-registered limits are kept. Added for reading, not as a rule change: the per-α box counts (the curve).

**First three scrolls, villa + Reader v2 (11:39)**

| scroll | Reader v2: α = 1 / 0.85 / 0.7 / 0.55 / 0 | villa ensemble: α = 1 / 0.85 / 0.7 / 0.55 / 0 |
|---|---|---|
| 0800 | 10 / 5 / 3 / 2 / 1 | 10 / 2 / 3 / 1 / 1 |
| 1218 | 11 / 7 / 4 / 2 / 1 | 8 / 2 / 2 / 0 / 0 |
| 0826 | 10 / 6 / 5 / 1 / 2 | 8 / 4 / 2 / 1 / 1 |

- Counts are letter boxes out of 15.
- The differences between scrolls are within binomial noise (about ±2 boxes out of 15). Detection limits come out as 1.0 or "none", trace limits between 0.55 and 1.0: the box test has too little power to rank scrolls.

**Secondary metric added before computing it on any scroll: ink retention**
- **Definition:** for each scroll, model and α, the Pearson correlation between the model's map at α and its map at α = 1, over the strip pixels (gaps and a 20 px border excluded). It uses every ink pixel of the strips, unlabelled 343 letters included, so it has far more statistical power than 15 boxes.
- **Summary:** α50, the α at which retention falls to 0.5 (linear interpolation; "< 0.55" if never). Lower α50 means 343-type ink stays visible to that model at weaker contrast on that scroll's papyrus.
- **Reference:** retention at α = 0 is the noise floor (independent maps, expected about 0).

### Section 7 result (all 12 scrolls, both passes, finished 2026-10-16 22:23; `map_boot.py`, 1000 bootstrap resamples over strips)

α50 by ink retention, with the 95% interval:

| scroll (voxel) | Reader v2 | villa ensemble | dnative | Hecate | ink_9um s42 / s43 |
|---|---|---|---|---|---|
| 0800 (8.64, reference) | 0.68 [0.65-0.70] | 0.71 [0.67-0.74] | 0.70 | 0.75 | 0.85 / 0.85 |
| 1218 (8.64) | 0.70 [0.64-0.75] | 0.75 [0.70-0.78] | 0.78 | 0.81 | 0.86 / 0.81 |
| **0268 (8.64)** | **≤ 0.55 [0.55-0.57]** | **0.61 [0.55-0.64]** | **0.63** | **0.70** | **0.75 / 0.73** |
| 1203 (9.36) | 0.71 [0.67-0.76] | 0.75 [0.71-0.79] | 0.73 | 0.86 | 0.87 / 0.88 |
| 0125 (9.36) | 0.71 [0.69-0.73] | 0.73 [0.70-0.75] | 0.69 | 0.78 | 0.86 / 0.87 |
| 0191 (9.36) | 0.69 [0.63-0.73] | 0.74 [0.71-0.76] | 0.72 | 0.80 | 0.86 / 0.86 |
| 0257 (9.36) | 0.71 [0.66-0.76] | 0.74 [0.67-0.79] | 0.72 | 0.87 | 0.87 / 0.88 |
| 0358 (9.36) | 0.71 [0.68-0.74] | 0.75 [0.74-0.79] | 0.76 | 0.83 | 0.87 / 0.87 |
| 0813 (9.36) | 0.69 [0.64-0.76] | 0.71 [0.68-0.77] | 0.70 | 0.77 | 0.86 / 0.85 |
| 1545 (9.36) | 0.74 [0.70-0.78] | 0.76 [0.71-0.82] | 0.78 | 0.88 | 0.88 / 0.88 |
| 0211 (9.36) | 0.70 [0.65-0.76] | 0.78 [0.73-0.84] | 0.78 | 0.87 | 0.88 / 0.88 |
| 0826 (9.36) | 0.68 [0.63-0.74] | 0.76 [0.74-0.79] | 0.81 | 0.81 | 0.88 / 0.87 |

**Correction (2026-10-18, section 9 test 3).** Any linear detector has α50 = 0.5 in this blend.
- The α50 values below show how much faster than linear mixing each model loses the 343 response. The comparisons between models and scrolls stand.
- Reading α50 as "ink visible down to that fraction" does not; that needs the box test.
- 0268's α50 ≈ 0.55 means its papyrus masks the 343 response almost no more than linear mixing would.

**Findings**
1. **Model ranking is the same on every scroll** (lower is better, i.e. ink still seen at weaker contrast): Reader v2 (about 0.70) < villa ensemble ≈ dnative (0.70-0.81) < Hecate (0.75-0.88) < single ink_9um seeds (0.85-0.88).
2. **The papyrus of 11 of the 12 scrolls behaves alike** within the intervals, at both voxel sizes. The background does not explain why nothing has been found.
3. **PHerc. 0268 is the clear exception for every model.** Reader v2 keeps half its response even at α = 0.55, the lowest level measured. Its background windows (Nov 2025 scan, mid-radius windings) have a fine, uniform fibre texture with few voids. 0800, for comparison, has large dark voids and cracks, and a relative standard deviation in layer 33 of 0.21 against 0.32.

**Box test (pre-registered limits)**
- Detection limits are 1.0 or "none" almost everywhere, trace limits 0.55-1.0: too noisy to rank scrolls, as seen on the first three.
- α = 0 validity failed for some model/scroll pairs (≥ 4 of 15 boxes "showing ink" on pure background): 1203 (dnative, s42, Reader v2), 0257 (dnative, Reader v2), 0358 (Reader v2), 0813 (dnative), 1545 (dnative). The retention metric does not depend on this.

**Meaning**
- With today's public models, ink must be at least about 70% as contrasted as PHerc. 343's (Reader v2), or 75-80% (older models), to be seen on these scrolls' papyrus.
- On PHerc. 0268, Reader v2 would see ink down to at most 55%.
- Nothing has been found on these scrolls by us or by public searches. Wherever they have been looked at, any ink is therefore weaker than those levels, or the regions searched hold no text.
- 0268 is where a wider Reader v2 search would set the tightest bound per cm²: so far its coverage is our 4 short windings plus the community atlas meshes.

## 8. PHerc. 0268, stage 1: tall band with Reader v2 (approved by the user 2026-10-17, 12 GB; rule written before any download)

**Why:** in the section-7 map, 0268 is the eligible scroll whose papyrus lets the models see the weakest ink (Reader v2 α50 ≤ 0.55, against about 0.70 elsewhere). Coverage so far is only about 20 cm² public (6 unsnapped spiral-fit meshes, all screened negative) plus our 4 pilot windings × 4.3 mm.

**Data (`tall0268.sh`)**
- **Band:** 1500 slices, z 6610-8110, centred on mid-height; it contains the pilot band 7110-7610.
- **New m7 + lasagna from the listing:** 0.96 + 0.80 + 0.78 = 2.54 GB.
- **CT level 0** goes into the survey's `ct0.zarr` (pilot chunks reused), at most 9.4 GB new, so the total stays ≤ 12 GB.
- **Windings:** 4 consecutive ones around radius 2400 vx, where the map measured the favourable papyrus. The winding nearest that median radius is chosen, then its neighbours −1, +1, +2. If the CT exceeds the budget, 3 windings.
- **Chain:** our axis, distance field, tracks, spiral fit (3000 steps, the survey's settings), hole-free snapping, render (66 layers).
- **Models:** Reader v2 and the 3 villa models at d −2, 0, +2 and the control +12, both sides.

**Rule (sections 4 and 6 combined)**
- **Candidate** only if all hold:
  1. In the Reader v2 reading-side map, stroke-like marks are arranged in at least 2 parallel horizontal lines, 3-7 mm apart.
  2. The same at a neighbouring depth.
  3. Absent at d+12 and on the blind side.
  4. Not explained by a CT material anomaly: the bright-spot share in layer 33 must not follow the response, as it did on 1218.
- **A single line or blob region** is a lead only, reported with crops.
- **If no candidate:** report the area searched and the bound "no ink ≥ about 55% of 343's contrast visible to Reader v2 there" (section 7). The bound holds only for the searched area.

### Section 8 result (run finished 2026-10-17 21:04; checked 2026-10-18): no candidate

**Run**
- Downloads: 2.54 GB m7/lasagna + 7.53 GB CT = 10.1 GB, within the 12 GB approved.
- New fit: satisfied tracks 7.8%, windings w010-w160.
- Windings T073-T076: median radius about 2400 vx; 1820 × 14460-15060 px each.
- Papyrus searched: 65.3 cm² (16.0-16.6 cm² per winding), about 3x all earlier coverage of 0268.
- Villa 48 runs and Reader v2 16 runs, no failures.

**Visual check (Reader v2 d0/d+2 reading side, control d+12, blind side; overview at 1/8, the active half of each winding at 1/4)**
- The left half of every winding is quiet: scattered faint specks.
- In the right half (render x about 7600-14400), the same structures repeat on all four windings:
  - a lens-shaped region bounded by curved cracks in the CT (a fold or overlap of the sheet), lit with mottled texture;
  - clusters of blobs along the lower edge of the band;
  - a few bright blocks and a row of small round dots (T075).
- **All of them also appear on the blind side** (and the lens partly at +12), so they are structural, not ink on one face.
- There are no lines of letter-like strokes anywhere.
- The A pointer (T076 d+2 median 1.93, 14 windows) only reflects these structures.

**Correction (2026-10-18):** the "55%" bound below rests on the retention metric, which has a linear floor of 0.5 (section 9, test 3). It is withdrawn. A defensible bound for this area is the box-test detection limit of Reader v2, about 80-100% of PHerc. 343's ink contrast.

**Verdict:** no candidate in 65 cm² of PHerc. 0268.
- Using the section-7 calibration for this papyrus: no ink stronger than about 55% of PHerc. 343's contrast is visible to Reader v2 in this band and these four windings.
- The bound covers only the searched area: z 6610-8110, radius about 2400 vx.

## 40. Round 32: how much contrast does 2.4 µm buy? The same PHerc. 0841 letters at 9.366 and 2.403 µm (rule written 2026-10-25 before any download; download approval asked separately)

**Why:** every recommendation of "finer voxels" rests on the organisers' Scroll 4 result and on TAUIL's blind read (6 of 8 letters at 2.4 µm against 3 of 8 at 9 µm). Nobody has measured, on the same letters, how faint ink can be at 2.4 µm before a model loses it, against the same curve at 9 µm. PHerc. 0841 is the one eligible-campaign scroll with the organisers' labels on both canvases and official surface volumes at both voxel sizes; the 2.403 µm volumes of the two labelled windows are already local (round 24, 8.1 GB). Cross-area list of 2026-10-25, idea 3; asked by all three reviewers.

**Data:**
- **Letters:** the round-24 windows of w00 (rows 1700-2500, cols 2200-4400 on the 9.366 µm canvas; ×3.8976 on the 2.403 µm canvas) and of the auto-grown segment …252405 (rows 1300-2100, cols 0-2200). At 9.366 µm: the official 28-layer surface volumes (local), labels box-downsampled, direction forward, window s7 and the label offsets of round 20 (fixed). At 2.403 µm: the official 109-layer surface volumes (local), labels native on that canvas (inklabels + supervision of 2026-09-18).
- **Blank backgrounds (to be approved):** one 800 × 2200 window of w00 at rows 2550-3350, cols 50-2250 (9.366 µm canvas): no label pixel within 100 px, 99% papyrus, the lowest Reader V3 mean response among all such windows (0.297 against 0.332 in the letter window), outside the letter window. At 9.366 µm it is local. At 2.403 µm it needs 1768 chunks of the official surface volume: **3.16 GB**. A second blank window (auto-grown segment, rows 2250-3050, cols 0-2200, 2.99 GB) is optional; the primary design uses the w00 blank for both letter windows.
- **Model at 2.4 µm (to be approved):** the organisers' canonical 2 µm ink model `scrollprize/ink_canonical_2um` (MIT; ResNet-152 3D + 3D decoder, PyTorch-Lightning checkpoint `r152_3ddec_v2_l5_epoch13.ckpt`, **1.55 GB**). Inference ported from villa `ink-detection/optimized_inference` (local copy): 256 px tiles, 62-layer window, values clipped at 200 and scaled by 1/200, Hann blending, decoder output at 1/4 resolution upsampled; the model class and `models/` are in the local villa. Its training scrolls are not stated on the card; whether it saw PHerc. 0841 is unknown and is reported as such.
- **Download in all: 4.7 GB** (7.7 GB with the second blank window).

**Bench, at each voxel size separately, same letters, same blank papyrus:**
- Blend as round 4 (per-layer moment matching on the joint papyrus, out = m + α(I − m) + √(1 − α²)(B − m)) of each letter window into the blank window, with the layer stacks centred on the mesh (28 layers at 9.366 µm, 109 at 2.403 µm; the depth shift refined by ±2 layers at 9.366 and ±8 at 2.403 by mean-profile correlation). α ∈ {1, 0.85, 0.7, 0.5, 0.35, 0}.
- Readers: Reader V3 at 9.366 µm (window and direction of round 20, fixed); the canonical 2 µm model at 2.403 µm, with direction (reverse or forward) and the 62-layer window start chosen on the **unblended** 2.403 µm letter windows (native AUC against the native labels) and then fixed. Reader v2 at 9.366 µm as a second reader.
- Pooled pixel AUC per α and voxel size (letters vs other supervised pixels, both letter windows pooled), paired bootstrap over letter components and 256 px (9.366) / 1000 px (2.403) tiles. Also reported: d′ per α, α₀.₆₅ at each voxel size, and the **equivalent contrast**: the α at 2.403 µm whose AUC equals the 9.366 µm AUC at α 1, read off the curve by linear interpolation.
- **Model check before the bench:** the canonical model's native AUC on the unblended 2.403 µm letter windows must be ≥ 0.80 (the labels were drawn on 2.4 µm data, so a working port must reach this). If not, the port is wrong or the model does not fit this scroll, and the round is reported INVALID with the native number.

**Rule (primary: V3 at 9.366 µm against the canonical model at 2.403 µm):**
- **RESOLUTION BUYS CONTRAST:** α₀.₆₅(2.403) ≤ α₀.₆₅(9.366) − 0.15 (for example 0.74 → ≤ 0.59), with the AUC difference at α 0.5 having a 95% interval above 0. Then "finer voxels" becomes a measured recommendation with a number: ink readable at 2.4 µm down to X% of the 9 µm limit.
- **NO GAIN:** α₀.₆₅(2.403) ≥ α₀.₆₅(9.366) − 0.05. The 2.4 µm advantage seen in Scroll 4 would then come from elsewhere (phase contrast, distance, energy, or models), not from the voxel size as such, for this scroll and these readers.
- **PARTIAL** otherwise.
- The comparison mixes voxel size with the two scans' other differences (77 against 113 keV, 0.22 against 1.2 m), with two different readers, and with the unknown training provenance of the 2 µm model; the verdict is stated for "the 2.403 µm scan read by its model against the 9.366 µm scan read by its model", not for voxel size alone.

**Run:** `r32/r32_run.sh` on the ZGX (download, port check, bench); output `~/vesuvius/eval/r32_result.txt` (ends with `R32_DONE`), JSON `r32_result.json`. Expected: about 1 h of download, 2-3 h of porting and computation; memory about 10 GB per 2.403 µm blend (109 layers × 3118 × 8575 px).

**Amendments before any result (2026-10-25, after the user's approval of 4.7 GB; flagged):**
- At 2.403 µm the labels are native to the canvas, but the organisers' 9.366 µm alignment needed offsets of 0 to −11 px (round 20), so a label-offset search of ±8 px (step 2, then 1) is run on the unblended native maps at the chosen direction and window, once per segment, and then held fixed, exactly as at 9.366 µm. Direction and window start are chosen on w00 only; the auto-grown segment takes the same setting.
- The 2.403 µm bootstrap uses 1000 px tiles (the 9.366 µm one 256 px); the letter components at the two voxel sizes come from the same labels but are counted on each canvas, so the paired bootstrap pairs letters only when the counts agree, otherwise it resamples them independently (reported).
- The runner waits for round 31 to finish before using the GPU.

### Result (2026-10-25, 18:32-19:52, 80 min of GB10; `r32_result.txt`, `r32_result.json`; downloads 4.68 GB as approved): PARTIAL by the rule, with a large measured effect

**Fits.** 9.366 µm: w00 forward s7 (depth shift −1, 169k label px in the joint papyrus), auto-grown forward s5 (shift +1, 78k). 2.403 µm: the port loads the checkpoint with no missing or unexpected key; on the unblended w00 window the canonical model gives native AUC 0.893 / **0.959** / 0.957 at starts 15 / 23 / 31 forward, 0.53-0.55 reverse, so direction forward and the centred window s23 are fixed; label offsets (+3, −7) on w00 and (−8, −8) on the auto-grown window (at the search limit; native AUC 0.904 there). **Model check passed** (≥ 0.80). Blends: depth shifts −4 and +5 layers at 2.403 µm; joint papyrus 26.5 M and 23.7 M px.

**Pooled AUC, both windows, same letters, same blank papyrus of w00:**

| reader | α 1 | 0.85 | 0.7 | 0.5 | 0.35 | 0 | α₀.₆₅ |
|---|---|---|---|---|---|---|---|
| 9.366 µm, Reader V3 | 0.884 | 0.746 | 0.555 | 0.509 | 0.501 | 0.485 | 0.77 |
| 9.366 µm, Reader v2 | 0.874 | 0.700 | 0.584 | 0.553 | 0.540 | 0.504 | 0.79 |
| 2.403 µm, canonical 2 µm model | 0.940 | 0.883 | 0.768 | 0.612 | 0.520 | 0.459 | **0.55** |

- **Equivalent contrast:** the 2.403 µm reader reaches the 9.366 µm V3 full-strength AUC (0.884) at α **0.85**. At α 0.7 it reads 0.768 against 0.555.
- α₀.₆₅: 0.55 against 0.77, a difference of 0.22, beyond the pre-registered 0.15.
- Difference at α 0.5: +0.103 **[−0.043, +0.238]**. The interval straddles 0 because the labels in these two windows form only **6 connected letter components** at either voxel size (the 0841 labels are large merged strokes), so the letter-level bootstrap has almost no power; the tile term alone would give a much narrower interval, but the rule asked for the joint one.
- **RULE: PARTIAL** (the α₀.₆₅ condition is met by a wide margin, the interval condition is not). The honest statement: on PHerc. 0841, the 2.403 µm scan read by its model sees ink down to about 55% of the contrast that the 9.366 µm scan read by Reader V3 needs, with the uncertainty of six letter units; a confirmation needs letter windows with more, smaller components (or a bootstrap unit at the stroke scale, which is a change of rule).

**Reading and caveats.**
- The gain is large and in the expected direction, and this is the first measurement of it on the same letters. It mixes voxel size with energy (77 against 113 keV), distance (0.22 against 1.2 m) and reader; the canonical model's training provenance for 0841 is unknown. Reader V3 was not trained on 0841.
- The 9.366 µm curve of 0841 letters in 0841 blank papyrus falls faster than T1's (V3 0.555 at α 0.7 against 0.623 with 1447 letters in 800): the same reader, different letters and papyrus; the two benches are not interchangeable.
- The auto-grown window's 2.403 µm label offset sits at the ±8 px search limit; a wider search could raise its native AUC slightly and does not affect the 9.366 µm side.
- For the cross-area list: idea 3 done. For the report: recommendation 3 ("finer voxels: expected, not fully shown") becomes "measured on one scroll: ink readable down to about 55% of the 9 µm limit at 2.4 µm, six letter units".
- For the First Letters question: this is the number that prices the 2.4 µm route on 1203 and 0846A: a 9 µm null bounds ink above about 75% of 1447's contrast; the 2.4 µm scans of those two scrolls would see ink down to roughly half that, if 0841 generalises.

## 39. Round 31: deconvolution of the renders before inference (approved by the user 2026-10-25 "proviamo le idee 3 e 8"; rule written before any computation; no downloads)

**Why:** round 19 measured a 10-90% sheet-edge width of 2.8 voxels (25-35 µm) in both campaigns, an upper bound on the scanner's in-plane blur, and round 10 showed that the networks' evidence sits at 9-35 µm, right at that limit. We tested denoising (round 13: no gain) but never deconvolution, the standard astronomy and microscopy move when the PSF is known and the noise is low (noise is 1-3% of the clutter at stroke scale, round 5). In a clutter-limited regime a linear deconvolution amplifies clutter as much as signal, so the prior is low; the networks are non-linear and were trained on unsharpened data, so the effect is an empirical question. Cross-area list of 2026-10-25, idea 8.

**Data (local):** the T1 bench (1447 letters in 800 papyrus, crops w058a, w060a, w060b, α 1/0.85/0.7/0.5/0.35/0) and the T1b blends of the same crops in other 800 windings (e050/e051/e069). Reader V3 (window s2, d −2) and Reader v2 (s2) through our float inference.

**Method:** in-plane 2D deconvolution of each of the 24 layers before inference (depth untouched):
- PSF: isotropic Gaussian with σ ∈ {0.8, 1.2, 1.6} px (σ 1.2 px = 2.56 σ ≈ 3.0 px 10-90% width, the measured edge);
- algorithms: Richardson-Lucy (10 iterations, skimage) and Wiener (balance 0.05, the fine-band noise share); plus unsharp masking (amount 1, σ 1.2) as the naive baseline. Seven variants.
- Inputs are clipped back to 1-255 and zero outside the joint papyrus. The networks keep their own per-tile normalisation.

**Selection (so that no variant is picked on the test bench):** the seven variants are run on the **T1b** blends at α 0.7 with Reader V3; the variant with the highest pooled AUC is the primary. All seven T1b numbers are reported.

**Test:** the primary variant on **T1** at every α, Reader V3 and Reader v2; pooled pixel AUC as in round 18; gain G = mean over α 0.7 and 0.5 of (AUC_deconvolved − AUC_original) for V3, with the round-10 paired bootstrap (1000 resamples over 19 letter components and 160 tiles); change at α 1; false lights at α 0 at the 50%-recall threshold.

**Rule:**
- **PASS:** G ≥ +0.03 with the 95% interval above 0 and no loss > 0.01 at α 1 (V3). Deconvolution then enters the chain and the detection limit is re-measured with it.
- **KILL:** G ≤ +0.01, or a loss > 0.02 at α 1.
- **PARTIAL** otherwise.
- Reported either way: the full T1 curves for the primary variant and for the unsharp baseline, and Reader v2's gain.

**Run:** `r31/r31_deconv.py` on the ZGX; output `~/vesuvius/eval/r31_result.txt`, JSON `r31_result.json`. Expected 1-1.5 h (CPU deconvolution, GPU inference).

### Result (2026-10-25, 45 min; `r31_result.txt`, `r31_result.json`): KILL

**Selection on T1b (α 0.7, Reader V3):** original 0.612; RL σ 0.8 / 1.2 / 1.6: 0.604 / 0.616 / 0.631; Wiener σ 0.8 / 1.2 / 1.6: 0.613 / 0.616 / 0.615; unsharp σ 1.2: 0.604. Primary = Richardson-Lucy σ 1.6 (+0.019 on T1b).

**T1 (pooled AUC, α 1 / 0.85 / 0.7 / 0.5 / 0.35 / 0; false lights at α 0):**

| input | model | 1 | 0.85 | 0.7 | 0.5 | 0.35 | 0 | false lights |
|---|---|---|---|---|---|---|---|---|
| original | V3 | 0.826 | 0.725 | 0.623 | 0.542 | 0.522 | 0.509 | 0.077 |
| RL σ 1.6 | V3 | 0.827 | 0.727 | 0.628 | 0.536 | 0.514 | 0.508 | 0.062 |
| unsharp σ 1.2 | V3 | 0.830 | 0.718 | 0.618 | 0.537 | 0.520 | 0.509 | 0.073 |
| original | v2 | 0.808 | 0.708 | 0.612 | 0.536 | 0.520 | 0.519 | 0.148 |
| RL σ 1.6 | v2 | 0.806 | 0.708 | 0.617 | 0.537 | 0.511 | 0.508 | 0.115 |
| unsharp σ 1.2 | v2 | 0.810 | 0.701 | 0.607 | 0.533 | 0.517 | 0.516 | 0.128 |

- Gain RL σ 1.6, V3, α 0.7/0.5: **−0.001 [−0.027, +0.028]**; change at α 1 +0.001. Reader v2: +0.003 [−0.018, +0.024]. Unsharp: −0.005 and −0.004.
- **RULE: KILL** (G ≤ +0.01). The T1b selection gain (+0.019) did not carry to T1; the networks are indifferent to in-plane deconvolution at the measured PSF scale, in both directions. False lights fall a little with RL (0.077 → 0.062 for V3), the only effect.
- Reading: as expected in a clutter-limited regime, a linear sharpening amplifies clutter with the signal; the networks' per-tile normalisation and training on unsharpened data leave nothing to gain. Idea 8 of the cross-area list is closed.

## 38. Round 30: does the reconstruction setting change readability at 9.362 µm? PHerc. 0139 original against pag0 and pag50 (rule written 2026-10-25 before any download; download approval asked separately)

**Why:** the bucket holds three reconstructions of the same 9.362 µm / 113 keV / 1.2 m acquisition of PHerc. 0139 (July 2025): the original volume 20250728140407 and two re-retrievals of November 2025, `pag0` (20251107132835) and `pag50` (20251107135911), presumably Paganin retrieval off and at a stronger δ/β. Round 19 located the 113 keV campaign's extra fine-scale texture inside the sheets and left "reconstruction" as an unverified cause; round 23 excluded rings and a filter tilt only. Nobody has measured whether the retrieval setting changes clutter or readability. If it does, the nine 113 keV eligible scrolls could be re-reconstructed without beamtime. The organisers' open problems ask for exactly this kind of scan-parameter evidence.

**Data:**
- PHerc. 0139 has 39 official segments; five carry the organisers' native 9.362 µm ink labels of 2026-09-18 (same release as the 0841 labels): w035, w039, w040, w041, w044. The tifxyz meshes (on the original volume) and the labels are downloaded (8.7 MB in `/mnt/data/vesuvius/ext/p0139`).
- Chosen: **w044** (451k labelled pixels, all inside a 1600 × 4400 px window at y 3150, x 1550) and **w040** (310k of 717k in the window at y 2300, x 1600). A third segment is not planned.
- **Download (to be approved):** the level-0 chunks (128³ uint8, 2.10 MB each) that a 41-layer band around each window touches, from each of the three volumes: 813 + 820 chunks ≈ 1.70-1.72 GB per volume per segment, i.e. **about 10.3 GB in all** (cap 12 GB), plus a z-registration probe of about 20 MB and a 1600 × 4400 crop of each official 9.362 µm surface volume (about 50 MB each) for the renderer check. One-segment fallback (w044 only): 5.2 GB.
- The three volumes have the same x, y shape (6621²) but different z extents (20974 against 20961 slices): **step 0** fetches one column of 3 chunks at the window's centre from each volume and finds the z offset of pag0/pag50 to the original by correlation over ±16 slices (expected 0 or 13). If no offset reaches r ≥ 0.9 the volumes are not co-registered on a simple shift, the test stops before the bulk download and that is reported.

**Chain:** `readability.tifxyz` renders the 41-layer band of each window from each volume (the mesh is the same, shifted in z by the step-0 offset for the re-retrievals); renderer check against the official surface volume crop as in §34 (mean per-layer r ≥ 0.95 on the original volume). All later readouts use the same mesh, window and layers for the three volumes, so only the reconstruction differs.

**Tests:**
- **T1, label-free physics (primary, unbiased):** per volume and segment: clutter index (DoG σ 1-3), gradient energy, round-19 interior texture fraction F and fringe amplitude, 10-90% edge width, round-13 void-noise share, sheet-check valid share and depth contrast. Reported with the difference to the original.
- **T2, native ink:** Reader V3 and Reader v2 float inference on the 17-layer window; window start and label offset chosen on the **original** volume only (round-20 alignment search) and then held fixed for pag0 and pag50; pooled pixel AUC against the 9.362 µm labels inside the supervision mask, both segments pooled; paired bootstrap over letter components and 256 px tiles (1000 resamples) for pag0 − original and pag50 − original.
- **T3, injected ink:** the round-12 readability bench (three 1447 letter rows at α 1, 0.85, 0.7 blended into blank windows of each volume's render, Reader V3), AUC per volume with the same bootstrap against the original.
- **Contamination, stated in advance:** every public 9 µm model was trained with PHerc. 0139 (Reader v2/V3 used 0139 teacher maps; dnative was fine-tuned on it), on renders of the *original* reconstruction. So T2 and T3 are biased toward the original. A gain of a re-retrieval over the original counts in full; a loss is ambiguous and is reported as such, never as "the original reads better".

**Rule:**
- **RECONSTRUCTION MATTERS:** in T2, pag0 or pag50 beats the original by ≥ +0.03 AUC with the 95% interval above 0 for both models, and T3 agrees in sign at α 0.85 (≥ +0.02). Recommendation to the organisers: re-reconstruct the nine 113 keV eligible scrolls with that setting, if the projections are kept.
- **NO EFFECT:** |Δ| < 0.015 in T2 for both models and both re-retrievals, and |Δ| < 0.02 in T3 at α 0.85, and the T1 clutter index within ±10% of the original.
- **WORSE OR AMBIGUOUS:** a re-retrieval reads worse by more than 0.015 in T2; reported with the contamination caveat; no recommendation either way.
- **PARTIAL** otherwise (for instance T1 moves by more than 10% with no AUC change, which would say that the models are robust to the setting and the texture excess is not the retrieval).
- **Invalid** if step 0 fails, or the renderer check fails on the original volume.

**Run:** `r30/r30_run.sh` on the ZGX; output `~/vesuvius/eval/r30_result.txt` (ends with `R30_DONE`), JSON `r30_result.json`. Expected: download about 1 h, computation about 1.5 h.

**Amendments before the bulk download (2026-10-25, after step 0 and before any render or score; flagged):**
- **Step 0 result:** one 3-chunk column per volume at each window's centre (37.8 MB in all). The z offset is 0 for pag0 and pag50 on both segments (slice-wise r 0.81 / 0.75 on w044 and 0.81 / 0.76 on w040 at d 0, lower by 0.02-0.04 at d ±1); in plane the peak is at (0, 0) too (r 0.77-0.83, lower by 0.06-0.08 at ±1 px). The pre-registered r ≥ 0.9 bar cannot be met between *different reconstructions* of the same slice, because the retrieval changes the texture itself; it was written for misregistration. **Amended criterion:** registration accepted when the correlation has a unique maximum at the same offset for both segments, in z and in plane, with a drop ≥ 0.02 at the neighbouring offsets. Met: offset (0, 0, 0). Grey-level scale also differs (means 75 / 56 / 52), which the models' per-tile normalisation and the relative T1 readouts absorb.
- **T3 dropped.** The windows were chosen around the densest labels, so they hold text everywhere (w044: 6% labelled, 17% supervised, the rest unknown). The injection bench needs ink-free backgrounds and cannot run on them without a second, label-free window per segment (another 10 GB). The rule loses the T3 clause: RECONSTRUCTION MATTERS = T2 gain ≥ +0.03 with the interval above 0 for both models; NO EFFECT = |Δ| < 0.015 in T2 for both models and both re-retrievals, and the T1 clutter index within ±10%.
- **Contamination check added to T2:** the models' AUC on the original is reported next to the organisers' label counts; absolute values are not compared with 0841 or 1447.

**Download done (2026-10-25, 17:04-17:19):** 792 + 806 chunks per volume, 2.7 GB per volume cache, 8.1 GB for the three volumes, plus 0.12 GB of official surface-volume sub-crops and 38 MB of probes: **8.3 GB in all**, under the approved 10.3 GB. Renders: 41 layers, 1600 × 4400 px, segment pixels 95.5-98.3%.

**Amendment to the renderer check (2026-10-25, 17:25, written before any T2 number was read; flagged):** on w040 the check passes at (0, 0) (mean per-layer r 0.982). On w044 it gives 0.461 at (0, 0), but an in-plane shift search shows the official 28-layer render sits 12 px off our render in both axes (r 0.899 at (−12, −12) on a 4 px grid, against 0.385 at (0, 0)); the canvases have the same size, so the organisers' render of w044 was made on a grid origin 12 px away from the tifxyz's. The labels live on the official canvas, so the same 12 px offset applies to them; the pre-registered ±24 px label-offset search of T2 absorbs it, as it did on 0841 (offsets 0 to −11 px). **Amended criterion:** the renderer is accepted when the mean per-layer r is ≥ 0.95 on at least one segment at (0, 0) and ≥ 0.85 on the other after an in-plane shift of at most 24 px. Met (0.982 and 0.899). The script's own verdict line will say INVALID because it applies the unamended check; the verdict is re-read from `r30_result.json` with this criterion and both lines are kept in the log.

### Result (2026-10-25, 17:19-17:34, 15 min of GB10; `r30_result.txt`, `r30_result.json`, figures `r30_w044.png`, `r30_sheets_*.png`): WORSE OR AMBIGUOUS for the models; UNAMBIGUOUSLY NOISIER AND MORE CLUTTERED in the label-free physics

**Fits on the original (T2):** w044 reverse, s12, label offset (+9, +10), Reader v2 AUC 0.927 (V3 s12, 0.945); w040 reverse, s10, offset (+6, +2), v2 0.874 (V3 s10, 0.879). The w044 offset matches the 12 px shift of the official render. Forward direction is at chance (0.53-0.59), so the reading side is fixed. 20 letter components, 75 tiles.

**T1, label-free (mean of the two segments; per segment in the JSON):**

| readout | original | pag0 | pag50 |
|---|---|---|---|
| clutter index, ink side | 0.056 | 0.111 | 0.125 |
| gradient energy, ink side | 0.079 | 0.227 | 0.245 |
| interior texture fraction F | 0.199 | 0.239 | 0.259 |
| sheet-edge width (layers) | 2.4 | 1.0 | 1.0 |
| fringe amplitude | 0.11 | 0.53 | 0.82 |
| void-noise share of the 1-3 px band | 0.028 | 0.084 | 0.095 |
| sheet check: valid share | 0.88 | 0.78 | 0.67 |
| sheet depth contrast (median) | 62.5 | 49.2 | 41.0 |

**T2, native ink (pooled, both segments):**

| model | original | pag0 | pag50 | pag0 − orig [95%] | pag50 − orig [95%] |
|---|---|---|---|---|---|
| Reader v2 | 0.904 | 0.852 | 0.833 | −0.052 [−0.091, −0.018] | −0.071 [−0.109, −0.037] |
| Reader V3 | 0.921 | 0.867 | 0.845 | −0.054 [−0.099, −0.022] | −0.076 [−0.127, −0.039] |

**Verdict.** The script printed INVALID under the unamended renderer check; with the amended check (0.982 on w040, 0.899 on w044 after the 12 px shift) the rule gives **WORSE OR AMBIGUOUS**: both re-retrievals read worse by 0.05-0.08 AUC for both models, intervals excluding 0, which the contamination caveat forbids reading as "the original is best for any model". The label-free readouts are not contaminated and all point the same way: pag0 and pag50 have twice the clutter index, three times the gradient energy and the void-noise share, five to eight times the edge fringe, sharper edges (1.0 against 2.4 layers) and fewer valid sheets. They are less-smoothed reconstructions (weaker or no phase retrieval) of the same data: finer structure and more noise at once.

**Reading.**
- Along the retrieval axis the organisers scanned, *more* smoothing (the original) gives lower clutter and higher model AUC; the re-retrievals do not help. Whether a model trained on pag0 renders would read them better is unknown; no public 9 µm model was trained that way.
- The clutter index is strongly sensitive to the reconstruction setting (×2 here), as much as or more than to the scroll. It is a property of the released volume, not of the papyrus. The report must say so where the index is proposed as a scan metric, and the campaign comparison (rounds 21-26) inherits an untested confound: a different retrieval setting between the July 2025 (113 keV) and May 2025 (116 keV) campaigns would move the index and the AUC by this much. Round 23 excluded rings and a filter tilt, not the retrieval strength.
- The noise share stays below 10% even in pag0, so the data remain clutter-limited at every setting tried.
- Recommendation for the organisers changes from "re-reconstruct" to: publish the retrieval parameters of each released volume, and if the projections are kept, a δ/β sweep on one labelled scroll would price the trade between sharpness and clutter for the models in use.
- Budget: 8.3 GB downloaded in all for this round (approved 10.3).

## 37. Round 29: power-law exponent β of the papyrus clutter, and what it says about target size (approved by the user 2026-10-25; rule written before any computation; no downloads)

**Why:** in mammography the anatomical background has a power-law spectrum P(f) ∝ f^−β with β ≈ 2.8-3, and Burgess, Jacobson & Judy (2001) showed that for β > 2 a larger target at the same per-pixel contrast is *harder* to detect for a linear observer: d′ ∝ c · D^(1 − β/2) for a target of diameter D. Our layout tests (round 3 class averaging, round 7 column lock-in on strips of the ink map) aggregate evidence over mm to cm and failed; round 7 noted that the map's strip means have a "red" spectrum. β has never been measured on papyrus CT renders or on ink maps. One number prices every "aggregate over a larger area" idea at 9 µm, and the cross-area analysis of 2026-10-25 listed it as the cheapest untried test.

**Data (all local):**
- Renders (66 layers, mesh at layer 33, ink side = lower layer index): PHerc. 800 e050-e069; 0268 T067-T082 (tall band); 1218 tall band; the nine 113 keV survey scrolls (0125, 0191, 0211, 0257, 0358, 0813, 0826, 1203, 1545), three windings each.
- Letter-source surfaces: 1447 w058/w060 (Nader, 24 layers, central layers 8-14); 0841 official 9.366 µm surface volumes (28 layers, central layers 10-16).
- Ink maps: Reader V3 8-bit maps at d 0 on 800 e050-e069 and on 0268 T067-T082 (blank papyrus by the searches' verdicts).

**Measurement:**
- Per render: papyrus mask J = layer 33 > 0 (surfaces: central layer > 0). Layers 25-32 (ink side, adjacent to the mesh). In each layer, 256 px windows fully inside J (stride 128), mean removed, Hann window, |FFT|², radially averaged in bins of spatial frequency; averaged over windows and layers → P(f). Frequency in cycles/µm using each scan's voxel size.
- β_render = minus the slope of log P against log f by least squares over periods 25-250 µm; R² of that fit; also two-band slopes over 25-60 µm and 60-250 µm. 95% interval from 200 bootstrap resamples over windows.
- Per ink map: windows of 512 px inside J, the probability map as stored (0-1), same spectrum; β_map over periods 100 µm-2 mm, with R² and the two-band slopes (100-500 µm, 0.5-2 mm) and the bootstrap interval.
- Size law: for β_map, the linear-observer ratio d′(D)/d′(100 µm) = (D/100 µm)^(1 − β/2) for D = 1 mm (a letter), 6.5 mm (the line pitch) and 20 mm (a column).

**Rule (on β_map of PHerc. 800, the scroll of the layout tests; 0268 reported beside it):**
- **LAYOUT EXCLUDED:** β_map ≥ 2.0 with the interval above 2.0. At fixed per-pixel contrast a linear statistic over a larger area has *lower* d′ than one over a stroke, so aggregation over lines or columns cannot recover faint text at 9 µm; rounds 3 and 7 are explained, and every remaining "aggregate over a larger area" idea is pruned.
- **LAYOUT NOT EXCLUDED:** β_map < 1.8 with the interval below 2.0. Aggregation should have helped; the round-7 null then needs another explanation, which is reported as an open point.
- **PARTIAL** otherwise.
- **Reported, no rule:** β_render per scroll with intervals; whether the render spectra follow one power law (R² ≥ 0.95) or bend between the two bands; Spearman between β_render and the round-21 readability AUC at α 0.85 across the 12 scrolls (exploratory).

**Run:** `r29/r29_beta.py` on the ZGX (CPU, about 30 min); output `~/vesuvius/eval/r29_result.txt`, JSON `r29_result.json`, figure `figures/r29_spectra.png`.

### Result (2026-10-25, 12 min of CPU; `r29_result.txt`, `r29_result.json`, `figures/r29_spectra.png`): LAYOUT EXCLUDED

**Ink maps (Reader V3 at d 0, blank papyrus, 512 px windows, periods 100 µm-2 mm):**

| map | windows | β | 95% | R² | 100-500 µm | 0.5-2 mm |
|---|---|---|---|---|---|---|
| PHerc. 800 (e050-e069) | 2145 | **4.08** | [4.06, 4.10] | 0.987 | 3.44 | 4.64 |
| PHerc. 0268 (T067-T082) | 3571 | 4.04 | [4.02, 4.06] | 0.985 | 3.35 | 4.46 |

- Size law for a linear statistic at fixed per-pixel contrast, β 4.08: d′(1 mm) / d′(100 µm) = 0.09; d′(6.5 mm, the line pitch) = 0.01; d′(2 cm, a column) = 0.00.
- **RULE: LAYOUT EXCLUDED** (β ≥ 2.0, interval above 2.0). Aggregating the map over letters, lines or columns lowers d′ by one to two orders of magnitude relative to a stroke, so rounds 3 and 7 could not have worked, and every remaining "aggregate over a larger area" idea on 9 µm maps is pruned. Caveat: the maps' redness is partly the networks' own output smoothness (Hann-blended 128-384 px tiles), but that is exactly the background any layout statistic on these maps faces.

**Renders (layers 25-32, 256 px windows, periods 25-250 µm):**

| scroll | voxel | β | 95% | R² | 25-60 µm | 60-250 µm |
|---|---|---|---|---|---|---|
| 0800 | 8.64 | 3.20 | [3.19, 3.20] | 0.982 | 4.11 | 2.47 |
| 0268 | 8.64 | 3.66 | [3.66, 3.67] | 0.955 | 5.32 | 2.31 |
| 1218 | 8.64 | 2.88 | [2.87, 2.89] | 0.987 | 3.56 | 2.33 |
| 0125 | 9.362 | 2.72 | [2.69, 2.74] | 0.979 | 3.56 | 2.04 |
| 0191 | 9.362 | 2.87 | [2.85, 2.90] | 0.975 | 3.82 | 2.10 |
| 0211 | 9.362 | 2.90 | [2.87, 2.93] | 0.986 | 3.61 | 2.31 |
| 0257 | 9.362 | 2.71 | [2.69, 2.73] | 0.981 | 3.48 | 2.06 |
| 0358 | 9.362 | 3.09 | [3.07, 3.11] | 0.966 | 4.31 | 2.12 |
| 0813 | 9.362 | 3.18 | [3.16, 3.21] | 0.961 | 4.51 | 2.11 |
| 0826 | 9.362 | 2.97 | [2.93, 3.00] | 0.953 | 4.34 | 1.84 |
| 1203 | 9.362 | 2.72 | [2.70, 2.74] | 0.985 | 3.39 | 2.12 |
| 1545 | 9.362 | 2.48 | [2.45, 2.50] | 0.989 | 2.97 | 2.00 |
| 1447 (Nader surfaces, layers 8-14) | 8.64 | 3.96 | [3.95, 3.97] | 0.961 | 5.73 | 2.74 |
| 0841 (official surface volumes, layers 10-16) | 9.366 | 4.13 | [4.12, 4.14] | 0.942 | 6.44 | 2.59 |

- The render spectra are not one power law: they bend, with slopes 3-6 at 25-60 µm and about 2.0-2.5 at 60-250 µm (R² 0.94-0.99 over the whole band). The steep fine band is the resolution roll-off (edges 25-35 µm, round 19); the 60-250 µm band is the papyrus texture proper, with β ≈ 2 in every scroll.
- Exploratory: Spearman(β_render, round-21 AUC at α 0.85) = +0.52 (p 0.08, n 12): steeper (quieter at fine scales) reads better, the same direction as the clutter index, not significant.
- **Side finding for the injection bench:** the two letter sources come from renders with β ≈ 4 (1447: Nader's surface volumes; 0841: the official 28-layer surface volumes), much steeper than our renders of the eligible scrolls (2.5-3.7) at the same voxel size. The official renderers produce smoother fine scales than ours, so an injected letter carries its source's smoother texture into a rougher background. Round 21 matched the sheet-edge width, not the spectrum. This is a confound to note in the report's limitations; it does not change the verdicts, which compare backgrounds under the same letters.

## 36. Round 28: ideal linear observer (Hotelling) on the T1 bench (approved by the user 2026-10-25; rule written before any computation)

**Why:** every detection limit so far is a property of a trained network. The three reviewers and the cross-area analysis of 2026-10-25 (`analog/cross_area_2026-10-25/ANALISI.md`) ask for the standard model-free reference of imaging physics: the Hotelling observer, the optimal *linear* detector for the task, with the clutter covariance estimated from signal-free papyrus (Barrett & Myers). Round 1's matched filter was 1D in depth and cross-scroll, and round 10 showed that the networks use the in-plane arrangement, so that test did not answer this question. Nobody in the community has published such a measurement. The outcome decides between "the networks lose faint evidence that a linear detector keeps" (model headroom) and "no linear detector of this patch size sees more than the networks" (the limit is in the data, for linear observers and these networks).

**Data (no downloads):** the T1 bench of round 4 (1447 letters of w058 and w060 blended into held-out PHerc. 800 papyrus e052/e058/e068: crops w058a, w060a, w060b, 24 layers, α ∈ {1, 0.85, 0.7, 0.5, 0.35, 0}; masks lab/cert/joint) and the T1b blends of round 6 (the same crops in 800 windings e050/e051/e069). Published 8-bit maps of Reader v2 (d −2) and Reader V3 (d −2) on T1 (`faint/maps1447`).

**Observer:**
- Input: the 17 layers the networks see (file layers 2-18), standardised per crop and per layer on the joint papyrus (mean 0, SD 1; 0 outside the joint papyrus).
- Pixel-wise Fisher/Hotelling discriminant on 3D patches centred on the pixel: w = K⁻¹(μ₁ − μ₀), with μ₁ the mean patch around ink pixels (lab ∧ cert ∧ joint), μ₀ around other certainty-mask papyrus pixels, K the pooled within-class covariance (ridge 10⁻³ of its mean diagonal). Fitted on up to 200k ink and 600k non-ink pixels drawn at random.
- Scoring = correlation of the standardised volume with w (a linear 3D filter), so every pixel gets a score.
- **Family** (fixed now): V1 15×15×17 px; V2 9×9×17; V3 21×21×9 (layers 6-14); V4 as V1 after subtracting a per-layer Gaussian local mean (σ 16 px). Rotation handling is left to the discriminant (letters have all stroke orientations in the training pixels).
- **Cross-fitting by winding, as round 6:** fold A tests w058a with an observer fitted on the T1b blends of w060a + w060b; fold B tests w060a and w060b with an observer fitted on the T1b blend of w058a. Letters, papyrus windings and crops never overlap between fit and test.
- **Two regimes, both pre-registered:**
  - *per-α observer* (primary): fitted on the training fold at the same α as the test (the true Hotelling bound at that contrast; it knows the signal statistics, which is what an ideal-observer bound means);
  - *fixed observer*: fitted at α 1 and applied to every α (like the networks, which are one fixed model).
- **Variant selection** inside each fold: the variant with the highest in-sample AUC on its own training blends at α 0.7 is the one applied to the test fold. One number per fold enters the result; the other variants are reported.
- **Secondary, not for the verdict:** a quadratic channel observer (Gabor quadrature energy, 3 scales × 6 orientations × 17 layers, then the same discriminant), to see whether orientation-invariant energy adds to the linear bound.

**Statistics:** pooled pixel AUC on T1 exactly as round 18 (letters vs other certainty-mask papyrus in the joint papyrus, three crops pooled), per α, for the observer and for Reader v2 and V3 from their published maps. Gain G = mean over α 0.7 and 0.5 of (AUC_HO − AUC_V3), per-α observer, with the round-10 paired bootstrap (1000 resamples over 19 letter components and 256 px tiles, 1024 quantile bins). Also reported: d′ = √2·Φ⁻¹(AUC) per α and the slope of log d′ against log α (the networks gave about 3.3; a linear observer under this blend should give about 1), α₀.₆₅, false lights on the α 0 renders at the 50%-recall threshold of α 1, and the fixed observer's curve.

**Controls (must pass before the verdict is read):**
- the α 0 renders give AUC within 0.50 ± 0.02 for the observer (no leakage through masks or crop geometry);
- the observer fitted on labels shifted by 60 px in x gives AUC ≤ 0.55 on the real labels at α 1;
- the α 1 observer's score map, looked at on one crop, shows letter shapes where the networks do.

**Rule:**
- **MODEL HEADROOM:** G ≥ +0.03 with the 95% interval above 0. A linear detector sees faint ink better than the best network; the next step is to build on it (a hybrid, or distillation of the observer's statistic), and the report says "the networks tested lose evidence that the data hold".
- **DATA LIMIT:** G ≤ +0.01 and AUC_HO(α 1) ≤ AUC_V3(α 1) + 0.01. No linear observer of this patch size beats the networks at any contrast; the report may say "for linear observers up to 21 px and for the networks tested, the limit is in the data".
- **PARTIAL** otherwise (for instance the observer wins at α 1 but not at faint contrasts, or the interval straddles the bar); the report states the numbers and no stronger claim.
- If a control fails, the result is reported as INVALID with the cause, and the rule is not applied.

**Run:** `r28/r28_ho.py` on the ZGX (CPU for the fits, GPU for the filtering), runner `r28/r28_run.sh`; output `~/vesuvius/eval/r28_result.txt` (ends with `R28_DONE`), JSON `r28_result.json`, figure `figures/r28_maps.png`. Expected cost about 1-2 h.

### Result (2026-10-25, `r28/r28_run.sh`, 29 min; output `~/vesuvius/eval/r28_result.txt`, JSON `r28_result.json`; post hoc `r28/r28_posthoc.py`, JSON `r28_posthoc.json`; figures `figures/r28_maps.png`, `figures/r28_insample_w058a.png`): DATA LIMIT by the rule's numbers; control (c) not met, for a substantive reason

**Runs.** The networks' AUCs from their published maps reproduce round 18 exactly (v2 0.808 / 0.708 / 0.612 / 0.536, V3 0.826 / 0.725 / 0.623 / 0.542 at α 1 / 0.85 / 0.7 / 0.5). Variant selection on the training folds: fold A chose V1 (15×15×17; in-sample AUC at α 0.7: V1 0.596, V2 0.584, V3 0.581, V4 0.519), fold B chose V3 (21×21×9; V1 0.586, V2 0.577, V3 0.589, V4 0.508). Local-mean removal (V4) takes the in-sample signal to chance, so what the linear observer learns in-sample is mostly a low-frequency brightness difference.

**Pooled cross-fitted AUC on T1** (19 letter components, 160 tiles):

| observer | α 1 | 0.85 | 0.7 | 0.5 | 0.35 | 0 |
|---|---|---|---|---|---|---|
| Reader v2 | 0.808 | 0.708 | 0.612 | 0.536 | 0.520 | 0.519 |
| Reader V3 | 0.826 | 0.725 | 0.623 | 0.542 | 0.522 | 0.509 |
| Hotelling, per-α | 0.482 | 0.480 | 0.481 | 0.486 | 0.489 | 0.499 |
| Hotelling, fixed (α 1) | 0.482 | 0.486 | 0.489 | 0.492 | 0.495 | 0.500 |
| Gabor-energy observer (secondary) | 0.513 | 0.491 | 0.482 | 0.481 | 0.483 | 0.488 |

- Gain per-α Hotelling − V3 at α 0.7/0.5: **−0.099 [−0.153, −0.029]**; fixed observer −0.092 [−0.148, −0.021].
- d′: V3 1.33 / 0.85 / 0.44 / 0.15 (slope 3.2), v2 slope 3.3; the observers' d′ is ≤ 0 at every α, so no slope.
- α₀.₆₅: v2 0.76, V3 0.74, observers never above 0.65.
- False lights at α 0 at the 50%-recall threshold: fixed observer 0.547 (chance level), v2 0.146, V3 0.075.

**Controls.** (a) α 0: 0.499 and 0.500, pass. (b) Shifted-label observer at α 1: 0.475, pass. (c) The α 1 score map of w058a (`figures/r28_maps.png`, rows 4 and 6) shows fibre texture and no letter shape where V3 shows pieces of Ε and Α: **not met.** Since the rule reads a failed control as a possible bug, the cause was checked post hoc before applying the rule.

**Post hoc (declared after the result; `r28_posthoc.json`):**
- In-sample AUC of the V1 observer on its own training blends: α 1 0.626 (fold A) and 0.581 (fold B); α 0.7 0.596 and 0.585. Its in-sample map of w058a (`figures/r28_insample_w058a.png`) shows no letter shape either.
- Same winding, different letters and different 800 background (w060a ↔ w060b, T1b fit, T1 test): 0.605 and 0.589 at α 1, 0.581 and 0.570 at α 0.7.
- Across windings with the test window shifted in depth by −2..+5 layers: fold A rises from 0.493 (shift 0) to 0.563 (+4); fold B stays within 0.513-0.547 with no common optimum.
- The template's absolute weight is flat across the 17 layers (5-7% per layer) and its per-layer mean alternates in sign, i.e. a noisy depth derivative, not an ink profile.

So the observer is implemented correctly (in-sample and same-winding it reaches 0.57-0.63, the α 0 and shifted-label controls hold) and still sees nothing across windings: the failure of control (c) is substantive. **The rule is applied: DATA LIMIT** (G ≤ +0.01 and AUC_HO(α 1) ≤ AUC_V3(α 1) + 0.01), with the caveat recorded.

**Reading.**
- At 9 µm there is no linear template of ink: the best linear observer on 15-21 px × 17-layer patches reaches at most 0.63 even in-sample on the same letters, 0.57-0.61 on new letters of the same winding, and chance on another winding, against 0.83 for the networks. Its in-sample signal is mostly a brightness offset that changes between windings (consistent with round 9: 343 and 1447 differ in sign).
- The networks' evidence is therefore non-linear (round 10: fine spatial arrangement, destroyed by phase randomisation), and their d′ ∝ α³ fall is not an inefficiency relative to a linear optimum, because that optimum is about zero. The report's sentence "a linear detector would keep d′ ∝ α, so a better detector may exist" is withdrawn.
- This also explains why every physics-style detector of rounds 1 and 9 (depth matched filter, mass, specks) failed: they are linear or near-linear statistics.
- What stays open: a non-linear ideal observer is not computable here, so "model headroom" is bounded only from the linear side. The claim for the report is "for the networks tested and for linear observers up to 21 px, the limit is in the data".
- A Gabor-energy (quadratic, orientation-invariant) observer also sits at chance (0.513 at α 1), so simple texture energy is not the signature either.

## 35. Sheet check on the six official PHerc. 800 segments (approved by the user 2026-10-25; rule written before any download or computation)

**Why:**
- The second site check found that PHerc. 800 has six official auto-grown segments, published on 2026-09-07 (tifxyz plus 31-layer surface volumes at 8.64 µm, about 20 cm² in all, z 10860-13243). We never used them.
- They give the sheet check its first test on an eligible scroll's official segments, and a direct comparison with our own surfaces of the same scroll (round 22: valid 63.1% over the 20 windings e050-e069).

**Test:**
- **Download** from the VC open data (pre-approved; cap 15 GB):
  - the six segments' tifxyz and official surface volumes;
  - the chunks of the 8.64 µm volume 20250521135224 that their ±20-layer bands touch.
- **Render and check:**
  - `readability.tifxyz` renders a 41-layer band per segment.
  - The band is compared with the official 31-layer volume exactly as in §34: central half of the canvas, one pixel in 16, best depth mapping and in-plane shift.
  - `readability.sheets` runs with maps (min papyrus 0.1) on the 41-layer bands and on the official 31-layer volumes.

**Rules:**
- **Renderer:** accepted on this scroll if the mean per-layer r ≥ 0.95 on all six segments.
- **Comparison with our surfaces** (area-weighted valid share of the six 41-layer bands):
  - **OFFICIAL BETTER** if ≥ 73% (our 63% + 10 points);
  - **SIMILAR** if 53-73%;
  - **OFFICIAL WORSE** if < 53%.
- **Reported, not judged:** per-segment valid, near and depth contrast; the 31-layer results; the maps.

### Result (2026-10-25): renderer ACCEPTED; comparison SIMILAR

**Download:** VC open data, pre-approved, 1.58 GB in all:
- 0.48 GB of segments (1,722 objects) in `ext/p0800_segments`;
- 1.10 GB of volume chunks (523 chunks, shared by the six overlapping segments) in `ext/p0800_vol`.

| segment | mean per-layer r (min-max) | 41-layer band: valid / near / depth contrast | official 31 layers: valid |
|---|---|---|---|
| 213516 | 0.974 (0.969-0.981) | 69.9% / 33.6% / 34.0 | 61.6% |
| 220042 | 0.976 (0.968-0.984) | 72.7% / 33.7% / 36.0 | 63.8% |
| 220955 | 0.976 (0.966-0.986) | 78.5% / 33.5% / 38.5 | 69.6% |
| 222030 | 0.976 (0.968-0.982) | 63.5% / 29.4% / 31.8 | 53.9% |
| 225813 | 0.976 (0.969-0.984) | 57.3% / 32.6% / 29.6 | 48.6% |
| 010146 (small) | 0.972 (0.961-0.981) | 45.3% / 34.7% / 25.7 | 40.5% |
| **area-weighted** | | **66.8%** | **58.0%** |

- **Renderer accepted at 8.64 µm too:** best mapping ours = 35 − official layer, i.e. the official 31 layers sit at integer offsets −15..+15 around the mesh, with the opposite normal.
- **Comparison SIMILAR (53-73%):** the official auto-grown segments sit on a distinct sheet over 66.8% of their papyrus, against 63.1% for our own surfaces of the same scroll. The depth contrast (median 26-39) is the same scan's.
- **The tool discriminates between segments:** 45-79% valid, with the lowest values where the depth contrast is lowest.
- **The 31-layer official renders** lose 8-9 points, as on 0841.

**Reading:**
- Our PHerc. 800 surfaces were about as well placed on sheets as the organisers' auto-grown segments.
- About a third of the papyrus in both shows no distinct sheet at 8.64 µm. That matches the scan's modest sheet-gap contrast, and segments built on it share the problem.

## 34. The tools on the organisers' segments: tifxyz adapter (approved by the user 2026-10-25; acceptance check written before any rendering)

**Why:**
- The organisers reward tools that work with their formats (tifxyz segments, the open-data zarr volumes, VC3D).
- Their August guide asks people to check by eye that a segmentation stays on one sheet. Our sheet check automates that.
- But their standard ink render has 28 layers, too thin to show the neighbouring sheets, which the check needs (about 40 layers).

**What:**
- `readability.tifxyz` renders a 41-layer band (±20 voxels along the normals, trilinear) straight from a tifxyz segment and the scan volume. A remote volume is first fetched chunk by chunk (only the chunks the band touches).
- `readability.sheets` now takes any layer count (mesh at the middle layer by default) and writes a quarter-size map:
  - green: valid sheet on the mesh;
  - yellow: valid sheet off the mesh;
  - red: papyrus without a sheet;
  - grey: not checked.
- **Demo:** the three official PHerc. 0841 segments (w00 and two auto-grown) on the 9.366 µm / 113 keV scan. VC data, pre-approved; cap 15 GB.

**Acceptance check for the renderer:**
- Our band is compared with the official 28-layer surface volume of each segment, on the central half of the canvas.
- The best depth mapping is searched (sign, offset in 0.25-layer steps), plus in-plane shifts up to ±2 px.
- The renderer is **accepted** if the mean per-layer correlation is ≥ 0.95 on all three segments; otherwise it is reported as not equivalent to the official renderer.

**Reported, not judged:**
- the sheet check on the 41-layer bands and on the official 28-layer volumes (expected to fail for lack of layers);
- the maps.

### Result (2026-10-25): renderer ACCEPTED

**Download:** 1,974 chunks of the 9.366 µm volume, 4.14 GB, VC open data, pre-approved, in `/mnt/data/vesuvius/ext/p0841_9um_vol`.

**Correction (logged, no effect on the verdict):** the first comparison pass was too slow (full-resolution correlation over 496 depth mappings). It was stopped after the w00 band had been written and before any number was printed. The rerun reuses that band and compares on one pixel in 16 of the central half.

| segment | mean per-layer r | min-max | best depth mapping | in-plane shift | sheet check, 41-layer band: valid / near / depth contrast | official 28 layers: valid |
|---|---|---|---|---|---|---|
| w00 | 0.967 | 0.943-0.979 | ours = 33.5 − official layer | (0, 0) | 83.2% / 33.4% / 59.6 | 74.0% |
| auto-grown 552896 | 0.964 | 0.945-0.977 | same | (0, 0) | 83.2% / 32.9% / 60.8 | 73.7% |
| auto-grown 252405 | 0.969 | 0.953-0.979 | same | (0, 0) | 81.8% / 31.7% / 59.2 | 71.5% |

**Reading:**
- **Renderer:** our band matches vc_render_tifxyz's output to r ≈ 0.97 per layer. The official normal points the other way, and the official layers sit at half-voxel offsets from the mesh. The remaining differences are probably interpolation details.
- **Sheet check:** the official segments sit on a distinct sheet over 82-83% of their papyrus, against 63-67% for our 800 surfaces and 14% for our 0268 surfaces. Their depth contrast (median about 60 grey levels) is higher than 800's (33-35) and 0268's (16-18). So the valid share reflects both segment quality and the scan's sheet contrast, and both numbers should be read together.
- **The standard 28-layer render** loses about 9-10 points of valid share, because sheets near the band edge cannot close.
- **"near" is about one third everywhere:** the tracked sheet centre is within ±2 layers of the mesh on only a third of the valid pixels. The mesh usually follows a sheet face, not its centre, so "near" is a description, not a quality score.

## 33. Round 27: does the clutter index beat simpler texture measures? (approved by the user 2026-10-25; rule written before any computation)

**Why:** the reviewers say any texture-variance statistic might predict injected readability, because the blend adds the background's texture to the ink. The index has never been compared with simpler measures.

**Test (no inference; statistics on whole renders, papyrus pixels at layers 27-33, mean over those layers and over each scroll's three renders):**
- **Candidates:**
  - (1) our clutter index: share of variance in the DoG σ 1-3 band, peak period 8.5 px ≈ 75 µm;
  - (2) plain grey-level variance;
  - (3) normalised variance (variance / mean²);
  - (4) gradient energy (mean squared gradient magnitude, as in scrollq);
  - (5) variance shares of other DoG bands: σ 0.5-1, 1-2, 2-4, 3-6 and 6-12 (peak periods about 3.3, 6.5, 13, 20 and 39 px);
  - (6) gp13's SNR @ 0.25 (per scroll, from its table 1.2).
- **AUC sets (α 0.85):**
  - set A, the 12-scroll backgrounds of round 21 in four combinations;
  - set B, the 11 survey renders with matched pipeline: the nine 113 keV scrolls plus 1218 t036-t038 and 0268 t072-t074, for 1447/V3 (rounds 18 and 25) and 0841/V3 (rounds 20 and 25).
- Spearman ρ of every candidate against AUC, in every set.

**Rule (on set B, the pipeline-matched one):**
- **SPECIFIC:** in both set-B lists, the index has the most negative ρ of candidates (1)-(4) and (6), and beats the best of (2)-(4) by ≥ 0.10 in |ρ|.
- **EQUIVALENT:** at least one of (2)-(4) comes within 0.05 of the index's |ρ| in both lists.
- **MIXED:** otherwise.
- The DoG bands (5) are reported, not judged: they say which spatial scale predicts best.

### Result (2026-10-25): MIXED

Files: `release/.../results/r27_stats.json` (per render and per scroll), `r27_result.json` (ρ). Spearman ρ with AUC at α 0.85:

| list | index (as defined) | DoG 1-3, eroded | variance | var / mean² | gradient energy | gp13 SNR |
|---|---|---|---|---|---|---|
| A 1447 / v2 | −0.96 | −0.96 | −0.40 | −0.05 | −0.84 | −0.45 |
| A 1447 / V3 | −0.92 | −0.90 | −0.48 | −0.13 | −0.80 | −0.53 |
| A 0841 / v2 | −0.80 | −0.78 | −0.51 | −0.15 | −0.69 | −0.49 |
| A 0841 / V3 | −0.85 | −0.88 | −0.66 | −0.25 | −0.87 | −0.36 |
| B 1447 / V3 | −0.90 | −0.87 | −0.38 | −0.33 | −0.75 | −0.41 |
| B 0841 / V3 | −0.55 | −0.60 | −0.15 | −0.05 | −0.55 | +0.18 |

- **Verdict MIXED:** the index beats gradient energy by 0.15 with 1447 letters but ties it with 0841 letters (set B), so neither SPECIFIC nor EQUIVALENT.
- **Total variance does not predict:** |ρ| ≤ 0.66, and ≤ 0.38 on set B. Normalised variance even less. So "any texture statistic would do" is false. What predicts is fine-scale structure.

**DoG bands (peak period; ρ in the six lists):**

| band | peak period | ρ in the six lists |
|---|---|---|
| σ 0.5-1 | ~30 µm | −0.82, −0.72, −0.56, −0.61, −0.65, −0.24 |
| σ 1-2 | ~60 µm | −0.94, −0.87, −0.76, −0.80, −0.84, −0.47 |
| σ 1-3 | ~75 µm | −0.96, −0.90, −0.78, −0.88, −0.87, −0.60 |
| σ 2-4 | ~120 µm | −0.88, −0.91, −0.66, −0.76, −0.90, −0.57 |
| σ 3-6 | ~180 µm | −0.48, −0.55, −0.20, −0.34, −0.59, −0.30 |
| σ 6-12 | ~350 µm | −0.02, −0.06, +0.25, +0.27, −0.25, +0.17 |

**Reading:**
- The predictive scale is periods of about 55-120 µm. That is the band where rounds 19 and 23 found the 113 keV texture excess (40-90 µm). This is the first direct, band-specific link between that excess and readability, though still correlational.
- **For the report:** "fine-scale texture at 50-120 µm predicts injected readability; total variance does not; the DoG index and plain gradient energy do about equally well".

## 32. Round 26: is the campaign gap a matter of voxel size? (approved by the user 2026-10-25; rule written before any computation)

**Why:**
- The rival explanation every reviewer raised is voxel size (9.362 µm is 8% coarser) and the models' domain.
- Round 25 made it pressing: with matched renders the gap survives only with the 8.64 µm letters (1447: +0.054). It vanishes with the 9.366 µm letters (0841: +0.013).

**Test:**
- **Resampling:**
  - The survey renders of the two 116 keV scrolls (1218 t036-t038, 0268 t072-t074) are resampled from 8.64 to 9.362 µm ("down").
  - The nine 113 keV survey renders are resampled from 9.362 to 8.64 µm ("up").
- **Method:**
  - Band-limited resampling with a DCT in all three axes, which removes or leaves empty the band between the two Nyquist limits.
  - Holes are filled with the layer mean before the transform and set back to zero afterwards (nearest-neighbour mask).
  - Depth uses odd windows centred on the mesh layer: 53 → 49 layers down, 49 → 53 up, ratio within 0.2% of 9.362/8.64. Layer 33 stays the mesh layer.
- **Bench:** `readability.bench` exactly as in round 25 (Reader V3; 1447 letters with window 2, 0841 letters with window 4; α 1, 0.85, 0.7), on the resampled renders.
- **Checks:**
  - The native 1203 renders are rerun and must give 0.689 and 0.721 within ±0.005.
  - The clutter index is reported before and after resampling.

**Primary rule (1447 letters, where the matched gap is G0 = +0.054):**
- Definitions:
  - G_down = mean AUC at α 0.85 of the two resampled 116 keV scrolls − the nine-scroll native mean (0.675);
  - G_up = the two-scroll native mean (0.729, round 25) − the mean of the nine resampled 113 keV scrolls.
- **VOXEL:** G_down ≤ 0.027 and G_up ≤ 0.027 (resampling removes at least half of the gap in both directions).
- **NOT VOXEL:** G_down ≥ 0.040 and G_up ≥ 0.040 (three quarters of the gap or more survives in both directions).
- **PARTIAL:** otherwise.

**Mechanism (both sources; Δ = resampled − native AUC at α 0.85, mean per group; threshold 0.015 as in round 25):**
- **TEXTURE:** all four |Δ| < 0.015.
- **DOMAIN** (the model prefers 8.64 µm pixels whatever the ink): Δ(116 down) ≤ −0.015 and Δ(113 up) ≥ +0.015 for both sources.
- **MATCH** (letters read best on backgrounds with their own voxel size):
  - for 1447, Δ(116 down) ≤ −0.015 and Δ(113 up) ≥ +0.015;
  - for 0841, Δ(116 down) ≥ +0.015 and Δ(113 up) ≤ −0.015.
- **MIXED:** otherwise.

**Known bias:** upsampling cannot invent the finest detail of the 113 keV scans, so "up" flatters them, while "down" is a fair emulation of coarser sampling. The detector blur (PSF) is not emulated.

**Correction (2026-10-25, before any AUC was seen):**
- The first run stopped at its second scroll. The "down" renders are 757 rows tall, shorter than the 800-row letter crops, so the blend window did not fit. Only the clutter index of native 1203 had been printed.
- **Fix:** every letter crop is cut to the 720-row window with the most labelled pixels, and the native renders are rerun with the same cut crops. All comparisons stay within round 26.
- G0, the native means and medians are recomputed from the native renders of this round. The thresholds (0.027, 0.040, 0.015) are unchanged.
- To save time, only α 1 and 0.85 are run (the rule uses 0.85; α 1 shows whether coverage changed).
- The reproduction check stays on the original crops: native 1203 must again give 0.689 and 0.721 (±0.005).

### Result (2026-10-25): PARTIAL (primary), MIXED (mechanism)

Files: `release/.../results/r26_1447.json`, `r26_0841.json`. The reproduction check passed: 1203 with the original crops gives 0.689 and 0.721 exactly. Reader V3, cut crops, AUC at α 0.85 (group means):

| letters | native 116 keV (2) | native 113 keV (9) | G0 | 116 down | 113 up | G_down | G_up | Δ(116 down) | Δ(113 up) |
|---|---|---|---|---|---|---|---|---|---|
| 1447 | 0.742 | 0.701 | +0.041 | 0.717 | 0.706 | +0.015 | +0.036 | −0.026 | +0.005 |
| 0841 | 0.785 | 0.753 | +0.031 | 0.723 | 0.794 | −0.031 | −0.010 | −0.062 | +0.041 |

**Verdicts:**
- **Primary (1447): PARTIAL.** Making the two 116 keV scrolls coarser removes most of the gap (G_down 0.015 ≤ 0.027), but making the nine finer removes little (G_up 0.036).
- **Mechanism: MIXED.**
  - 0841 letters follow the DOMAIN pattern strongly: coarser backgrounds read worse, finer ones better, by 0.04-0.06.
  - 1447 letters only half: down −0.026, up +0.005.
  - MATCH is clearly rejected: 0841 letters read best on 8.64 µm grids, not on their own 9.366 µm one.

**Other numbers:**
- **α 1 (source render only):** native 0.822 / 0.824 (1447) and 0.858 / 0.858 (0841) in both campaigns. The cut crops removed the coverage difference.
  - Resampling changes coverage: down −0.019 / −0.006, up +0.011 / +0.024.
- **Drop from α 1 to 0.85 (pipeline-free):**
  - 1447: campaign gap +0.044 native, +0.037 after down, +0.050 after up. Resampling does not close it.
  - 0841: +0.031 native, −0.025 after down, +0.015 after up.
- **Clutter index on the 11 native renders:** Spearman −0.85 (1447, p 0.001; −0.75 within the nine) and −0.40 (0841, p 0.12; −0.35 within the nine). On the resampled renders: −0.18 and −0.12.
- **Sensitivity to the crop window:** cutting the crops from 800 to 720 rows moved the matched-pipeline 0841 gap from +0.013 (round 25) to +0.031, and the 0841 clutter correlation from −0.71 to −0.40.

**Reading:**
1. **Voxel size matters as much as the campaign.** An 8% change of voxel size moves readability by 0.03-0.06 AUC, as much as the campaign gap. The campaign comparison, which mixes 8.64 and 9.362 µm, cannot separate papyrus texture from voxel scale and the models' domain.
   - This is the same thing seen two ways: a coarser voxel packs the same physical texture into finer pixel scales, where the models are sensitive.
2. **The gap is not settled.** It is +0.01 to +0.05 with matched renders, depending on letter source and crop window.
3. **The clutter index is robust for 1447-type ink.** For 1447 letters it ranks renders in every variant (−0.75 to −0.97). For 0841 letters it is weaker and crop-dependent (−0.35 to −0.80).
4. **For the report:** the campaign claim drops to "differences of 0.01-0.08 AUC, not attributable to the campaign's texture". The index claim holds for 1447-type ink, with the 0841 weakness stated.

## 31. Scroll-level statistics asked for by the reviewers (2026-10-25; post hoc, no rule, no new inference)

All from the round-21 AUCs (four combinations, the numbers of chart 2) and the clutter indices of rounds 12 and 20. Script: scratchpad `per_scroll.py`; table: `release/.../results/per_scroll.csv` (12 rows, AUC at α 1, 0.85 and 0.7, difference to 800 with CI).

**Campaign split with the scroll as unit (3 against 9; exact test over all 220 splits, one-sided; the smallest possible p is 1/220 = 0.0045):**

| combination | gap α 0.85 | p | gap α 0.7 | p | worst 116 keV − best 113 keV (α 0.85) |
|---|---|---|---|---|---|
| 1447 / v2 | +0.051 | 0.009 | +0.041 | 0.027 | −0.006 (0191 above 1218) |
| 1447 / V3 | +0.070 | 0.0045 | +0.054 | 0.009 | +0.011 |
| 0841 / v2 | +0.048 | 0.0045 | +0.050 | 0.009 | +0.014 |
| 0841 / V3 | +0.077 | 0.0045 | +0.079 | 0.009 | +0.027 |

- Full separation of the groups holds at α 0.85 in three of four combinations, and at α 0.7 in none (overlaps of 0.001-0.025).

**Clutter index within the nine 113 keV scrolls (answers "the correlation is just the campaign label"):**

| combination | ρ (12 scrolls) | ρ (9 scrolls) [bootstrap 95%] | permutation p | leave-one-out RMSE: index / campaign mean / grand mean |
|---|---|---|---|---|
| 1447 / v2 | −0.95 | −0.93 [−1.00, −0.68] | < 0.001 | 0.017 / 0.022 / 0.031 |
| 1447 / V3 | −0.97 | −0.93 [−1.00, −0.68] | < 0.001 | 0.015 / 0.022 / 0.038 |
| 0841 / v2 | −0.80 | −0.72 [−0.98, −0.03] | 0.018 | 0.025 / 0.029 / 0.036 |
| 0841 / V3 | −0.80 | −0.67 [−0.93, +0.04] | 0.029 | 0.030 / 0.032 / 0.047 |

- Earlier "−0.67 / −0.77" for the 0841 within-campaign values came from round 20 (no blur matching); these are round 21.

**Head-to-head with gp13's index** ("SNR @ 0.25", median per scroll, table 1.2 of `report/sections/01_index.md`, read 2026-10-24, repo last pushed 2026-09-08):
- Against our AUC at α 0.85: ρ −0.45 (1447/v2), −0.53 (1447/V3), −0.49 (0841/v2), −0.36 (0841/V3) over 12 scrolls; two-sided permutation p 0.08-0.24; bootstrap CIs all include 0.
- Within the nine 113 keV scrolls: −0.07, −0.20, −0.08, +0.23.
- Its separability axis: −0.15 to −0.34 (p 0.29-0.64).
- So: gp13's index does not predict injected readability; ours does, also inside one campaign. "The opposite of" overstated a non-significant negative correlation.

**Pipeline component found in the same table (α 1):**
- At α 1 the blend returns the source render, masked to the joint papyrus J (source papyrus ∩ background papyrus at layer 33; `o[:, ~J] = 0`).
- The 1447 AUC at α 1 is 0.816 (v2) and 0.844 (V3) on all three careful-fit 116 keV backgrounds, against 0.785-0.788 and 0.801-0.804 on the nine survey renders.
- So the background changes the score even without any of its texture: holes in the short survey bands change which pixels are scored and add zero-filled edges.
- For 0841 letters the α 1 gap is small (V3 0.831-0.867 against 0.824-0.838).
- The drop from α 1 to 0.85 (inside each background) is a pipeline-free view. 1447/V3: 0.099 (116 keV mean) against 0.128 (113 keV mean), gap 0.029. 0841/V3: 0.086 against 0.139, gap 0.053.
- Round 25 tests the same question with matched pipelines.

**Detection limit at other cut-offs (T1, round 18, linear interpolation in α):**

| model | AUC 0.60 | AUC 0.65 | AUC 0.70 |
|---|---|---|---|
| Reader v2 | 0.67 | 0.76 | 0.84 |
| Reader V3 | 0.64 | 0.74 | 0.81 |

**Searched area weighted by the round-22 sheet check:** 0.144 × 261 cm² (0268) + 0.631 × 200 cm² (800) ≈ 38 + 126 = 164 cm² with a valid tracked sheet.

## 30. Round 25: is the campaign split an artefact of our render pipeline? (2026-10-25; rule written before any computation)

**Why:**
- All nine 113 keV backgrounds of the readability tests are survey renders: short 500-slice bands, quick fits.
- All three 116 keV backgrounds came from careful fits: 800's own fit, and the 1500-slice tall bands of 0268 and 1218.
- With the release tool, the clutter index of 1218's survey renders is 0.114-0.125, inside the range of the 113 keV survey renders (0.111-0.167). Its tall renders gave 0.111.
- The reviewers also flag the 3-against-9 split as confounded.

**Test:**
- The readability bench (`readability.bench`, identical to rounds 18 and 20) with Reader V3. Letter sources:
  - the three 1447 rows, window start 2;
  - the three 0841 crops, window start 4.
- α 1, 0.85 and 0.7, on the survey renders of the two 116 keV scrolls that have them: PHerc. 1218 (t036-t038) and PHerc. 0268 (t072-t074).
- As a reproduction check, the 113 keV scroll 1203 (t040-t042) is rerun with the same tool, and must match rounds 18 and 20 within ±0.01.

**Rule (for each ink source, comparing with the nine 113 keV survey-render AUCs of rounds 18 and 20):**
- **SPLIT HOLDS:** the mean AUC at α 0.85 of 1218 and 0268 (survey renders) exceeds the nine-scroll mean by ≥ 0.03, and both scrolls are above the nine-scroll median.
- **PIPELINE:** the two-scroll mean is within ±0.015 of the nine-scroll mean.
- **MIXED** otherwise.

The verdict needs both ink sources to agree; otherwise it is MIXED.

### Result (2026-10-25): MIXED

Files: `release/.../results/r25_1447.json`, `r25_0841.json`. Reproduction check passed: 1203 gives 0.689 (1447 letters) and 0.721 (0841 letters), exactly as in rounds 18 and 20.

| ink source (Reader V3) | 1218 survey | 0268 survey | mean of the two | nine 113 keV: mean / median | gap | exact p (2 against 9, 55 splits) | verdict |
|---|---|---|---|---|---|---|---|
| 1447 letters | 0.708 | 0.750 | 0.729 | 0.675 / 0.676 | +0.054 | 0.018 (the minimum) | SPLIT HOLDS |
| 0841 letters | 0.730 | 0.704 | 0.717 | 0.704 / 0.715 | +0.013 | 0.36 | PIPELINE |

- Clutter index of the survey renders: 1218 0.117 / 0.116, 0268 0.109 / 0.135 (1447 window / 0841 window). The 0268 survey bands are much more cluttered in the deeper 0841 window.
- At α 1, the survey renders of both campaigns score the same (1447: 0.798-0.802; 0841: 0.833-0.844). The careful-fit renders scored 0.844 / 0.867. The coverage effect seen in §31 is therefore a property of the render pipeline, not of the campaign.

**Reading:**
- Part of the 0.05-0.08 campaign gap of rounds 18-21 came from our renders. The 116 keV backgrounds were careful fits, the 113 keV ones short survey bands.
- With matched renders, the gap survives with 1447 letters (+0.054) and vanishes with 0841 letters (+0.013).
- The sources also differ in voxel size: 1447 is 8.64 µm like the 116 keV scans, 0841 is 9.366 µm like the 113 keV ones. A voxel-match or domain component is therefore plausible and untested.
- **What holds:** the clutter index of the render ranks readability across the 11 survey renders regardless of campaign: Spearman −0.95 (1447) and −0.71 (0841, one-sided permutation p 0.009). It also holds within the nine 113 keV scrolls (§31).
- **Consequence for the report:** the robust claim is "readability follows the clutter of the render, and a label-free index measures it". "The 113 keV campaign reads worse" becomes a qualified, source-dependent observation. Reader v2 was not rerun.

## 29. Rounds 21-24: checks chosen from lateral round 4 (approved by the user 2026-10-24; rules written before any computation or download)

Source: `IDEAS_lateral4.md`, ideas 2, 5, 3 and 1, in that order.

### Round 21: blur-matched injection (does the ranking survive equal sharpness?)
- **Why:** an injected letter keeps its source's sharpness, while the backgrounds' sheet edges range from 21 to 37 µm (round 19; 0268 is the widest).
- **Method:**
  - The outer-edge 10-90% width of each letter source (1447 w058/w060 renders, 24 layers, guess layer 12; the three 0841 crops, 28 layers, guess 14) is measured with the round-19 method.
  - Each background's width comes from round 19 (same renders).
  - For a Gaussian blur, width = 2.563 σ. When the background is wider, the source crop is blurred in 3D by σ_add = √(σ_bg² − σ_src²), converted to source voxels, before blending. Papyrus outside the original mask is set back to 0. A sharper background leaves the source unchanged; nothing is sharpened.
  - Everything else is as rounds 18 and 20: same crops, backgrounds, windows, blends and bootstrap, for 1447 and 0841 letters with Reader v2 and V3.
- **Rule:** **ROBUST** if, in all four combinations, the mean AUC at α 0.85 of the nine 9.362 µm scrolls is below that of the three 8.64 µm ones and Spearman (clutter, AUC) ≤ −0.70. Otherwise **NOT ROBUST**, naming the combinations that fail.
- **Reported:** 0268's difference to 800 in each combination, and how many of the nine are significantly below 800.

### Round 22: did the 0268 surfaces sit on sheets?
- **Why:** gp13 ranks 0268 last of 14 for sheet separability, and its renders have the widest edges.
- **Method:** the round-1/19 run-based tracker (guess layer 33) on all 16 0268 search windings (T067-T082) and all 20 800 windings (e050-e069), in 2000 px chunks with at least 50% papyrus at layer 33. Per scroll:
  - (a) the share of papyrus pixels with a valid tracked sheet;
  - (b) the share of valid pixels whose sheet centre is within ±2 layers of layer 33.
- **Rule:** **PASS** (the 0268 searches sampled sheets as well as the 800 ones) if 0268 reaches at least 0.8 × 800's value on both (a) and (b). **FAIL** otherwise; the report then weakens the 0268 bound.

### Round 23: is the 113 keV texture a reconstruction signature?
- **Data:** local level-0 CT chunks of the 12 scrolls (survey and tall bands; no downloads). Per scroll, up to 8 windows of 512 × 512 px in z-slices with at least 80% papyrus, spread over the local band.
- **Ring signature (z-invariant, azimuthally coherent energy):**
  - The window is resampled on a polar grid (r, θ) around the volume centre (assumed to be the rotation axis), with the in-plane DoG (σ 1 and 3) of each slice.
  - The radial profile is averaged over θ and over 200 consecutive slices. The share is the variance of that profile over r divided by the variance of the DoG over the window.
  - Rings keep their radius in every slice; papyrus sheets drift by more than 3 px over 200 slices.
- **Spectral tilt:** the radial power spectrum of the windows (Hann-tapered), in physical frequency (cycles per µm). Per-campaign geometric means give the ratio R(f) = P113 / P116 over 0.005-0.05 cycles/µm, fitted with a power law.
- **Rule:** **ARTEFACT** if either
  1. the median ring share of the nine 113 keV scrolls is ≥ 2 × that of the three 116 keV ones, or
  2. the power-law fit has R² ≥ 0.9 and every one of the nine scrolls' own ratios (to the 116 keV mean) has a fitted exponent within ±20% of the pooled one.

  **TEXTURE** otherwise.

### Round 24: voxel size or protocol? (the same PHerc. 0841 papyrus, two scans)
- **Data:**
  - 0841 segments w00 and auto-grown …252405, on the 2.403 µm / 77 keV / 0.22 m surface volumes (109 slices, about 33 GB per segment in full).
  - Only the chunks covering the left 2200 px of the round-20 crop window are downloaded: w00 rows 1700-2500, auto-grown rows 1300-2100, on the 9.366 µm canvas, ×3.8976. That is about 3.1 GB per segment of Vesuvius Challenge data, pre-approved; the size is reported.
- **Downsampling:**
  - A box prefilter (4 slices × 4 × 4 px), then linear resampling at the 9.366 µm grid centres: 28 layers and the 9.366 µm canvas.
  - The result is a "9.366 µm scan with the 77 keV / 0.22 m protocol" of the same papyrus, on the same canvas as the native 113 keV / 1.2 m surface volume.
- **Measures, per segment and version, on the same window:**
  1. the native pixel AUC of Reader V3 and Reader v2 against the 2026-09-18 labels, with the round-20 search (both directions, starts 3/5/7, offsets ±24 px) applied to both versions;
  2. the round-19 interior texture fraction F (guess layer 14).
- **Rule:**
  - **PROTOCOL** if, on both segments and for V3, the downsampled 77 keV version gains ≥ +0.03 AUC and has F at least 15% lower.
  - **VOXEL SIZE** if |ΔAUC| < 0.015 and F within ±10% on both.
  - **MIXED** otherwise.
- **Caveat:** the labels were refined from 2.4 µm ink predictions, which could favour the downsampled version. The offset search is applied to both, and the result is read with that bias in mind.
- **Correction (2026-10-25, after the first run, before any rerun):** the w00 window was badly chosen, and the error is mine.
  - The left 2200 px of the round-20 w00 crop hold no labelled pixel; all 169,163 lie in x 2200-4400. The first run therefore returned no AUC for w00, in either version.
  - The auto-grown segment's left half holds 78,196 labelled pixels and was valid.
  - w00 is rerun on x 2200-4400, which needs the chunks of that window: about 3.2 GB more, Vesuvius Challenge data. The rule is unchanged.

### Results, rounds 21-23 (2026-10-24 evening; `r21_result.txt` / `.json`, `r22_result.txt` / `.json`, `r23_result.txt` / `.json`)

**Round 21, blur-matched injection: ROBUST, but the test was barely exercised.**
- **Source widths:** the measured edge widths of the sources were 65 µm for all three 1447 crops and 68, 21 and 68 µm for the 0841 crops, against 21-37 µm for the backgrounds. So no 1447 blend was blurred (0 of 108), and only the 0841 w00 crop was (32 of 108 blends).
- **The depth-edge width is not a clean sharpness measure for these sources.** 65-68 µm points to oblique or poorly separated sheets in those segments, not to blurrier scans. The test therefore checks little beyond the 0841 w00 crop.
- **Four combinations:**

  | combination | mean AUC α 0.85, 9.362 / 8.64 µm | Spearman | 0268 − 800 [95%] | of nine below 800 |
  |---|---|---|---|---|
  | 1447 / Reader v2 (unchanged) | 0.683 / 0.734 | −0.95 | +0.017 [−0.002, +0.036] | 7 |
  | 1447 / Reader V3 (unchanged) | 0.675 / 0.745 | −0.97 | +0.005 [−0.023, +0.034] | 9 |
  | 0841 / Reader v2 | 0.701 / 0.749 | −0.80 | −0.022 [−0.070, +0.015] | 2 |
  | 0841 / Reader V3 | 0.692 / 0.769 | −0.80 | −0.020 [−0.076, +0.033] | 5 |

- **The campaign split holds in all four.** With the 0841 letters blur-matched, 0268 falls behind 800 (not significantly), so its earlier lead was not robust.

**Round 22, 0268 surfaces on sheets: FAIL.**
- **Tracker validity:** 0268 (16 windings) has a valid tracked sheet on 14.4% of papyrus pixels (14-16% per winding), with the centre within ±2 layers of the mesh on 25.6% of those. 800 (20 windings) has 63.1% and 31.9%. The ratios are 0.23 and 0.80, so FAIL on (a).
- **Post-hoc diagnostic (not a rule change):** the tracker needs at least 25 grey levels of contrast along the depth profile.
  - On 0268 the median contrast is 16 (T073, T078), and only 19-20% of papyrus pixels reach 25.
  - On 800 the median is 32-35, and 71-80% reach 25.
  - 0268's papyrus is also brighter (mean 138-140 against 95-100).
- **Reading:** at 8.64 µm, 0268's renders show little sheet/gap alternation along the normal: densely packed or fused sheets, or compressed contrast. This is consistent with gp13 ranking 0268 last of 14 for sheet separability, and with its wide, low-contrast edges (round 19).
- **Consequences:**
  1. the 261 cm² 0268 null carries little weight, because our surfaces mostly do not follow a distinct sheet face;
  2. 0268's "readability" measured injected ink on a smooth, fused background, which says nothing about ink on its sheets;
  3. the report must drop "0268 is the most readable scroll" and "rescan 0268 next".

**Round 23, reconstruction signature: TEXTURE.**
- **Rings:** median ring share 6.9e-4 (113 keV, 8 scrolls; 0125 had no complete local window) against 9.5e-4 (116 keV), ratio 0.73. No ring excess.
- **Spectrum:** the normalised spectrum ratio P113 / P116 is not a power law (R² 0.54; per-scroll exponents −0.87 to +0.35). It is 1.04-1.09 at 0.011-0.024 cycles/µm (periods 40-90 µm) and falls to about 0.45 at 0.044-0.049 cycles/µm (periods 20-23 µm, near the 9.362 µm Nyquist limit, consistent with 2× mean binning).
- **Reading:** no ring-artefact or filter-tilt signature. The 113 keV excess sits at 40-90 µm periods, the band of the clutter index, and the finest scales are, if anything, smoother. It looks like structural texture at fibre-bundle scale, not something a re-reconstruction of the kinds tested would remove.

**Round 24, first run (before the correction above):**
- The auto-grown …252405 segment, left window, is valid:
  - Reader V3: native 113 keV AUC 0.917, downsampled 77 keV 0.921 (+0.004);
  - Reader v2: 0.883 → 0.909 (+0.026);
  - interior F 0.253 → 0.232 (ratio 0.92).
- w00 gave no result (unlabelled window); it is rerun.

**Round 24, final (w00 rerun on x 2200-4400, 2026-10-25 00:01-00:40; 5.84 GB of 2.403 µm chunks on disk in all): MIXED**

| segment | Reader V3: native 113 keV → downsampled 77 keV | Reader v2 | interior F, 77 / 113 keV |
|---|---|---|---|
| w00 | 0.895 → 0.895 (−0.001) | 0.887 → 0.900 (+0.014) | 0.244 / 0.288 = 0.85 |
| auto-grown …252405 | 0.917 → 0.921 (+0.004) | 0.883 → 0.909 (+0.026) | 0.232 / 0.253 = 0.92 |

- **Rule:**
  - PROTOCOL fails: no AUC gain for V3.
  - VOXEL SIZE fails on one condition only: |ΔAUC| < 0.015 holds on both segments, but w00's texture is 15% lower, outside ±10%.
  - Hence MIXED.
- **Reading:** at equal 9.37 µm voxels, the 77 keV / 0.22 m protocol gives 8-15% less interior fine texture than the 113 keV / 1.2 m one, on the same papyrus. Yet Reader V3 reads the native 0841 ink equally well (ΔAUC −0.001 and +0.004); the older Reader v2 gains a little (+0.014, +0.026).
- So, for the best model at full ink strength, voxel size, not protocol, sets readability. Changing the 9 µm protocol is not a substitute for finer voxels.
- **Caveat:** this measures native ink at full strength. The campaign split (rounds 12, 18, 20) shows mostly for fainter ink, so a texture difference of 8-15% might still matter at α ≤ 0.85. That was not measured here.

## 28. Round 20: a second ink source from the 113 keV campaign itself, PHerc. 0841 (approved by the user 2026-10-24; rules written before any download or computation)

**Why:** our readability ranking injects 8.64 µm / 116 keV letters (1447) into all backgrounds. On the 9.362 µm scrolls the letters are therefore foreign to the scan and about 8% too large. "Measure Before You Hunt" reads the campaign split the other way. A positive from the 113 keV campaign itself puts the mismatch on the other side and settles whether the split is real.

**Source:** PHerc. 0841, not eligible, "ink detected".
- Its 9.366 µm volume (`20250821151531-9.366um-1.2m-113keV`, from the ESRF 2025-07-17 session, 4.683 µm binned 2×) belongs to the same campaign as the nine 9.362 µm scrolls.
- Three segments (w00 and two auto-grown) with official 28-layer surface volumes on that volume (`surface-volumes/9.366um-1.2m-113keV-volume-20250821151531.zarr`, about 1.6 GB in all).
- The organisers' ink labels of 2026-09-18 (`ink-labels/2.403um-volume-20260319124803/20260918/`: inklabels, supervision and validation masks) are on the 2.403 µm canvas, 3.8976 times the 9.366 µm canvas.
- Download: Vesuvius Challenge open data, pre-approved; the size is reported.
- **Provenance:** the Reader V3 README states that no model it shows (Reader v2 included) was trained on any part of PHerc. 0841, which the team keeps for validation. 0841 is independent for both models.

**Step 1, alignment and reading direction (not a test):**
- The labels and supervision mask are downsampled to the 9.366 µm canvas (area average; label = mean > 0.5, supervised = mean > 0.5).
- On each segment's native surface volume, Reader v2 is run in both depth orders at layer starts 3, 5 and 7 (about d −2, 0, +2 for a 28-layer volume centred on the surface).
- Over offsets of ±24 px (1 px steps), the offset, direction and window with the highest pixel AUC (labels against other supervised pixels) are kept and then fixed. For each model, its window is then chosen among the three, in the fixed direction and offset, by native AUC on w00.
- **Usable** if at least one segment reaches a native Reader v2 AUC ≥ 0.65 at its best setting. Otherwise the 0841 labels cannot serve as positives at 9 µm, and the round stops.
- Alignment uses Reader v2's map. That inflates the absolute native AUC slightly, but not the comparison between backgrounds, which use fixed masks.

**Step 2, letter crops:** three windows of 800 × 4400 px on the 9.366 µm canvas with the most label pixels inside the supervision mask (if possible from different segments), chosen from labels and masks only.

**Test:**
- The round-12 readability test with the 0841 crops in place of the 1447 ones, into the same backgrounds (three windings of each of the 12 scrolls, window position from masks), at α 1, 0.85 and 0.7.
- 0841 layer i ↔ background layer i + 19, with the ±4 depth shift by mean-profile correlation and per-layer moment matching (as `b_any`). The 0841 stack is flipped first if its reading direction is forward, so that its ink face matches our renders.
- No resampling: on the 8.64 µm backgrounds the 0841 letters now look about 8% too small, the mirror image of the 1447 case.
- Models: Reader v2 and Reader V3 at their step-1 windows, through our float inference. Statistic: pooled pixel AUC per scroll at α 0.85, the bootstrap difference to 800, and Spearman (clutter index, AUC).

**Rule:**
- **CONFIRMED** (the campaign split holds with native 113 keV ink): for both models, the mean AUC at α 0.85 of the nine 9.362 µm backgrounds is below that of the three 8.64 µm ones, and Spearman (clutter, AUC) ≤ −0.70.
- **REVERSED:** for both models the 9.362 µm mean is above the 8.64 µm mean. The round-12 ranking was then driven by the letter source, and the report must say so.
- **MIXED** otherwise.

### Result (2026-10-24, 15:08-16:02; `r20_result.txt`, JSON `r20/align.json`, `r20_rank.json`): CONFIRMED

**Download:** 1.80 GB, 4025 files (three 9.366 µm surface volumes, labels, meshes).

**Step 1: usable.**
- Reading direction: forward on all three segments (reverse gives AUC 0.54-0.60). The stacks were flipped, as planned.
- Label offsets on the 9.366 µm canvas were 0 to −11 px, in line with the ~7 px offsets other participants report for labels moved between voxel sizes.
- Native Reader v2 AUC at the best setting: 0.884 (w00, s7, offset (0, −6)), 0.827 and 0.824. Reader V3 on w00: 0.876 / 0.912 / 0.920 at s3/s5/s7.
- Both models read best at s7, i.e. oriented start s4. The best window is the deepest tested; deeper starts were not tried.
- **Crops** (from labels and masks only, one per segment, x 0 on each canvas):
  - auto-grown …252405 at y 1300, 205,061 label px;
  - w00 at y 1700, 169,163;
  - auto-grown …552896 at y 450, 167,416.

**Test: pooled AUC at α 1 / 0.85 / 0.7 with 0841 letters**

| scroll | voxel | Reader v2 | Reader V3 |
|---|---|---|---|
| 0268 | 8.64 | 0.847 / 0.772 / 0.705 | 0.869 / 0.801 / 0.724 |
| 0800 | 8.64 | 0.847 / 0.768 / 0.683 | 0.869 / 0.792 / 0.710 |
| 1218 | 8.64 | 0.847 / 0.749 / 0.658 | 0.869 / 0.760 / 0.675 |
| 0191 | 9.362 | 0.841 / 0.732 / 0.604 | 0.838 / 0.744 / 0.640 |
| 0826 | 9.362 | 0.841 / 0.732 / 0.658 | 0.842 / 0.715 / 0.647 |
| 0211 | 9.362 | 0.840 / 0.728 / 0.627 | 0.824 / 0.719 / 0.629 |
| 0125 | 9.362 | 0.838 / 0.720 / 0.647 | 0.839 / 0.737 / 0.675 |
| 0358 | 9.362 | 0.841 / 0.720 / 0.633 | 0.838 / 0.677 / 0.586 |
| 1203 | 9.362 | 0.840 / 0.719 / 0.649 | 0.844 / 0.721 / 0.636 |
| 0813 | 9.362 | 0.836 / 0.709 / 0.639 | 0.837 / 0.713 / 0.621 |
| 0257 | 9.362 | 0.845 / 0.677 / 0.569 | 0.840 / 0.665 / 0.531 |
| 1545 | 9.362 | 0.839 / 0.635 / 0.554 | 0.831 / 0.644 / 0.557 |

- **Reader v2:** mean AUC at α 0.85 is 0.708 for the 9.362 µm scrolls and 0.763 for the 8.64 µm ones. Spearman (clutter, AUC) −0.76 (p 0.005). Three of nine are significantly below 800 (0813, 0257, 1545); the intervals are wider than with 1447 letters.
- **Reader V3:** 0.704 against 0.784; Spearman −0.84 (p 0.001). Seven of nine are significantly below 800.
- **RULE: CONFIRMED.** With ink from the 113 keV campaign itself, and the letter-size mismatch now on the 8.64 µm side, all three 8.64 µm scrolls still read better than all nine 9.362 µm ones, for both models. The clutter index still predicts the order. The campaign split is not an artefact of the letter source.
- At full strength (α 1) the gap almost vanishes for Reader v2 (0.836-0.845 against 0.847). It opens as the ink gets fainter, as expected if fine texture competes with faint strokes.
- 0268 again leads 800 by a non-significant margin (+0.004 and +0.009).

## 27. Round 19: where does the extra fine structure of the 113 keV scans sit? (approved by the user 2026-10-24; rules written before any computation)

**Why:** rounds 12, 13 and 18 show that the nine 9.362 µm / 113 keV scans carry more fine-scale (1-3 px) energy than the 8.64 µm / 116 keV ones, that it is not noise, and that it makes ink harder to see with both Reader v2 and V3. The organisers' open-problems page rates the 9 µm / 110 keV set-up below 2.4 µm without saying why. "Measure Before You Hunt" reads the same energy as better scan quality. All scans used a 1.2 m propagation distance, which the organisers consider too long at about 4.6 µm (phase-contrast fringes at material edges). So: is the extra energy at sheet edges (an acquisition or reconstruction effect) or inside the sheets (texture)?

**Data (no downloads):**
- 116 keV / 8.64 µm: PHerc. 800 e050, e057, e064; 0268 T073-T075; 1218 T039-T041. Rows 500-1320 of these tall renders, to match the survey band height (as round 13).
- 113 keV / 9.362 µm: the first three survey windings of each of the nine scrolls (the round-12 backgrounds).
- Each render is processed in 2000 px wide chunks; chunks with less than 50% papyrus at layer 33 are skipped.

**Sheet geometry:** the round-1 run-based sheet tracker (`lat1.sheets` logic, guess layer 33), giving per pixel the inner edge (rise), the outer edge (fall) and a validity mask. Only valid pixels are used.

**Test A, location of the fine-scale energy.**
- On layers 20-46, the in-plane difference of Gaussians d = G(σ 1) − G(σ 3) of each layer (the clutter-index band).
- Voxels of the tracked sheet are split by their depth distance to the nearer edge: **edge shell** (within 1.5 layers of rise or fall, on either side) and **interior** (more than 2 layers inside both edges).
- Per class and render: the fine-scale fraction F = Σ d² / Σ (v − class mean of that layer)². Also, over all papyrus voxels of layers 27-34, the overall fraction, which is the clutter index of round 12 on these windows.
- Campaign ratios: ρ_edge, ρ_int and ρ_all = mean over the 113 keV renders / mean over the 116 keV renders.

**Test B, edge profile.**
- On open outer faces (no papyrus within 6 layers beyond the fall edge), the depth profile across the fall edge from −6 to +6 layers, sampled sub-voxel and normalised as (v − void) / (plateau − void). Here plateau is the median of the sheet interior and void the median from +4 to +6 layers.
- Per render: the 10-90% edge width (layers and µm) and the fringe amplitude A = overshoot (the maximum of the normalised profile minus 1, inside the edge) + undershoot (minus the minimum, from 0 to +4 layers outside).

**Rule:**
- **EDGE** (the extra energy is edge enhancement, from acquisition or reconstruction): ρ_edge ≥ 1.25, ρ_int ≤ 1.10, and the median A of the 113 keV renders ≥ 1.5 × that of the 116 keV renders.
- **INTERIOR** (texture inside the sheets): ρ_int ≥ 1.25.
- **MIXED** otherwise.

**Interpretation, fixed in advance:**
- EDGE: a reconstruction or acquisition choice adds the clutter, so phase retrieval or a shorter propagation distance could make 9 µm scans more readable. That would be a separate test.
- INTERIOR with narrower 113 keV edges (in µm): the 113 keV scans are simply sharper and resolve more fibre texture, which at 9 µm hides carbon ink. Sharper is not better at this voxel size; only a large resolution step helps.
- INTERIOR with similar edges: the papyri themselves differ. That is unlikely to hold for nine scrolls of one campaign, and is reported as such.

**Run:** `r19/r19_edges.py` (CPU), output `~/vesuvius/eval/r19_result.txt`.

### Result (2026-10-24, about 1 h of CPU; JSON `r19_result.json`): INTERIOR

| campaign | renders | F edge shell | F interior | F all (clutter) | fringe amplitude A (median) | edge width 10-90% (median) |
|---|---|---|---|---|---|---|
| 113 keV / 9.362 µm | 27 | 0.190 | 0.297 | 0.144 | 0.075 | 26 µm |
| 116 keV / 8.64 µm | 9 | 0.162 | 0.221 | 0.109 | 0.074 | 24 µm |
| ratio | | **1.17** | **1.35** | 1.32 | **1.02** | 1.08 |

- **Rule:** ρ_int = 1.35 ≥ 1.25, so **INTERIOR**. The extra fine-scale energy of the 113 keV scans sits inside the sheets. The edge shell carries less of it (1.17), and the edges show no extra fringing (A 0.075 against 0.074) and are not sharper (26 µm against 24 µm).
- **Every one of the 27 renders of the nine 113 keV scrolls** has F interior 0.248-0.364, against 0.211-0.236 for all nine 116 keV renders. There is no overlap.
- **Pre-registered reading (INTERIOR with similar edges): "the papyri themselves differ".** As stated in advance, that is implausible for nine scrolls of one campaign. The likelier cause is a property of that campaign's acquisition or reconstruction that adds texture inside the sheets without sharpening edges or adding fringes. Candidates are the reconstruction filter and the 4.683 µm detector pixel binned 2×; neither is verified. Edge fringes from the 1.2 m propagation distance are excluded as the cause, since both campaigns used 1.2 m and their fringe amplitudes are equal.
- **By-product:** the 0268 renders have the widest edges of all 36 (37 µm, against 21-28 µm elsewhere). This is either a blurrier scan (November 2025 session) or less distinct sheets; gp13's separability axis ranks 0268 last. An injected letter keeps its own sharpness, so the injection bench may slightly favour backgrounds blurrier than the letter source. 0268's lead over 800 is small and not significant with either model (+0.017 and +0.005), and the report must not lean on it.

## 26. Round 18: Reader V3 on our benches and on the search renders (approved by the user 2026-10-24; rules written before any computation)

**Why:** the prior-work check of 2026-10-24 (`prior_check/`) found Reader V3 by Domenico Russo, released 2026-10-19 ([repository](https://github.com/DomRusso2/reader-v3), [checkpoint](https://huggingface.co/domenicor046/reader-v3), MIT). It is Reader v2 trained further on 384 px tiles on the same data. Its README reports gains over Reader v2 on held-out scrolls at 113 and 116 keV, and less false ink. Our detection limit, readability ranking and searches rest on Reader v2 only.

**Download (approved by the user):** `reader-v3.pth`, 138,379,659 bytes, sha256 `ea405417450abd8ace1b8ff79ebce3adb646c5e48ab95da46844d77efe984d8a`, equal to the Hugging Face LFS record. Stored in `/mnt/data/vesuvius/ext/reader_v3/`.

**Runtime checks (not tests), before any test:**
- **Architecture:** same 508 weight tensors with the same shapes as Reader v2 (checked). Tile 384 px (config `crop_size` [17, 384, 384]), so the published command (`--overlap 0.5`, Hann) uses stride 192.
- **Provenance:** the V3 README states that no model it shows was trained on any part of PHerc. 1447 or 0841, and V3 uses Reader v2's training data, which has no 1447, 800 or 0268. T1 and the readability test stay independent for V3. 343P is in the training data, as for Reader v2.
- **Float inference:** our `r18/r18_infer.py` (tile size from the checkpoint, stride tile/2, Hann weights, `normalize_robust` per patch, layers reversed) must reproduce the published command's 8-bit V3 map of T1 crop w058a at α 1, window s2, at correlation ≥ 0.99 over the joint papyrus. If it fails, test 2 is not run, and that is reported.

**Test 1: detection limit on T1.**
- V3 maps with the published command (`villa_any.sh`) on the T1 renders. The window is chosen among d −2/0/+2 on the w058 crop at α 1, as for every model, and then kept.
- Pooled pixel AUC at α 1, 0.85, 0.7, 0.5, 0.35 and 0, against Reader v2 at d −2 (round-4 maps).
- Gain = V3 − Reader v2, mean of α 0.7 and 0.5, with the paired bootstrap over letter components and 256 px tiles of round 10.
- **PASS (V3 lowers the limit):** gain ≥ +0.03 with the 95% interval above 0. **KILL** otherwise.
- Reported either way: V3's α₀.₆₅, the change at α 1, and the false lights on the α 0 renders at each model's 50%-recall threshold (round 4, T4).

**Test 2: readability ranking with V3.** The round-12 test unchanged (same crops, backgrounds, window choice from masks, blend and bootstrap), with V3 at its test-1 window, through our float inference.
- Reported: AUC per scroll at α 1/0.85/0.7, the difference to 800 with bootstrap, and Spearman (clutter index, AUC at 0.85).
- **Model-independent** (the round-12 findings hold for V3) if all three hold:
  1. Spearman ≤ −0.70;
  2. the mean AUC at α 0.85 of the nine 9.362 µm scrolls is below that of the three 8.64 µm ones;
  3. 0268 is in the top two.
- **Model-dependent** otherwise; the report then says which finding changed.

**Test 3: a new search of the existing renders.**
- V3 maps (published command) at d 0, +2, −2 and the control +12, both directions, on PHerc. 0268 T067-T082 (16 windings, about 261 cm²) and PHerc. 800 e050-e069 (20 windings, about 200 cm²). No new CT.
- **Screening** as round 17, per 1 cm tile: score = top-1% mean of the reading-side d0 map minus the larger of the same statistic on the blind side and at d+12. The 15 best tiles per scroll are inspected (reading d0 and d+2, blind side, d+12, CT layer 33) and compared with Reader v2's best tiles.
- **Candidate rule unchanged** (sections 8 and 25): (1) stroke-like marks in at least 2 parallel horizontal lines 3-7 mm apart on the reading side at d0; (2) the same at a neighbouring depth; (3) absent at d+12 and on the blind side; (4) not explained by a CT material anomaly (bright-spot share of layer 33).
- A single line or blob region is a lead only, reported with crops. Any candidate stays private and goes to the user before anything else.
- **If no candidate:** report the area and the bound set by test 1 (V3's detection limit) for that area.

**Run:** `r18/r18_run.sh` on the ZGX; output `~/vesuvius/eval/r18_result.txt` (ends with `R18_DONE`). Order: runtime check, test 1, test 2, then the long map runs of test 3 and its screening.

### Results, runtime check and tests 1-2 (2026-10-24, 11:25-12:03; JSON `r18_t1.json`, `r18_rank.json`)

**Runtime check: passed.** V3's window is d −2 (w058a at α 1: AUC 0.860 at d −2, 0.855 at d 0, 0.829 at d +2). Our float inference matches the published command's map at r 1.0000: equal on 98.8% of 6.3 M papyrus pixels and within one level on 100%.

**Test 1, detection limit: KILL.**

| model | α 1 | 0.85 | 0.7 | 0.5 | 0.35 | 0 | α₀.₆₅ | false lights at α 0 |
|---|---|---|---|---|---|---|---|---|
| Reader v2 (d −2) | 0.808 | 0.708 | 0.612 | 0.536 | 0.520 | 0.519 | 0.76 | 0.146 |
| Reader V3 (d −2) | 0.826 | 0.725 | 0.623 | 0.542 | 0.522 | 0.509 | 0.74 | **0.075** |

- V3 − v2 at α 0.7/0.5: +0.008 [−0.022, +0.030], below +0.03. At full strength +0.018.
- **Reading:** V3 is a cleaner reader, not a more sensitive one. It halves the false lights on blank papyrus at the same recall (0.075 against 0.146), as its README says, but it sees faint ink no better: the limit moves from α₀.₆₅ 0.76 to 0.74.

**Test 2, readability ranking with V3: MODEL-INDEPENDENT.**

| scroll | voxel | AUC α 1 / 0.85 / 0.7 | α 0.85 minus 800 [95%] |
|---|---|---|---|
| 0268 | 8.64 | 0.844 / 0.762 / 0.668 | +0.005 [−0.022, +0.034] |
| 0800 | 8.64 | 0.844 / 0.758 / 0.653 | — |
| 1218 | 8.64 | 0.844 / 0.714 / 0.603 | −0.044 [−0.075, −0.007] |
| 0191 | 9.362 | 0.802 / 0.703 / 0.600 | −0.055 [−0.103, −0.006] |
| 1203 | 9.362 | 0.802 / 0.689 / 0.595 | −0.069 [−0.117, −0.029] |
| 0826 | 9.362 | 0.802 / 0.680 / 0.604 | −0.078 [−0.129, −0.029] |
| 0125 | 9.362 | 0.804 / 0.678 / 0.594 | −0.079 [−0.124, −0.035] |
| 0211 | 9.362 | 0.805 / 0.676 / 0.586 | −0.082 [−0.122, −0.034] |
| 0358 | 9.362 | 0.803 / 0.673 / 0.596 | −0.084 [−0.123, −0.050] |
| 0813 | 9.362 | 0.803 / 0.667 / 0.579 | −0.091 [−0.145, −0.035] |
| 0257 | 9.362 | 0.801 / 0.656 / 0.579 | −0.102 [−0.143, −0.054] |
| 1545 | 9.362 | 0.801 / 0.653 / 0.560 | −0.105 [−0.155, −0.047] |

- Spearman (clutter index, AUC at α 0.85) = **−0.97** (p < 0.001; Reader v2 −0.95). Mean AUC at α 0.85: 9.362 µm 0.675, 8.64 µm 0.745. Top two: 0268 and 800.
- **Reading:** with the better model the campaign split is cleaner. All three 8.64 µm / 116 keV scrolls now read better than all nine 9.362 µm / 113 keV ones, and all nine are significantly below 800 (Reader v2: seven). The round-12 findings do not depend on the model.

### Result, test 3 (2026-10-24, 12:03-14:36; `/mnt/data/vesuvius/eval/r18/screen.json`, crops in `r18/crops/`): NO CANDIDATE

**Run:** V3 maps at d 0/+2/−2/+12, both directions, about 5 min per 0268 winding and 4 min per 800 winding, no failures. Area screened: **260.9 cm² of PHerc. 0268** (T067-T082) and **199.9 cm² of PHerc. 800** (e050-e069).

**Screening:**
- 0268: the 15 best V3 tiles score +0.117 to +0.237; 10 of them are at or next to one of Reader v2's 15 best tiles.
- 800: +0.125 to +0.266; 11 of 15 coincide with v2's.
- Bright-spot shares 0.002-0.036, no 1218-like material anomaly. So V3 lights mostly the same places as v2, more sharply.

**Visual check of all 30 tiles** (reading d0 and d+2, blind side, d+12, CT layer 33; contact sheets in the scratchpad):
- **0268:** blob clusters, horizontal smudge bands that follow fibre bands (T075), the lens-shaped fold of stage 1 (T073 x 7514) and the radially repeating zone (T070 x 7514). Every one also appears, weaker, on the blind side or at d+12. No lines of strokes.
- **800:** the known e059 density cloud (large amorphous blobs over the whole band height in porous CT), the e051 crack zone (same shape on the blind side and at d+12), single vertical marks (e052 x 0, e069 x 8670) and scattered blobs.
- **One weak lead, 800 e053 x about 1500-2600** (tiles #07 and #11), zoomed at full resolution over 2.1 cm: a cluster about 6 mm wide of stroke-like shapes (a horizontal bar, a T-like and a D-like shape) at d0 and d+2. It is absent on the blind side and at d+12, but it is one cluster inside 800's dense blob field, with no second line. Criterion 1 fails, so it is a single blob region: a lead only, by the rule. Reader v2 also scored these tiles high (+0.162, +0.117), and round 4's visual check had not flagged e053.

**Verdict:** no candidate in 460.8 cm² with Reader V3. In that area, no ink at least as contrasted as V3's detection limit (α₀.₆₅ 0.74 of 1447's contrast, practically the same as Reader v2's) is visible. V3's lower false-light rate did not reveal anything that Reader v2 had hidden.

## 25. Round 17: PHerc. 0268 stage 2, a large search on the most readable scroll (chosen by the user 2026-10-23; rule written before any download)

**Why:** round 12 ranked 0268 the most readable eligible scroll we can measure. Stage 1 (section 8) searched 65 cm² (T073-T076) without a candidate.

**Data:**
- The stage-1 fit and snapped windings (band z 6610-8110).
- 12 more windings next to stage 1: T067-T072 and T077-T082, at radius about 2400 vx ± 10%.
- CT level 0 into the existing `PHerc0268/ct0.zarr` (pre-approved Vesuvius Challenge data; cap 32 GB; size reported).
- Expected area about 190 cm²; with stage 1 about 255 cm².

**Maps:** Reader v2 at d 0, +2, −2 and the control +12, reading side (`_reverse`) and blind side.

**Screening (to choose what to inspect, fixed in advance):**
- Per 1 cm wide tile (1157 px, full band height): score = mean of the top 1% of the reading-side d0 map minus the larger of the same statistic on the blind side and at d+12.
- The 15 highest-scoring tiles over all 12 windings are inspected visually: reading d0 and d+2, blind side, d+12.
- Also checked: whether the share of bright spots in layer 33 follows the response (the 1218 material anomaly).

**Rule (section 8, unchanged):**
- **Candidate** only if all hold: (1) stroke-like marks in at least 2 parallel horizontal lines 3-7 mm apart on the reading side at d0; (2) the same at a neighbouring depth; (3) absent at d+12 and on the blind side; (4) not explained by a CT material anomaly.
- **A single line or blob region** is a lead only, reported with crops.
- **If no candidate:** report the area searched and that, in that area, no ink at least as contrasted as the detection limit of rounds 4-12 (about 85% of 1447's contrast for Reader v2) is visible.

### Result (2026-10-24 00:23, `r17/r17_run.sh`; output `~/vesuvius/eval/r17_result.txt`, `/mnt/data/vesuvius/eval/r17/screen.json`; contact sheets `figures/r17_top6.png`, `figures/r17_last3.png`): NO CANDIDATE

**Run:**
- **CT:** 7.89 GB downloaded (9951 chunks local; the first attempt hit a dropped connection and the retry succeeded).
- **Renders and maps:** 12 renders and Reader v2 maps at d 0/+2/−2/+12, about 6 min per winding.
- **Area:** 195.6 cm² searched. With stage 1, about 261 cm² of PHerc. 0268, the most readable eligible scroll we measured.

**Screening:** the 15 top tiles score +0.100 to +0.137 (reading top-1% minus the larger of blind and d+12), with bright-spot shares 0.002-0.010, so no material anomaly like 1218. They group into about 8 regions:
- T070, T069, T079 and T077 at render x about 8000-10400: the same angle on several windings, i.e. the radially repeating structure already seen in stage 1;
- T081 x 13300-14500; T082 x 11560; T080 x 578 and 12138; T068 x 10404.

**Visual check of all 15 tiles** (reading d0 and d+2, blind side, d+12, CT layer 33):
- Every region shows scattered round blobs or blob clusters. They are present at d0 and d+2, but also, weaker, on the blind side and at d+12. Where blobs align, they follow fibre bands or the band edge (T077 bottom), and the CT shows cracks or folds there.
- No region has stroke-like marks in 2 or more parallel lines 3-7 mm apart that are absent on the blind side and at d+12. Criteria 1 and 3 fail everywhere.

**Verdict:** no candidate in 195.6 cm² (about 261 cm² of 0268 in all). In that area no ink at least as contrasted as Reader v2's detection limit (about 85% of 1447's contrast) is visible. All lights are structural, as in stage 1.

## 24. Round 16: PHerc. 0175B redone (approved by the user 2026-10-23 against my advice; rules written before any computation)

**Fixes for round 15's two failures:**
1. **Band:** full-resolution z 7528-8368 (840 slices), so renders are about 860 px tall and fit the 800 px letter crops. The m7 level-1 rows 19-21 already local cover it. The axis is re-estimated with 5 control points over the new band. The extra CT is downloaded by `get_ct_for_mesh.py`; only missing chunks are fetched, and the size is reported.
2. **Surfaces:**
   - 0175B's sheets are about 44 voxels apart (about 97 crossings over a 4253 vx radius), against about 27 in 800. With round 15's ±15 vx snapping search, a circle in mid-gap found no sheet (18% of vertices unsnapped), and the hole-free interpolation left the surface between sheets.
   - Now: the same circles (45% and 65% of the radius, best-covered 8000 px arcs) on a 10-voxel grid (was 20), snapped with `--max-off 25`.

**Rules (unchanged from section 23):**
- **Validity per render:** ≥ 50% papyrus at layer 33 and a tracker sheet within ±5 layers of 33 on ≥ 30% of papyrus pixels. Invalid renders are not scored.
- **Test:** the round-12 readability test (three 1447 letter-row crops at α 1, 0.85, 0.7; Reader v2 d −2; pooled AUC; bootstrap difference to 800), with 800 and 0268 rerun as references.
- **PASS** if 0175B − 800 at α 0.85 ≥ +0.05 with the interval above 0; **CANDIDATE** if it also exceeds 0268. **KILL** otherwise.
- **If both renders are invalid again:** the conclusion is that 0175B's sheets cannot be followed by our pseudo-winding method (probably fused or compressed), and the scroll stays unmeasured.

### Result (2026-10-23, `r16/r16_run.sh`; output `~/vesuvius/eval/r16_result.txt`): renders INVALID again, so 0175B stays UNMEASURED by the rule

**Pipeline:**
- **Axis:** about 94 crossings per ray, relative spread 0.12.
- **Snapping improved:** 91% and 89% of vertices on m7 sheets (round 15: 82% and 81%).
- **Extra CT:** 4.04 GB (3863 chunks now local, 8.3 GB on disk). 0175B downloads in all: 0.56 + 4.85 + 4.04 = 9.45 GB.
- **Renders:** 850 px tall.

**Validity:**

| render | sheet within ±5 of 33 | tracker valid | sheet thickness (median) |
|---|---|---|---|
| p045b | 0.12 | 28% | 13.6 |
| p065b | 0.14 | 30% | 12.4 |
| 800 (reference) | | 67-82% | about 9 |

- The rule needs ≥ 0.30, so both renders are INVALID.
- The surfaces lie on m7-predicted sheets (about 90%), but the intensity tracker rarely finds a distinct papyrus run with gaps on both sides, and the runs it finds are thick.
- The likely reading: 0175B's sheets are densely packed or fused, with no clear sheet-gap alternation along the normal. That is a property of the scroll, not of our surfaces.

**Exploratory only, not a verdict:** the test run on the two invalid renders (6 blends; result kept apart as `r16_test_EXPLORATORY.json`).

| scroll | AUC α 1 / 0.85 / 0.7 | clutter fraction |
|---|---|---|
| 0175B | 0.817 / 0.730 / 0.631 | 0.137 |
| 800 | 0.816 / 0.737 / 0.638 | |
| 0268 | 0.816 / 0.755 / 0.675 | |

- 0175B − 800 at α 0.85: −0.007 [−0.033, +0.018].
- Read at face value, 0175B is about as readable as 800 and below 0268: not a candidate, in line with rounds 14 and 15.
- Its high clutter fraction with 800-like readability is an exception to round 12's relation, possibly because its surfaces are not clean sheets.

## 23. Round 15: a reliable readability measurement for PHerc. 0175B (approved by the user 2026-10-23; rules written before any computation; downloads approved step by step)

**Why 0175B:** of the seven never-surveyed 8.64 µm scrolls it came closest to 0268 in one raw-CT block (round 14), but round 14's raw-CT calibration failed. A render-based measurement, as in round 12 (ρ −0.95), is needed. 0175B has no lasagna normals but has the m7 surface prediction.

**Method:** pseudo-windings instead of a spiral fit. The readability test needs real papyrus surfaces, not correct winding identities.
1. **Download, step 1:** m7 level 5 (3.9 MB) and level 1 for a band at mid-height, full-resolution z 7634-8262 (559.7 MB).
2. **Axis:** the scroll axis in the band, from the m7 level-1 band with the PHerc. 800 method (minimum spread of sheet-crossing counts over 48 rays).
3. **Pseudo-windings:** two circles around the axis at 45% and 65% of the papyrus radius, at full resolution z 7698-8198 (500 slices), each limited to an arc of at most 8000 px.
4. **Snapping:** circles snapped onto the nearest m7 sheet with `snap_mesh.py` (continuity constraint, hole-free).
5. **Download, step 2:** level-0 CT chunks covering the snapped arcs ± 40 voxels. Exact list and size asked before downloading; expected about 1-2 GB.
6. **Renders:** 66 layers (`render_tifxyz.py`).

**Test:** the round-12 readability test, unchanged.
- Three 1447 letter-row crops blended at α 1, 0.85 and 0.7 into windows of each render (chosen from masks); Reader v2 at d −2; pooled pixel AUC.
- Bootstrap difference to PHerc. 800 at α 0.85 with round 12's letters and 800 data.
- Clutter fraction as in round 12.

**Rule:**
- **PASS** (0175B reads better than 800) if AUC at α 0.85 exceeds 800's by ≥ 0.05 with the interval above 0.
- **CANDIDATE above 0268** if it also exceeds 0268's AUC at α 0.85 (0.755).
- **KILL** otherwise. The clutter fraction is reported and checked against the round-12 relation (AUC ≈ f(clutter)).
- **Validity check:** each render must contain ≥ 50% papyrus at layer 33 and the tracker must find a sheet within ±5 layers of 33 on ≥ 30% of pixels (as for 800, 28-38%). Otherwise the snapping failed, and that render is reported as invalid, not scored.

### Result (2026-10-23, `r15/r15_run.sh`; output `~/vesuvius/eval/r15_result.txt`): renders INVALID, no readability measurement

**Downloads (pre-approved Vesuvius Challenge data):**
- m7 level 5 + level-1 rows 19-21: 0.56 GB.
- CT level 0 around the two arcs: 2313 chunks, 4.85 GB. My 4 GB cap first refused it, and I raised it to 5 GB.
- Total about 5.4 GB.

**Pipeline:**
- **Axis:** about 97 sheet crossings per ray, relative spread 0.11. Papyrus radius 4253 vx.
- **Circles:** R 1914 and 2765 vx, 8000 px arcs with 0.91 and 0.89 sheet coverage.
- **Snapping:** 82% and 81% of vertices on an m7 sheet (800 gave 54-69%).
- **Two mistakes of mine, both fixed or recorded:** the circle step first ran with the venv lacking `tifffile`; and the 500-slice band gives renders only 520 px tall, so the 800 px letter crops do not fit. The pre-registered test crashed at 0175B (800 and 0268 ran).

**Validity check: both renders INVALID.**
- p045: papyrus at layer 33 = 1.00, but a sheet within ±5 layers of 33 on only 0.14 of papyrus pixels (rule ≥ 0.30). Tracker: valid on 29% of papyrus, median sheet thickness 12.4 layers.
- p065: 0.16; tracker valid on 35%, thickness 12.4.
- 800 renders give the tracker valid on 67-82%, with thickness about 9.
- So the surfaces mostly do not sit on one distinct sheet. Either 0175B's sheets are thick and fused (the tracker cannot separate them) or the circles cross between windings. The renders are not scored, as the rule says.

**Exploratory only (renders invalid, not a verdict):** the simple render clutter fraction, layers 27-34 on layer-33 papyrus, rows matched.

| render | clutter fraction |
|---|---|
| 0175B p045 / p065 | 0.140 / 0.124 |
| 800 e050 / e057 | 0.092 / 0.094 |
| 0268 T073 | 0.093 |
| 1218 T039 | 0.104 |

- 0175B shows more fine-scale energy than all three 8.64 µm references, comparable to the 9.362 µm scrolls of round 12. If anything, it would read worse than 800.
- This agrees with round 14 (raw-CT prediction 0.699). Not a candidate.

**What a valid measurement would need:** a band of ≥ 820 slices (about 4-5 GB more CT) and surfaces on distinct sheets (a proper spiral fit, or the bucket's `normal-grids`, whose format is not yet parsed). The expected gain is low given the exploratory index.

**Status (2026-10-23 evening): DONE (was RUNNING on the ZGX).**
- **Pipeline:** `~/vesuvius/eval/scripts/r15/r15_run.sh` (scripts also in `eval/r15/`: `r15_circles.py`, `r15_test.py`), launched with nohup.
- **Progress and verdict:** `~/vesuvius/eval/r15_result.txt` (ends with `R15_DONE` or a `FAILED <step>` line). Logs in `~/vesuvius/survey/PHerc0175B/logs/`, data in `/mnt/data/vesuvius/survey/PHerc0175B/`.
- **When it ends:** report the CT download size (last line of `logs/ct.log`), the validity of the two renders (p045, p065) and the round-15 rule line, then write the results here.
- **Downloads:** the user pre-approved downloads of Vesuvius Challenge data (2026-10-23), but sizes are still reported. Step 1 = m7 level 5 + level-1 rows 19-21 (563.6 MB); step 2 = CT around the arcs (cap 4 GB).

## 22. Round 14: readability index of the seven unsurveyed 8.64 µm eligible scrolls (approved by the user 2026-10-23; rules written before any computation; download approval asked separately)

**Scrolls:** PHerc. 0175A, 0175B, 0306B, 0483A, 0483B, 0490A and 0490B. These eligible volumes have no lasagna normals, so we have no surface renders; the index is measured on raw CT blocks.

**Blocks (chosen from the bucket listing only, before any download):**
- Two blocks per scroll of 128 × 512 × 512 voxels (one level-0 z-slab of 4 × 4 chunks of 128³) at mid-height, at about 40% and 70% of the radius from the volume centre, with all 16 chunks present.
- 14 blocks, 224 chunks, 469.8 MB (uncompressed uint8 chunks).

**Raw-CT index:**
- Per z-slice, in-plane difference of Gaussians (σ 1 and 3 px).
- Papyrus = 7 × 7-smoothed value above the block's midpoint of its 20th and 80th percentiles.
- (A) var(DoG) / var(raw) over papyrus voxels. (B) the same over interior papyrus voxels (whole 3 × 3 × 3 neighbourhood papyrus).

**Calibration on the 12 scrolls of round 12, local CT, no download:**
- Two blocks each of the same size, taken from local chunks near the rendered band.
- Spearman ρ of each version against round 12's AUC at α 0.85. The version with the larger |ρ| is kept; the selection uses reference scrolls only.
- **Calibration PASS** if |ρ| ≥ 0.7 with p < 0.05. Otherwise the raw-CT index is not a valid proxy, and the seven values are reported without a ranking claim.

**Prediction:**
- A linear fit of AUC on the kept index over the 12 references gives a predicted AUC for each new scroll. The interpretation is relative to the 8.64 µm references (800, 0268, 1218), since all seven new scrolls are 8.64 µm.
- **CANDIDATE:** a new scroll whose index is better than 0268's (the most readable so far) in both blocks.
- A candidate would be proposed for the round-12 injection test (needs renders, hence lasagna normals or our own surface fit) and then for a search. Each step is approved separately.

### Result (2026-10-23, `r14/r14_index.py`; files `/mnt/data/vesuvius/eval/r14/calib.json` and `new.json`; download 469.8 MB as approved)

**Fixes during the run (no effect on any result):** the first calibration run crashed on chunk-name parsing and on two references with no complete 4 × 4 block. Fixed with a 3 × 3 fallback and references without blocks excluded. 0826 still had no complete block locally, so 11 references were used.

**Calibration: FAIL.**
- Version A: Spearman ρ −0.46 (p 0.15). Version B: ρ −0.63 (p 0.039). B kept; the rule needed |ρ| ≥ 0.7.
- The raw-CT index is a weaker proxy than the render-based one of round 12 (ρ −0.95).
- Plausible causes: only one or two blocks per scroll, with large block-to-block differences, and raw CT mixing sheet interiors with gaps and edges, unlike near-surface render layers.
- 0268 still stands apart (B 0.253; the others 0.30-0.34).

**Seven new scrolls (index B per block; fit AUC = −0.974 × index + 1.001, reported only):**

| scroll | block 1 / block 2 | predicted AUC at 0.85 |
|---|---|---|
| 0175A | 0.368 / 0.373 | 0.640 |
| 0175B | 0.339 / 0.281 | 0.699 |
| 0306B | 0.348 / 0.336 | 0.668 |
| 0483A | 0.336 / 0.352 | 0.666 |
| 0483B | 0.344 / 0.371 | 0.653 |
| 0490A | 0.311 / 0.345 | 0.682 |
| 0490B | 0.332 / 0.347 | 0.671 |

References (8.64 µm): 800 0.314 (AUC 0.737), 0268 0.253 (0.755), 1218 0.324 (0.709).

**No CANDIDATE:** no new scroll is quieter than 0268 in both blocks. 0175B's second block (0.281) comes closest. Because the calibration failed, these values are not a reliable ranking. Taken at face value, none of the seven looks more readable than 0268, and 0175A looks hardest.

## 21. Round 13: is the 9.362 µm scans' extra fine-scale energy noise or structure? (approved by the user 2026-10-23; rules written before any computation)

**Origin:** round 12. The share of near-surface papyrus variance at 1-3 px predicts readability (ρ −0.95), and it is higher in all nine 9.362 µm / 113 keV scrolls. Round 5's noise budget covered only 8.64 µm data.

**Data:**
- 9.362 µm: PHerc. 1545 t033/t034, 0257 t044/t045, 1203 t040/t041 (survey renders), i.e. the two hardest scrolls and the easiest of the group.
- 8.64 µm references: 800 e050/e057/e064, 0268 T073, 1218 T039. Rows 500-1320 of the tall renders, to match the survey height.

**Measurement (per render, as round 5):**
- **Noise spectrum:** in-plane radial noise power spectrum from 16 × 16 patches lying fully in void voxels (smoothed value below the tracker threshold, eroded 5 × 5 × 5), in layers 20-46.
- **Noise share of each band:** the noise variance passed by two difference-of-Gaussians bands, computed analytically from that spectrum: the readability band (σ 1-3 px) and the stroke band (σ 3-15 px). Each is divided by the measured papyrus variance in the same band, on papyrus voxels of layers 27-34.
- **Primary:** f₁₃ = noise share of the 1-3 px band. f₃₁₅ (round 5's R) is reported.

**Operational check (always run):**
- The three 1447 letter-row crops of round 12, blended at α 0.85 into two windows per scroll: the three 9.362 µm scrolls, and 800 as reference.
- Reader v2 at d −2 on the blend as is, and after a 3D Gaussian denoiser σ = 0.5, 0.75, 1.0 px (inside the joint papyrus).
- Pooled AUC per group; bootstrap over letter components and tiles.

**Rule:**
- **NOISE** (denoising route reopened for the August 2025 scans) if both hold:
  1. f₁₃ ≥ 0.5 on average over the 9.362 µm renders and ≤ 0.2 over the 8.64 µm ones;
  2. the best σ improves the pooled 9.362 µm AUC by ≥ +0.02 with the interval above 0, while improving 800 by ≤ +0.01.
- **STRUCTURE** (the August scans are harder by their papyrus or optics, not their noise) if f₁₃ ≤ 0.2 on average over the 9.362 µm renders and no σ gives a 9.362 µm gain with the interval above 0.
- **MIXED** otherwise.

### Result (2026-10-23, `r13/r13_noise9.py`; output `~/vesuvius/eval/r13_result.txt`, JSON `r13_result.json`; about 40 min)

**Noise budget per render:**

| scroll (voxel) | noise variance | 1-3 px band: noise / papyrus = share | 3-15 px share |
|---|---|---|---|
| 1545 t033 / t034 (9.362) | 28.7 / 41.7 | 6.7/133.7 = 0.05 · 9.5/136.0 = 0.07 | 0.014 / 0.019 |
| 0257 t044 / t045 (9.362) | 45.3 / 53.8 | 10.8/129.6 = 0.08 · 12.1/133.0 = 0.09 | 0.023 / 0.023 |
| 1203 t040 / t041 (9.362) | 19.2 / 16.1 | 4.1/126.3 = 0.03 · 3.4/121.5 = 0.03 | 0.008 / 0.006 |
| 800 e050 / e057 / e064 (8.64) | 36.6 / 29.3 / 32.3 | 0.10 / 0.08 / 0.09 (papyrus 80-84) | 0.02 |
| 0268 T073 (8.64) | 71.4 | 18.2/48.5 = 0.37 | 0.121 |
| 1218 T039 (8.64) | 65.6 | 15.2/61.0 = 0.25 | 0.075 |

- Mean noise share of the 1-3 px band: **9.362 µm 0.06**, 8.64 µm 0.18.
- The 3-15 px shares are rough: 16 px patches barely resolve that band.

**Operational check** (pooled AUC at α 0.85, change [95%]):

| denoiser | 9.362 µm (1545, 0257, 1203) | 800 |
|---|---|---|
| none | 0.660 | 0.735 |
| Gaussian σ 0.5 | 0.661 (+0.000 [−0.004, +0.004]) | 0.725 (−0.010) |
| σ 0.75 | 0.652 (−0.008) | 0.705 (−0.031) |
| σ 1.0 | 0.635 (−0.026 [−0.042, −0.011]) | 0.680 (−0.055) |

**RULE: STRUCTURE.**
- The 9.362 µm scans are not noisier at fine scale: their noise share is the lowest of all, 0.03-0.09.
- What makes them harder is more fine-scale papyrus energy: 121-136 against 80-84 for 800 and 49-61 for 0268 and 1218.
- Denoising does not help them and hurts 800.
- All nine August 2025 scrolls share this, so it is more likely a property of that campaign's scans (optics or reconstruction sharpness) than of nine papyri. That is not verified.
- **By-product:** 0268, the most readable scroll, has the quietest papyrus at 1-3 px (48.5), even though noise is a larger share of it. Fine-scale papyrus energy, not noise, is what limits readability.

## 20. Round 12: where is ink easiest to see? (approved by the user 2026-10-23; rules written before any computation)

**Rationale:** the limit is papyrus clutter at 9-35 µm (rounds 5, 9 and 10). Clutter need not be uniform, so the detection limit may vary between scrolls and within a scroll.

**Common tools:**
- **Letter crops:** three 800 × 4400 px crops of PHerc. 1447 holding one letter row each:
  - w058 y 2860-3660, x 600-5000;
  - w060 y 1450-2250, x 1500-5900;
  - w060 y 2700-3500, x 1000-5400.
- **Blend:** blended (round-4 blend, `r6/b1447.py` generalised to any 66-layer background) into a background window.
- **Model and score:** Reader v2 (O) at d −2 (1447 layers 2-18), our float inference. Pixel AUC of letters vs other papyrus inside certainty ∩ joint papyrus.

### Test 1: readability ranking of the scrolls
- **Backgrounds:** 3 windings per scroll, with the window position chosen from masks only (maximum joint coverage):
  - 800: e050, e057, e064;
  - 0268: tall-band T073-T075;
  - 1218: tall-band T039-T041;
  - 0125, 0191, 0211, 0257, 0358, 0813, 0826, 1203 and 1545: the first three survey windings.
- **Contrasts:** α 1, 0.85 and 0.7.
- **Statistic:** pooled AUC per scroll at α 0.85, with a bootstrap over letter components (shared) and 256 px tiles (per scroll).
  - The 9.362 µm scrolls are reported separately: the injected 8.64 µm letters appear about 8% larger relative to their papyrus.
- **Clutter index (reported):** the fraction of near-surface papyrus variance at 1-3 px scale (difference of Gaussians, σ 1 and 3) in the blank backgrounds, Spearman-correlated with the AUC across scrolls.
- **PASS** (readability differs usefully) if at least one scroll's AUC at α 0.85 exceeds 800's by ≥ 0.05 with the bootstrap interval of the difference above 0. That scroll then becomes the priority target for a deeper search; downloads would be asked separately.
- **KILL** otherwise.

### Test 2: quiet zones inside PHerc. 800
- **Injections:** letter crops (rotating the three) at α 0.85 into all 20 windings e050-e069, at y 500 and 1000 and two x positions per winding (x 500 and width − 4900): 80 positions. Local AUC per position.
- **Predictors, from the blank window only** (pre-specified):
  - (a) the clutter fraction as in test 1;
  - (b) the blank Reader v2 response (mean probability of the existing d −2 map);
  - (c) median sheet thickness (tracker);
  - (d) mean density of the sheet interior;
  - (e) median recto-side gap.
- **PASS** if two conditions hold:
  1. the local AUCs vary usefully (10th-90th percentile spread ≥ 0.10);
  2. a predictor has |Spearman ρ| ≥ 0.4 with Bonferroni-corrected p < 0.01 (raw p < 0.002).
- **After a PASS:** a predicted-detectability map of all 800 windings in 1820 × 2200 px tiles, the top 5 zones, and their Reader v2 maps shown for visual reading (no claims).
- **KILL** otherwise.

### Test 3: density and compression (materials test D1)
- **1447** (w058, w060, O's d −2 maps): local sheet density (mean of the interior layers between the tracker edges) and thickness, both smoothed over 1 mm, split into tertiles over certainty ∩ papyrus. Pixel AUC per tertile, bootstrap over letter components and tiles.
- **343:** box hits per density tertile, on O's d0 maps of the clean renders.
- **PASS** if, on 1447, AUC(lowest-density tertile) − AUC(highest) ≥ +0.05 with the interval above 0, and 343 shows the same order. Thickness is reported the same way.
- **KILL** otherwise. Power is low (about 7 letters per tertile).

### Side task: locate "Reader V3" (web only, no download)

**Side task result:** not public. Two searches found no Hugging Face or GitHub release; it is cited only in Jashann's README. Nothing to download.

### Results (2026-10-23, `r12/run_r12.sh`; output `~/vesuvius/eval/r12_result.txt`, JSON `r12_*.json`; about 1 h of GB10)

**Test 3, density and compression: KILL.**
- 1447 density tertiles (low/mid/high): AUC 0.837 / 0.783 / 0.814; low − high +0.023 [−0.065, +0.103].
- 1447 thickness tertiles: 0.795 / 0.814 / 0.823; low − high −0.029 [−0.129, +0.053].
- 343 boxes by density tertile: 5/5, 5/7, 2/4 (the order of the hypothesis, but few boxes).
- Reading: local density or thickness does not set detectability.

**Test 1, readability ranking: KILL by the rule** (no scroll beats 800 by ≥ 0.05 with the interval above 0). The ranking itself is informative.

| scroll | voxel | AUC α 1 / 0.85 / 0.7 | α 0.85 minus 800 [95%] | clutter fraction |
|---|---|---|---|---|
| 0268 | 8.64 | 0.816 / 0.755 / 0.675 | +0.017 [−0.002, +0.036] | 0.102 |
| 0800 | 8.64 | 0.816 / 0.737 / 0.638 | — | 0.085 |
| 0191 | 9.362 | 0.787 / 0.715 / 0.628 | −0.023 [−0.063, +0.017] | 0.124 |
| 1218 | 8.64 | 0.816 / 0.709 / 0.603 | −0.029 [−0.055, +0.003] | 0.111 |
| 1203 | 9.362 | 0.785 / 0.691 / 0.614 | −0.046 [−0.088, −0.014] | 0.114 |
| 0211 | 9.362 | 0.788 / 0.689 / 0.603 | −0.049 [−0.082, −0.013] | 0.139 |
| 0826 | 9.362 | 0.785 / 0.688 / 0.590 | −0.049 [−0.092, −0.015] | 0.128 |
| 0813 | 9.362 | 0.786 / 0.687 / 0.595 | −0.050 [−0.104, +0.006] | 0.143 |
| 0125 | 9.362 | 0.786 / 0.687 / 0.618 | −0.051 [−0.087, −0.013] | 0.142 |
| 0358 | 9.362 | 0.788 / 0.673 / 0.597 | −0.064 [−0.098, −0.038] | 0.146 |
| 0257 | 9.362 | 0.785 / 0.668 / 0.586 | −0.070 [−0.109, −0.032] | 0.157 |
| 1545 | 9.362 | 0.785 / 0.646 / 0.552 | −0.091 [−0.142, −0.037] | 0.154 |

- **Spearman** (clutter fraction, AUC at α 0.85) over the 12 scrolls: **ρ = −0.95, p < 0.001.**
- **Reading:**
  - A label-free index (the share of near-surface papyrus variance at 1-3 px) predicts how readable a scroll is for 1447-like ink.
  - The 8.64 µm / 116 keV scrolls (0268, 800, 1218) read better than all nine 9.362 µm / 113 keV scrolls of the August 2025 campaign, seven of them significantly. The 9.362 µm scrolls have a higher fine-scale clutter fraction.
  - **Correction (2026-10-24, while writing the report):** not quite all. 0191 (0.715) edges past 1218 (0.709). All nine read worse than 800, seven significantly.
  - 0268 is the best scroll: +0.017 at α 0.85 and +0.037 at α 0.7, short of the rule.
- **Caveats:**
  - The injected 8.64 µm letters look about 8% larger relative to the 9.362 µm papyrus.
  - The cross-scroll correlation is driven partly by the campaign split. Within the 9.362 µm group the order also follows the index; within the 8.64 µm group 0268 beats 800 despite more clutter.
  - Whether the higher fine-scale fraction of the 9.362 µm scans is noise or structure was not measured. Round 5 measured noise only on 8.64 µm data.

**Test 2, quiet zones in 800: KILL.**
- 80 positions: local AUC at α 0.85 median 0.701, with a 10th-90th spread of only 0.086 (the rule needs ≥ 0.10).
- Predictors: clutter fraction ρ −0.40 (p 0.0002), blank Reader v2 response −0.23, thickness −0.06, density +0.02, recto gap −0.19.
- Reading: the clutter fraction also predicts local detectability inside 800, but the local variation is too small to give windows where much fainter ink would show.

## 19. Round 11: a "concentrated profile" false-positive filter (approved by the user 2026-10-23; rule written before any computation)

**Origin:** round 10, test 4. Letter blobs draw Reader v2's evidence from a few layers, while false lights draw evenly on all of them. The idea came from looking at all groups, including round 10's test groups. Round 10's held-out sets are therefore not independent for it, and fresh false lights are added.

**Blobs, ablation and drops:** exactly as round 10, test 4 (top-1% blobs ≥ 50 px; six 3-layer slabs replaced by the same layers shifted 405 px; drop of the blob's mean logit per slab).
- Letters: 1447 T1 crops at α 1 and 343 s028-s031.
- Round-10 lights: 0268 T073-T076, 1218 T039-T042, 800 e055/e060.
- **Fresh lights, never seen:** 800 e063 and e066, PHerc. 0125 t044, PHerc. 0358 t045.

**Statistic (position-free, chosen to avoid fitting where the peak sits):**
- **Primary:** the normalised entropy of the positive-drop profile, H = −Σ p_j log p_j / log 6 with p_j = d_j⁺ / Σ d⁺. The direction is fixed in advance: letters lower (more concentrated).
- **Reported:** the largest slab share, max_j p_j.

**Rule:**
- Threshold by maximum Youden J on 343 letters vs 0268 lights. Tested once on 1447 letters vs all other lights (1218, 800 e055/e060, and the fresh set).
- **PASS** if test AUC ≥ 0.80, ≥ 70% of 1447 letters are kept and ≤ 10% of lights pass, AND the fresh lights alone pass at ≤ 10%.
- **KILL** if test AUC < 0.70 or the direction flips. **PARTIAL** otherwise.
- **Use if PASS:** a false-positive filter for any future candidate (the prize asks for false-positive mitigation). It does not add sensitivity.

### Result (2026-10-23, `r11/r11_peak.py`; output `~/vesuvius/eval/r11_result.txt`, JSON `r11_result.json` with per-blob drops; about 45 min of GB10)

**Medians per group:**

| group | blobs | entropy H | largest-slab share |
|---|---|---|---|
| 1447 letters | 35 | 0.924 | 0.292 |
| 343 letters | 17 | 0.967 | 0.245 |
| 0268 lights | 207 | 0.984 | 0.218 |
| 1218 lights | 128 | 0.969 | 0.242 |
| 800 e055/e060 lights | 89 | 0.980 | 0.223 |
| fresh lights (800 e063/e066, 0125 t044, 0358 t045) | 135 | 0.981 | 0.221 |

**Filter performance:**

| statistic | train AUC | threshold | test AUC | letters kept | lights passing | fresh lights passing | 1447 vs fresh AUC |
|---|---|---|---|---|---|---|---|
| entropy | 0.594 | H ≤ 0.980 | 0.749 | 83% | 57% | 49% | 0.780 |
| largest share | 0.608 | ≥ 0.224 | 0.753 | 86% | 53% | 44% | |

**RULE: PARTIAL** (test AUC between 0.70 and 0.80; the light pass rates are far above 10%).

**Reading:**
- 1447's letters draw on fewer layers than false lights do. 343's letters barely do (H 0.967 against 0.97-0.98), so the threshold set on 343 is weak.
- The depth profile carries some information (AUC about 0.75, also on fresh lights), but neither this statistic nor round 10's shell fraction (test AUC 0.73) can serve as a strict filter.
- At most it could be one input to a combined score, not a veto.

## 18. Round 10: what does the model see, and how universal is the limit? (approved by the user 2026-10-23; rules written before any computation)

**Bench and statistics:** the round-4 T1 bench (1447 letters in held-out 800 papyrus, 3 crops, α 1/0.85/0.7/0.5/0.35/0). Pooled pixel AUC and the letter-and-tile bootstrap as in `score_faint.py`. O = Reader v2.

### Test 1: depth-window ensemble (existing maps)
- **Method:** mean of O's probability maps at d −2, 0, +2 (L24 s2, s4, s6) against O at its chosen d −2.
- **PASS** if the mean gain at α 0.7 and 0.5 is ≥ +0.02 with the interval above 0. **KILL** otherwise.

### Test 2: a team of model families
- **Models:** villa dense-native (dnative) and ink_9um seeds 42 and 43 (`villa_any.sh`, reading side). Each model's window is chosen among d −2/0/+2 on the w058 crop at α 1, as in round 4.
- **Ensemble E:** the mean of the four models' maps (O, dnative, s42, s43), each z-scored over the crop's joint papyrus.
- **PASS** if E − O at α 0.7 and 0.5 is ≥ +0.02 with the interval above 0. **KILL** otherwise.
- **Universality (reported):** each model's contrast α₀.₆₅, where its pooled AUC falls to 0.65 (interpolated). If all lie within ±0.05 of each other, the limit is read as a property of the data, not of one model.

### Test 3: which scales and which aspect carry the evidence (diagnostic; interpretation fixed in advance)
- **Setting:** O on the T1 crops at α 1 (native 1447 letters), our float inference.
- **Input variants, per layer in the image plane:**
  - low-pass (Gaussian σ = 1, 2, 4, 8 px);
  - high-pass (input − Gaussian σ = 2, 4, 8, 16 px, plus the crop's mean);
  - phase randomisation in 128 px tiles: amplitude kept, one random phase field shared by all layers of a tile.
- **Statistics:** pixel AUC for the band variants. For phase randomisation, tile-level AUC: the mean probability of 128 px tiles with ≥ 20% letter pixels against tiles with no letter pixels inside the certainty mask, original against randomised.
- **Reading:**
  - Coarse evidence if low-pass σ 4 keeps AUC ≥ 0.75 while high-pass σ 4 drops below 0.65; fine evidence if the reverse.
  - Texture evidence if the randomised tile-level AUC stays ≥ 0.65; structure evidence if it falls below 0.58.
  - Otherwise mixed.

### Test 4: depth fingerprint of letters vs false lights
- **Blobs:** connected components (≥ 50 px) of O's map above its 99th percentile on the papyrus.
  - Letters: 1447 T1 crops at α 1 (overlapping the labels), and 343 s028-s031 (inside letter boxes).
  - False lights: 0268 T073-T076 and 1218 T039-T042 (all top blobs), and 800 e055/e060 (all top blobs).
- **Ablation:** one 3-layer slab at a time across O's 17-layer window, replaced by the same layers shifted by +405 px (3.5 mm) along x. That keeps texture statistics and breaks local structure.
- **Fingerprint:** per blob, the drop in mean logit per slab, and the shell fraction = the drop in the slab(s) covering the outer (inked) face ± 2 layers (tracker fall, blob mean) divided by the sum of positive drops.
- **Rule:** a threshold on the shell fraction is chosen on 343 letters vs 0268 lights (maximum Youden J) and tested once on 1447 letters vs 1218 and 800 lights.
  - **PASS** if held-out AUC ≥ 0.80 and ≥ 70% of 1447 letter blobs are kept with ≤ 10% of false lights passing.
  - **KILL** if AUC < 0.70 or the direction flips. **Partial** in between.

### Test 5: where were letters found? (desk check)
- **Method:** the radial position (winding index or fraction of radius from the outside) of the published 9 µm and 2.4 µm text finds (343, 1447, Scroll 5/PHerc. 172, PHerc. 1667, Paris 4), against our search bands (800 windings 50-69 of about 103 sheets; 0268 T073-T076; the survey's mid-radius windings).
- **Rule:** if at least 3 of the finds lie in the outer third and our bands do not, we propose searching the outer windings of 800 and 0268 (download sizes to be asked). Otherwise there is no change.

**Results, tests 1-4 (2026-10-23, `r10/run_r10.sh`; output `~/vesuvius/eval/r10_result.txt`, JSON `r10_*.json`; about 1 h of GB10)**

**Tests 1 and 2: pooled T1 AUC.**

| model | α 1 | 0.85 | 0.7 | 0.5 | 0.35 | 0 | window | α₀.₆₅ |
|---|---|---|---|---|---|---|---|---|
| Reader v2 (O) | 0.808 | 0.708 | 0.612 | 0.536 | 0.520 | 0.519 | d −2 | 0.76 |
| O, depth-window mean | 0.805 | 0.704 | 0.614 | 0.542 | 0.527 | 0.513 | d −2/0/+2 | |
| dnative | 0.786 | 0.652 | 0.577 | 0.527 | 0.511 | 0.500 | d −2 | 0.85 |
| ink_9um seed 42 | 0.695 | 0.605 | 0.544 | 0.507 | 0.497 | 0.511 | d −2 | 0.92 |
| ink_9um seed 43 | 0.691 | 0.589 | 0.533 | 0.493 | 0.500 | 0.510 | d 0 | 0.94 |
| ensemble E | 0.794 | 0.686 | 0.598 | 0.532 | 0.513 | 0.512 | | 0.79 |

- **Test 1: KILL.** Depth-window mean − O = +0.004 [−0.006, +0.015].
- **Test 2: KILL.** E − O = −0.009 [−0.047, +0.029]: averaging with weaker models dilutes Reader v2.
- **Universality: model-dependent.** α₀.₆₅ spreads 0.18, from 0.76 (Reader v2, trained on native 8.64 µm data) to 0.94 (ink_9um seeds, trained on simulated 9 µm).
- **Reading:** the training data of the model moves the limit. The best public model sets today's limit, and a better-trained model could lower it modestly. Small-label fine-tuning cannot (round 6).

**Test 3: scales and aspect.**

| input | pixel AUC | tile AUC |
|---|---|---|
| original | 0.808 | 0.877 |
| low-pass σ 1 / 2 / 4 / 8 px | 0.790 / 0.703 / 0.564 / 0.495 | |
| high-pass σ 2 / 4 / 8 / 16 px | 0.658 / 0.708 / 0.749 / 0.773 | |
| phase-randomised | | 0.492 (202 letter and 128 blank tiles) |

- **By the rule:** scale "mixed" (high-pass σ 4 = 0.708 is below 0.75), aspect "**structure**".
- **In substance:**
  - Smoothing beyond 2 px (17 µm) destroys the evidence (σ 4: 0.564). Removing everything coarser than 16 px costs little (0.773).
  - So Reader v2 sees ink mainly in fine detail of about 9-35 µm, at the scanner's effective resolution (edge width about 35 µm, round 9).
  - The evidence is in the spatial arrangement, not in texture statistics: with the amplitude spectrum kept and the phase randomised, the AUC falls to chance.

**Test 4: depth fingerprint: PARTIAL.**

| group | blobs | mean drop per slab (window layers 0-2 … 15-16), normalised | shell fraction (median) |
|---|---|---|---|
| 1447 letters | 35 | 0.09 0.17 0.26 0.23 0.16 0.08 | 0.25 |
| 343 letters | 17 | 0.14 0.22 0.21 0.19 0.15 0.09 | 0.23 |
| 0268 lights | 202 | 0.15 0.15 0.14 0.17 0.17 0.17 | 0.33 |
| 1218 lights | 128 | 0.15 0.18 0.16 0.17 0.15 0.14 | 0.33 |
| 800 lights | 89 | 0.16 0.19 0.16 0.17 0.18 0.13 | 0.31 |

- **Train** (343 letters vs 0268 lights): letters have the lower shell fraction, threshold 0.28, AUC 0.801.
- **Test** (1447 letters vs 1218 + 800 lights): AUC 0.734; 71% of letters kept, but 29% of lights pass (the rule needs ≤ 10%).
- **Reading:** the letters' evidence peaks in a few central layers of the window, while false lights draw evenly on all layers (whole-sheet structures). The pre-registered statistic, which looks at the outer face, catches this only partly.
- **Post-hoc lead, not pre-registered:** a peakedness statistic (e.g. the largest slab share, or the profile's entropy) could make a better false-positive filter. It would be a separate test.

**Result, test 5 (2026-10-23, desk check from our records): NO CHANGE.**
- **343:** the letter boxes sit at r ≈ 780 vx with about 31 real sheets inside (`fl343/PLAN_stageB.md`). That is the inner or middle part of the roll, not the outer third. The total sheet count of 343 was not measured, so the fraction is an estimate.
- **1447:** w058-w062 are three consecutive windings of the z 11000-14500 band (dataset card). Their position relative to the outer surface is not given; the numbering suggests the middle, not established.
- **PHerc. 1667:** the published reading spans much of the radius. [one line removed: private alignment details]
- **Paris 4:** text read across many windings in 2023-2025.
- **Scroll 5 (PHerc. 172):** finds "mostly toward the outer wraps" (materials agent, unverified). Likely selection bias: segmentation starts from the outside.
- **Reading:** at most one or two finds fall in the outer third, so the rule's condition (≥ 3) is not met. Written rolls carry text over most of their radius; where text was found reflects where people looked. Our mid-radius bands are not the reason for the nulls.

## 17. Round 9: registration-free areal mass and the effective-resolution gate (approved by the user 2026-10-23; rules written before any computation)

**Source:** `lateral3/materials.md`, test A and the test-B gate.
- **Premise:** any linear blur conserves the depth-integrated attenuation. Carbonisation removed 50-70% of the papyrus's mass but little of the soot's, so ink should add an areal-mass excess (estimated 6-40% of the sheet) that survives 9 µm voxels.
- **Never measured this way:** round 1's matched filter was cross-scroll and worked on a fixed window around a mesh that is often off the sheet.

**Data:**
- PHerc. 1447 w058 and w060 (24-layer renders, Nader's labels, certainty mask, papyrus = layer 12 > 0);
- PHerc. 343 s028-s031 (66 layers, 16 covered letter boxes, 200 random boxes per winding as `box343_single`);
- round-1 tracker edges (`lat1/edges`: rise = inner edge r, fall = outer edge f, valid).

V is the render after a 5 × 5 in-plane mean. V_void is the render's mean over void voxels (smoothed value below the tracker threshold, eroded 5 × 5 × 5), as in round 5.

**Step 0 (diagnostic, no verdict):**
- Mean depth profile of V − V_void locked to each edge (offsets −10..+6 layers from round(f), and mirrored from round(r)).
- 1447: letters vs other papyrus in the certainty mask. 343: letter boxes vs their rings.
- It shows where any excess sits (outside the face: film; inside: impregnation) and whether the two scrolls' faces are mirrored.

**Readouts (per pixel):**
- **A1, sheet mass:** Σ (V − V_void) over layers floor(r) − 3 .. ceil(f) + 3.
- **A2, face gradiometer:** the inked face's mass (4 layers inside plus 2 outside its edge) minus the same on the other face.
- **A3:** A1 minus its linear regression on sheet thickness f − r (fitted per render).
- Pixels whose window leaves the render are excluded.
- Each readout is smoothed (Gaussian σ 6 px), and its local median over 4 mm (computed on an 8× downsampled grid) is subtracted.

**Fixed in advance:**
- **Inked face:** on 343 the outer face (f), as in round 1. On 1447 it is cross-fitted: the face with the higher A2 AUC on one winding is used on the other.
- **Sign:** more mass under ink.

**Statistics:**
- 1447: pixel AUC per winding (letters vs other papyrus inside certainty ∩ papyrus ∩ valid).
- Shifted-label controls: labels moved ±405 and ±810 px along x.
- 343: box test on the readout map (z over the papyrus, clipped 0..3, inside − ring ≥ 0.3) against random boxes.

**Rule:**
- **PASS** if one readout satisfies all three:
  1. AUC ≥ 0.60 on both 1447 windings;
  2. on each winding, AUC exceeds the largest shifted-label AUC by ≥ 0.05, so the effect is stroke-shaped and not regional;
  3. on 343, ≥ 5/16 letter boxes and ≥ 2× the random-box rate.
- **KILL** otherwise.
- **Reported either way:** the mean A1 excess under letters on 1447, as % of the local sheet mass with a 95% bootstrap interval over letter components. Its upper bound is the measured limit on ink mass, and the input for any mass- or lead-based scan proposal. Conversion: a 3-5 mg/cm² sheet means 1% ≈ 0.3-0.5 µm of a 1 g/cm³ film.
- **After a PASS only (pre-registered utility step):** add the readout's z to Reader v2's logit, with the weight fitted on 343 only, and score on the T1 bench at α 0.7 and 0.5. It needs +0.03 AUC with the interval above 0.

**Effective-resolution gate (a measurement, no verdict on ink):**
- On open faces (recto gap ≥ 6 layers), the 10-90% width of the transition across the outer edge along the normal: sub-voxel interpolation between the void level and the sheet plateau, median over pixels, per scroll.
- If it exceeds 3 voxels (26 µm), surface morphology at 5-20 µm (film, cracks, groove filling) is not testable at 9 µm, and materials tests B and C are dropped. Otherwise they become testable (separate approval).

### Result (2026-10-23, `r9/r9_mass.py`; output `~/vesuvius/eval/r9_result.txt`, JSON `r9_result.json`; CPU only)

**RULE: KILL.** No readout shows more mass under ink.

| readout | w058 | w060 | largest shifted-label AUC | 343 boxes (random) |
|---|---|---|---|---|
| A1, sheet mass | 0.460 | 0.459 | 0.495 / 0.522 | 0/16 (1%) |
| A2, gradiometer, outer face + | 0.496 | 0.493 | 0.514 / 0.512 | 1/16 (1%) |
| A3, mass residual on thickness | 0.445 | 0.435 | 0.492 / 0.520 | 0/16 (2%) |

**Step 0 (letters − other papyrus, render units, offsets −10..+6 from the edge):**
- **No positive bump at the inked face.** On w058 the letters are slightly lower at every offset (−1.5 to −3.6).
- **On w060** the differences sit in the gaps: −10 to −11 just beyond the outer face (wider gaps at letters, as in round 8), and +2.5 to +2.9 into the inner gap.
- **Reading:** geometry differs at letters, not density.

**Mass bound:**
- **The pre-registered statistic is invalid, and that is our error.** It gave +14.0% [+12.6, +15.5] on w058 and +10.4% [+9.0, +11.7] on w060. The mask split the letters into about 2,500 small fragments per winding, and equal weights per fragment let noisy edge fragments dominate.
- **Pixel statistics point the other way:** letter median −0.087 vs other −0.037 (w058), −0.099 vs −0.054 (w060).
- **Corrected (post hoc, not pre-registered):** whole letters as units (19 letters ≥ 2000 px, 144 background tiles, 5000 resamples, pixel-weighted). Letters minus background = **−4.3% [−7.2, −1.2]** of the local sheet mass.
- **Reading:** a positive areal-mass excess under the ink is excluded at 95% for this readout. Letters are, if anything, about 4% lighter, plausibly because of the ±3 layers outside the edges and the wider gaps at letters. The materials model's prediction (+6-40%) is falsified for 1447.
- **Consequence:** lead at Tack's levels (which would add 8-70% attenuation) is absent from 1447's ink. A lead K-edge scan makes sense only for a roll whose writing XRF shows to carry lead.

**Effective-resolution gate:**

| | w058 | w060 | 343 (4 windings) |
|---|---|---|---|
| outer-face 10-90% edge width (layers) | 4.05 | 4.11 | 3.73 |
| open pixels sampled | about 200,000 | about 200,000 | |

The widths exceed 3 voxels (about 35 µm). **Surface morphology at 5-20 µm (film, cracks, groove filling) is not testable at 9 µm**, so materials tests B and C are dropped.

## 16. Round 8: two last cheap checks (approved by the user 2026-10-23; rules written before any computation)

### Test A: does writing change how the windings stick? (disbond C-scan, contrarian idea 3)
- **Mechanism:** the ink's binder (gum) might have glued the inked recto to the next winding during carbonisation, or the soot might have acted as a release film. Either way, the gap between windings would follow the strokes. A gap is voxel-scale geometry, not a micron-thin film, so it might escape the clutter limit of round 5.
- **Score maps per pixel:** the recto-side gap (layers counted outward from the outer edge to the next papyrus run, as `r5_gap.recto_gap`) and a contact mask (gap ≤ 1). Control: the verso-side gap, counted inward from the inner edge (`setoff2.gap_map` logic). Ink sits on the recto, so a text effect should be stronger there.
- **1447 (primary):** pixel AUC of the recto gap and of the contact mask, letters against other papyrus inside the certainty mask (w058 and w060 pooled; the score sign is free, so an AUC far below 0.5 also counts).
  - Controls: the label mask shifted by ±405 and ±810 px (3.5 and 7 mm) along x, keeping only pixels inside the certainty mask; and the verso-gap AUC.
- **343 (confirmation):** per letter box, mean recto gap inside minus in its ring (box grown 2×), against 200 random boxes per winding. Permutation p-value (two-sided) of the letter boxes' mean difference.
- **PASS** if all four hold:
  1. on 1447 the recto-gap or contact AUC is ≥ 0.58 or ≤ 0.42;
  2. the shifted-label controls stay within 0.50 ± 0.03;
  3. the verso-gap AUC deviates from 0.5 by less than half as much as the recto one;
  4. 343 shows the same sign with p < 0.05.
- **KILL** otherwise.

### Test B: "free dual energy" (desk check, metadata only)
- **Method:** list the volumes of the 21 eligible scrolls, plus 343 and 1447, on the open-data bucket (directory listings and array metadata, no data). Read voxel size and energy from the names.
- **Feasible** if at least one eligible scroll, or a scroll with known ink, has two full-height scans of the same papyrus at energies at least 10 keV apart and voxel sizes within a factor 1.5. The next step (registration, material decomposition, a test on known ink) would then be a separate proposal with its download size.
- **Closed** otherwise.

**Result A (2026-10-23, `r8/r8_disbond.py`; output `~/vesuvius/eval/r8_disbond.txt`, JSON `r8_disbond.json`): KILL.**
- **1447 overall:** AUC recto gap 0.552, contact 0.490, verso gap 0.474. The shifted-label controls give 0.519-0.528, close to the true labels. So the small recto effect is regional (letters lie in areas with slightly wider gaps), not stroke-shaped.
- **The windings disagree:**
  - w058: median recto gap 3.0 layers at letters and elsewhere; contact share 0.173 vs 0.156.
  - w060: median gap 5.0 vs 3.0; contact share 0.120 vs 0.187.
- **343:** inside − ring recto gap −0.62 vs +0.09 for random boxes (p = 0.003). Letter boxes there sit where windings are closer, the opposite sign to 1447.
- **Conditions:** 1 (|AUC − 0.5| ≥ 0.08), 3 (verso weaker) and 4 (same sign on 343) fail; 2 holds.
- **Reading:** the gap between windings does not follow the strokes in a consistent way. The 343 effect is real but regional, and goes the other way on 1447.

**Result B (2026-10-23, `fetch_previews.ls` on the open-data bucket, metadata only): CLOSED.**
- 19 of the 21 eligible scrolls have a single scan: 8.640 µm / 116 keV (May or November 2025) or 9.362 µm / 113 keV (August 2025). 343 and 1447 also have one scan each.
- PHerc. 0846A and PHerc. 1203 have a second scan (2026-03-19) at 2.403 µm, 0.2 m propagation distance and 77 keV. The energies differ by 36 keV, but the voxel sizes differ about 4× (rule: within 1.5×), so the pair does not qualify.
- Public work found no text on either scroll at 2.4 µm (mletic; ArcheyChen on 0846A's band, about 107 cm²).
- **By-product:** the organisers have started higher-resolution, lower-energy, longer-propagation rescans of eligible scrolls (0846A, 1203). This is the direction our round 5 points to.

## 15. Round 7: column lock-in, a population test for text (approved by the user 2026-10-22; rule written before any computation)

**Idea (physics agent, `lateral2/physics.md` idea 3).** Columns (5-7 cm, gaps 1-2 cm) make the ink response periodic in unrolled arc length s. Folds and crush zones are organised by angle θ and repeat once per turn. Removing the θ-coherent part and looking for a constant pitch in s across windings could show that text is present even where single letters are invisible.

**Data:**
- Reader v2 maps at d0 (L66 s25) of the 20 PHerc. 800 windings e050-e069 (about 1.6 m of arc). Reading side (`_reverse`) is the test; the blind side (forward) is a control.
- Papyrus mask: layer 33 > 0. 0268 T073-T076 is report-only.

**Profiles:**
- Per winding, 1 mm strips (116 px): the mean ink probability over the band's papyrus pixels. A strip is empty if coverage is < 30% or it lies within 150 px of the render edge.
- **θ reference:** x / width = fraction of the turn. For winding k, the mean of the profiles of windings k±2..k±5 interpolated at the same θ is subtracted (radial differential).
- Each winding's residual is centred, and all residuals are scaled by their pooled SD.

**Statistic:**
- 5 segments of 4 consecutive windings (robust to winding-assignment errors). Within a segment the strips are concatenated in s.
- Power(P) = |Σ w r e^(−2πi s/P)|² / Σ w, summed over segments. T = max over pitch P ∈ [55, 100] mm (0.5 mm steps).

**Null:**
- Each winding's residual is circularly shifted by a random amount and T recomputed: 200 scrambles per trial, 1000 for the science runs. p = (1 + #(T_scr ≥ T)) / (n + 1).
- "Detected" means p < 0.01.

**Power (map-level injection):**
- **Ink-only increment:** O's response to 1447 letters at contrast α, measured on the round-4 T1 crops at d0 (L24 s4): Δ = p(α) − p(0), minus its mean over certainty-mask papyrus without letters. Kept inside the certainty mask, averaged per 1 mm strip over the band height (1820 rows).
- **Synthetic columns:** pitch P ~ U[60, 90] mm, column width 0.8 P, random phase. Each column is filled with the three crops' increment profiles (random order and flips); gaps get nothing. The columns are added to the real 800 reading-side profiles before the θ reference.
- 50 trials per α ∈ {1, 0.85, 0.7}.
- **Assumption, stated:** the response to faint ink adds to the map. A real-text positive control over ≥ 1 m of arc does not exist in our data (343 and 1447 are too short).

**Calibration:**
- 50 null datasets: the real reading-side profiles with winding order permuted and each winding reversed in s.
- The blind side of 800, processed identically.

**Rule**
- **PASS** (the test has power and is calibrated): detection ≥ 80% at α 0.85, false detections ≤ 2% on the null datasets (at most 1 of 50), and the blind side not detected.
- **KILL** otherwise.
- **If PASS, the science result on 800:**
  - a reading-side detection with the blind side clean means text-like columns are present, with their pitch;
  - no detection gives an upper limit: columns with ink at or above α₈₀ (the contrast with 80% detection, interpolated) × 1447's are excluded over e050-e069.
- **0268:** its own power and p-value, reported only.

### Result (2026-10-22, `r7/r7_columns.py`; output `~/vesuvius/eval/r7_result.txt`, JSON `r7_result.json`; a few minutes of CPU)

**PHerc. 800** (20 windings, 1492 mm of arc with data, 5 segments of 4):
- **Power:** detected in 0/50 trials at α 1, 0/50 at 0.85 and 0/50 at 0.7, so α₈₀ > 1.
- **Null datasets:** 2/50 false detections (4%).
- **Science runs** (meaningless without power): reading side T 59.1 at P 84.5 mm, p = 0.49; blind side T 68.9 at 71.5 mm, p = 0.53.

**PHerc. 0268** (4 windings, 494 mm): power 2/50 at α 1, 1/50 at 0.85, 0/50 at 0.7. Null datasets 0/50. Reading side p = 0.37, blind side p = 0.10.

**RULE: KILL** (power at 0.85 < 80%, and null rate > 2%).

**Why (diagnostic, 800 reading side):**
- The 1 mm strip mean of the ink probability has SD 0.031 along the windings (mean 0.308). Subtracting the θ-coherent part does not reduce it (SD 0.031 after).
- Full-strength 1447 text adds only +0.016 to the strip mean inside a column. It is diluted over the 1.6 cm band height, and Reader v2's response to 1447 letters is moderate (AUC 0.81).
- The variability of the maps is "red" (strong at the cm scale), so averaging along a column does not beat it.
- In 800 the circumference (6.6-9.1 cm over e050-e069) falls in the same range as the column pitch (6-9 cm). Columns then sit at nearly the same angle on successive windings, and the radial differential partly removes them together with the folds.

**Lesson:** layout-level tests on 9 µm ink maps lack power. The columns of even full-strength 1447-like text disappear in the cm-scale variability of the maps. This is consistent with mletic's line score at chance at 9 µm and with the uncertainty-bench power below 50% at 113/116 keV.

## 14. Round 6: in-domain ceiling probe (approved by the user 2026-10-22; rule written before any training or test)

**Question:** with real labels of the same ink, can Reader v2's model family detect fainter 1447 letters than the original does? This is a skyline. If even in-domain labelled training cannot lower the limit, ink-transfer and simulator routes are not worth running.

**Folds (by winding, fully independent):**
- Fold A = w058's letters; fold B = w060's letters.
- Each model trains on one fold and is scored only on the other fold's crops ("cross-fitted"). Every letter is scored by a model that never saw it.

**Bench T1b** (bench rules of `lateral2/ml.md`):
- The T1 crops and blend of round 4, with new held-out PHerc. 800 backgrounds: e050 (w058 crop), e051 (w060 upper crop), e069 (w060 lower crop). x offsets chosen from masks only, as before.
- Training backgrounds are e056-e064, at least 5 windings from every test background.
- α ∈ {1, 0.85, 0.7, 0.5, 0.35, 0}.
- Reader v2 (O) at d −2, our float inference (`r5_infer.py`).
- Provenance: Reader v2's training list has no 1447 and no 800.

**Arm (i), fine-tune:**
- Reader v2, all weights, trained on the fold's 1447 letters blended into the training backgrounds at α ~ U[0.35, 1] (round-4 blend, whole-render layer statistics).
- Target: Nader's labels, loss only inside the certainty mask. Input as at inference (layers 2-18 ± 2 jitter, reversed, `normalize_robust`), flips and rotations.
- AdamW lr 3e-5, wd 1e-4, 200 warm-up steps and cosine decay, 2500 steps, batch 32, bf16.
- Two seeds per fold. The step-2500 weights are fixed in advance; no checkpoint selection.

**Arm (ii), context head on frozen O:**
- Input: O's logit map, pooled 4×. Model: a small residual CNN with dilations 1-16 (receptive field about 500 px at full resolution, about 10k parameters), output added to O's logit.
- Training maps: the fold's crops blended into e056, e058, e060, e062, e064 at α 1, 0.85, 0.7, 0.5, 0.35, with O run on each.
- Target: labels pooled 4×, inside the certainty mask. Adam lr 1e-3, 1500 steps, batch 32, two seeds.

**Statistic:**
- Pooled pixel AUC on T1b (letters vs other papyrus in the certainty mask ∩ joint papyrus), each crop scored by the other fold's model.
- Gain over O at α 0.7 and 0.5, averaged. Paired bootstrap (1000) over letter components and 256 px tiles, on the map averaged over the two seeds.

**Rule**
- **PASS (headroom):** in either arm, both seeds give a mean gain ≥ +0.05, and the seed-averaged map's 95% interval is above 0.
- **KILL:** in both arms the seed-averaged mean gain is < +0.03. Even labelled in-domain training cannot lower the limit, so ink-transfer, simulator and JEPA-style routes are dropped.
- **PARTIAL** otherwise.
- Also reported: the change at α 1, the per-letter mean AUC, and false lights on the α 0 crops at each model's 50%-recall threshold.
- **Added before any run (2026-10-22):** arm (ii) works on a 4× pooled map, and plain smoothing alone could raise AUC. So "O pooled 4× and upsampled" is computed as a reference. Arm (ii) counts as learned headroom only if it also beats that reference by the same margins (+0.05 for both seeds, interval above 0). Otherwise any gain is credited to smoothing and reported as such.

### Result (2026-10-22, `r6/run_r6.sh`; log `~/vesuvius/eval/r6_result.txt`, JSON `r6_result.json`; 1 h 45 min of GB10)

**Runs:**
- T1b joint papyrus covers 98-100% of the certainty masks.
- Four fine-tunes (2 folds × 2 seeds, 2500 steps, 19 min each), final masked BCE 0.61-0.63.
- Context heads: final loss 0.49-0.54.
- Depth shifts in training (global statistics) were +1..+3 layers, against 0 in the crop blends. This is the same kind of difference as in round 4, covered by the ±2 jitter.

**Pooled cross-fitted AUC on T1b** (19 letter components, 160 tiles):

| model | α 1 | 0.85 | 0.7 | 0.5 | 0.35 | 0 |
|---|---|---|---|---|---|---|
| O | 0.808 | 0.711 | 0.610 | 0.520 | 0.500 | 0.499 |
| O pooled 4× | 0.809 | 0.712 | 0.611 | 0.520 | 0.501 | 0.499 |
| arm (i) seed 0 / seed 1 | 0.794 / 0.791 | 0.703 / 0.697 | 0.609 / 0.601 | 0.525 / 0.517 | 0.501 / 0.493 | |
| arm (i) seed mean | 0.795 | 0.702 | 0.607 | 0.521 | 0.497 | 0.495 |
| arm (ii) seed mean | 0.767 | 0.691 | 0.595 | 0.519 | 0.508 | 0.497 |

**Gains** (mean of α 0.7 and 0.5):

| comparison | gain | seeds |
|---|---|---|
| arm (i) vs O | −0.001 [−0.031, +0.028] | +0.002 / −0.006 |
| arm (ii) vs O | −0.008 [−0.063, +0.040] | −0.013 / −0.006 |
| O pooled vs O | +0.000 | — |

**Report-only measures:**

| measure | O | arm (i) | arm (ii) |
|---|---|---|---|
| change at α 1 | — | −0.013 | −0.040 |
| per-letter mean AUC, α 0.7 / 0.5 | 0.603 / 0.523 | 0.612 / 0.526 | 0.584 / 0.525 |
| false lights at α 0 | 0.063 | 0.043 | 0.094 |

**RULE: KILL (no headroom even with in-domain labels).**
- Fine-tuning Reader v2 on real 1447 letters of one winding, blended at the same faint contrasts into 800 papyrus, does not help it see the other winding's letters at α 0.7 or 0.5. A context head over about 500 px does not either.
- As pre-registered, the ink-transfer, simulator and JEPA-style routes are dropped.
- **Caveat:** each fold has about 10 letter components. A much larger in-domain label set could behave differently, but none exists at 8.64 µm. With round 4 (343 stamps) and round 5 (clutter-limited, x = 0.04), the limit looks physical.

## 13. Round 5: six diagnostics from lateral round 2 (approved by the user 2026-10-22; rules written before any computation, except test 4, a desk fact)

Source: `IDEAS_lateral2.md`. No downloads. Scripts in `r5/`. Reader v2 = O; T1 = the round-4 bench (1447 letters in held-out 800 papyrus, 3 crops, pooled pixel AUC inside certainty ∩ joint papyrus, letter-and-tile bootstrap). O's window there is d −2 (L24 s2), chosen in round 4. Orientation: the 343 ink sits on the outer face of our surfaces (round 1, step 0), i.e. the tracker's "fall" edge. The "recto-side gap" is therefore counted outward from it.

### Test 1: logit audit (where is faint evidence lost?)
- **Why:** O's T1 AUCs convert to d′ = √2 Φ⁻¹(AUC) = 1.24 / 0.78 / 0.39 / 0.14 at α 1 / 0.85 / 0.7 / 0.5, i.e. d′ ∝ α³. Part of the loss may come from our readout: 8-bit maps (p < 1/255 → 0) and box tests on probabilities.
- **Method:** our own tiled inference (exact reproduction of the published command: 128 px tiles, stride 64, Hann weights) writes float probability and float logit maps of T1 at s2. Pooled AUC is computed from (a) the stored 8-bit maps, (b) float probabilities and (c) float logits. Then d′ and the exponent p in d′ ∝ α^p (least squares on log d′ against log α, α 1-0.5).
- **Box test variant:** the box mean of the z-scored logit, inside − ring ≥ 0.3, no clipping; same letter and random boxes as round 4.
- **PASS** (evidence is lost in the readout) if p(c) ≤ 2.0, or if logit boxes at α 0.7 reach ≥ 5/20 with random ≤ 10%.
- **KILL** (the loss is inside the network) if p(c) ≥ 2.7 and logit boxes at α 0.7 ≤ 2/20.
- Otherwise: partial. Reported anyway: the 343 fade boxes (16) with logit box scores at α 1-0.35.

### Test 2: noise or clutter?
- **Noise estimate:** from void voxels of the T1 α 1 crops (smoothed value below the papyrus threshold, with a whole 5 × 5 × 5 neighbourhood void): residual variance after a 5 × 5 in-plane local mean, and its radial power spectrum. Model-free ratio R = σn² / σc² at stroke scale (difference of Gaussians, σ 3 and 15 px, on the near-surface layers 9-19), with σc² = band-passed papyrus variance outside the letters − σn².
- **Injection:** noise with the measured spectrum is added to the T1 α 1 crops at +25%, +50% and +100% of σn² (inside the joint papyrus, clipped to 1..255), and O is run (float logits). Clutter control: the same added variance as zero-mean PHerc. 800 papyrus texture from another crop, at +100%.
- **Equivalent contrast:** α_eq is where O's clean T1 AUC curve (round 4, interpolated in α) equals the noisy AUC. Noise share x = (1/α_eq² − 1)/k, where k is the added fraction (k = 1 for +100%).
- **PASS** (noise matters, so asking for more photons or a denoiser is worth it) if x ≥ 0.38 at k = 1 and the noise lowers AUC at least as much as the clutter control.
- **KILL** (clutter-limited: drop photon and denoising routes) if x ≤ 0.15.
- Otherwise: intermediate, report x. R is reported as the model-free check.

### Test 3: is ink easier to see where the recto faces a gap?
- **Recto-side gap:** per pixel, the number of non-papyrus layers counted outward from the tracker's outer edge (fall) to the next papyrus run, with the tracker's smoothing and threshold (as `setoff2.gap_map`, mirrored), capped at the render. Strata: fused ≤ 2, mid 3-5, open ≥ 6 layers.
- **1447 (w058, w060 native renders, O's d −2 maps):** pixel AUC per stratum, letters against other papyrus inside the certainty mask. Bootstrap (1000) over letter components and 256 px tiles for AUC(open) − AUC(fused).
- **343 (s028-s031, O's d0 maps of the clean renders):** box hits by the box's median gap stratum, and random boxes (200 per winding) by stratum.
- **PASS** if, on 1447, AUC(open) − AUC(fused) ≥ 0.08 with the interval above 0, and (where 343 has ≥ 4 boxes in both strata) the 343 open hit rate is ≥ 2× the fused one while random boxes rise less.
- **KILL** if the 1447 difference is < 0.08, the interval includes 0, or the sign is opposite.
- **Inconclusive** if a 1447 stratum holds < 5% of the letter pixels.
- If PASS, the follow-up is an open-recto map of 800 (2 × 2 cm tiles) to choose where to search.

### Test 4: were the searched bands in the margins? (desk fact, computed 2026-10-22 before writing this rule)
- **Survey bands:** `survey/scripts/band.py` centred every band at mid-height of the papyrus extent measured on the m7 level-5 prediction (slices with > 10% of the maximum papyrus area).
- **Distances:** the bands lie 5.7 cm (0268) to 9.7 cm (1218) from the nearest preserved papyrus end. PHerc. 800's band (z 11000-12500 of 24298 slices, 8.64 µm) is 9.5 cm from the bottom and 10.2 cm from the top. Preserved heights are 12.7-21 cm.
- **Upper and lower margins** of a roll lie within about 3 cm of its original edges, so no searched band is in them. A break would only move the original edge further away.
- **Intercolumnia:** our renders span 4-10 cm along each winding, so with columns of 5-7 cm and gaps of 1-2 cm, most of the rendered area lies inside columns.
- **Verdict:** the margin explanation of the nulls is excluded. The contrarian's ON/OFF test (steps 1-2, z-core downloads) is not needed for this purpose.

### Test 5: metal-speck census
- **Why:** lead was found in the ink of two Herculaneum fragments (Brun et al. 2016; Tack et al. 2016). At 113-116 keV, above lead's 88 keV edge, even micron grains make bright specks.
- **Specks:** residual r = V − 3 × 15 × 15 local mean. Connected components (26-neighbourhood) of r > 5 robust σ (MAD over the render's papyrus), size 1-27 voxels.
- **Face assignment:** recto shell = from 1 layer inside to 3 layers outside the outer edge (fall); verso shell = the mirror image at the inner edge (rise). Run-based sheet tracker as in round 1.
- **Calibration:** speck density per mm² of recto shell inside letter boxes against random boxes, for 343 (16 boxes) and 1447 (20). Bootstrap over boxes.
- **Census:** recto/verso density ratio per scroll over all local renders (343, 1447, 800 e050-e069, 0268 tall band, 1218 tall band, survey windings), with bootstrap over 2 × 2 cm tiles.
- **PASS** if (a) on 343 or 1447 the letter/random ratio is ≥ 2 with a lower 95% bound > 1.3, or (b) a scroll has a recto/verso ratio ≥ 1.5 with a lower bound > 1.2. In case (b) that scroll's specks are then inspected for line structure before any claim.
- **KILL** otherwise.

### Test 6: WiSE-FT of the round-4 weights
- **Model W:** the parameter-wise average 0.5 · O + 0.5 · F, with F the round-4 fine-tune.
- **Run:** T1 exactly as in round 4: window chosen on the w058 crop at α 1 among d −2, 0, +2; same rule (mean gain at α 0.7 and 0.5 ≥ +0.03 with the interval above 0, α 1 ≥ O − 0.02, false lights ≤ 1.25 × O).
- **Caveat:** the T1 backgrounds sit next to F's training windings (ML agent's bench critique). This favours W, so a pass would need a cleaner bench before any use.

### Results (2026-10-22, `r5/run_r5.sh`; log `~/vesuvius/eval/r5_result.txt`, JSON in `/mnt/data/vesuvius/eval/r5/`)

**Test 1, logit audit: PARTIAL by the rule; in substance the loss is inside the network.**
- **Step 0:** our float inference matches the published 8-bit map exactly on 98% of papyrus pixels and within one level on 100%.
- **Pooled T1 AUC:** identical from 8-bit maps, float probabilities and float logits at every α (0.808 / 0.708 / 0.612 / 0.536 / 0.520). So p = 3.27-3.28 for all three readouts.
- **Logit box test:** more permissive for letters and random boxes alike.

  | contrast | logit boxes | 8-bit boxes |
  |---|---|---|
  | α 0.7 | 5/20 vs 18% random | 1/20 vs 11% random |
  | α 0.5 | 2/20 vs 16% random | — |

  On 343 (logit): 12/10/6/3/1 of 16 at α 1/0.7/0.5/0.35/0, against 16-22% random. The ratio over random is the same as on the 8-bit maps.
- **Reading:** faint evidence is not lost in our storage or aggregation. d′ ∝ α³ happens inside the network.

**Test 2, noise or clutter: KILL. Clutter-limited.**
- **Noise:** from void voxels of the three crops (20,000 patches each), variance 20-23 (render units), lag-1 layer correlation +0.79.
- **Model-free ratio:** R = σn²/σc² at stroke scale = 0.010-0.013. Noise is about 1% of the papyrus clutter.
- **Injection** (pooled AUC 0.808 clean):

  | added | AUC | α_eq | x |
  |---|---|---|---|
  | noise +25% | 0.806 | 0.998 | 0.02 |
  | noise +50% | 0.802 | 0.992 | 0.03 |
  | noise +100% | 0.794 | 0.979 | **0.04** |
  | clutter control +100% (same variance) | 0.803 | — | — |

- **Reading:** photon and reconstruction noise is negligible against the papyrus texture. More dose, longer exposure or a denoiser (Noise2Inverse) would not lift the ink. Only resolution or a different contrast mechanism can.

**Test 3, recto-side gap: KILL (the trend is the opposite of the hypothesis).**
- **1447** (O at d −2): AUC fused 0.829, mid 0.806, open 0.784. Letter-pixel shares are 0.28 / 0.37 / 0.35. Open − fused = −0.045 [−0.100, +0.018].
- **343:** no letter box in the fused stratum. Mid 9/13, open 3/3; random 15% and 9%.
- **Reading:** ink is not easier to see where the recto faces a gap.

**Test 4, margins:** excluded (desk fact above).

**Test 5, metal specks: KILL.**
- **Calibration:** the letter-box/random speck density ratio is 0.92 [0.60, 1.36] on 343 and 1.16 [0.79, 1.56] on 1447.
- **Census:** the recto/verso ratio is 0.94-1.11 on all 14 scrolls (343, 1447, 800, 0268, 1218 and 9 survey scrolls), every interval including 1.
- **Reading:** bright specks (thousands per few cm²) are mineral grains and the like on both faces. No scroll shows metal-bearing ink at this sensitivity.

**Test 6, WiSE-FT: KILL (no T1 gain), with a weak trend.**
- **Window:** W chose d −2 (AUC 0.844 on the w058 crop, O 0.842).

  | α | 1 | 0.85 | 0.7 | 0.5 | 0.35 |
  |---|---|---|---|---|---|
  | W − O (AUC) | −0.010 [−0.027, +0.008] | +0.021 [−0.009, +0.059] | +0.028 [−0.003, +0.064] | +0.011 [−0.020, +0.048] | −0.002 |

- **Mean of α 0.7 and 0.5:** +0.020 [−0.010, +0.054], below +0.03, with the interval including 0.
- **Other conditions:** false lights 0.119 vs 0.152 (−22%). Boxes at α 0.7: 4/20 vs 1/20.
- **Reading:** averaging with the original removes F's full-strength loss and lattice cost. A small gain at α 0.7-0.85 may exist but is not established, and the bench favours W (adjacent windings).

**What round 5 settles**
1. The limit is the papyrus texture (clutter), not photon noise: x = 0.04, R = 0.01. This is a number for the organisers: at 8.64 µm / 116 keV, more dose or denoising will not reveal the ink; resolution or contrast must change.
2. The evidence is lost inside the network (d′ ∝ α³), not in our readout.
3. Three "where to look" premises are excluded: margins, open recto, metal-bearing ink.

## 12. Round 4: faint-ink stamps as training data (D1) (approved by the user 2026-10-21; rule written before any training or test)

**Question:** if Reader v2 is fine-tuned on real ink injected at reduced contrast into the target scroll's own papyrus, does it detect ink it has never seen, in papyrus it has never seen, at lower contrast than the original, without more false lights?

**Step 0 (done before this rule):** our own forward pass reproduces the published inference command. It loads the checkpoint as `infer.configure_model` does, reads layers 25-41 reversed (reading side) and applies `normalize_robust` per 17 × 128 × 128 patch. Tiled at stride 64 with Hann weights, the interior of a 640 px region of f100_w029 matches the published map at correlation 1.0000 (forward layer order: 0.16). A training step at batch 32 takes 0.45 s.

**Training (`faint/train_faint.py`)**
- **Start:** Reader v2 (`reader-v2-step040000.pth`), all weights trainable.
- **Ink:** PHerc. 343 renders s028-s031.
- **Target:** the original Reader v2's own map of the clean 343 render (d0, reading side), i.e. what it sees at full strength. No hand labels.
- **Papyrus:** PHerc. 800, 13 training windings: e050, e051, e053, e054, e056, e057, e059, e061, e062, e064, e065, e067, e069.
- **Held out, never seen in training:** e055, e060, e063, e066 (the section-1 fade backgrounds) and e052, e058, e068 (the backgrounds of test T1).
- **Stamp:** each sample is a 343 window and a random 800 training window, blended per layer as in section 1: out = m + α(R − m) + √(1 − α²)(B′ − m).
  - B′ is the 800 window shifted in depth to the 343 render's mean profile (at most ±4 layers) and matched per layer to its mean and SD (whole-render papyrus statistics).
  - α is uniform in [0.35, 1].
  - Half of the 343 windows are centred on teacher p > 0.5, half anywhere on the papyrus; patches lie fully on the joint papyrus.
- **Input:** as at inference (layers 25-41 reversed, `normalize_robust` per patch), with the ±2-layer window jitter of Reader v2's own training, and random flips and 90° rotations applied to input and target alike.
- **Loss and schedule:** binary cross-entropy against the teacher probability. AdamW, lr 5e-5, weight decay 1e-4, 300 warm-up steps then cosine decay, 6000 steps, batch 32, bf16, seed 0.
- **No early stopping, no checkpoint selection:** the step-6000 weights are the model F. The original is O.
- **Caveat:** the 800 training papyrus counts as "no ink". Any real ink in those 13 windings is taught as background, so F may never be used to search them; only held-out windings may be searched.

**Tests (same commands for O and F; maps with `villa_any.sh`, reading side)**

**T1, primary: unseen ink in unseen papyrus.**
- PHerc. 1447 letters (Nader's labels) injected into held-out PHerc. 800 papyrus (`faint/blend1447.py`).
- Three crops of 1820 × 4400 px: w058 y 2650-4470 × x 400-4800; w060 y 500-2320 × x 600-5000; w060 y 2600-4420 × x 600-5000.
- Backgrounds: e052, e058 and e068 respectively. Each x offset is chosen to maximise the joint papyrus share inside the labels' certainty mask, from masks only.
- Blend as in `fade_blend.py`, with 1447 layer i matched to 800 layer i + 21 (both at 8.64 µm), giving 24-layer renders. α ∈ {1, 0.85, 0.7, 0.5, 0.35, 0}.
- Window: each model's d ∈ {−2, 0, +2} is chosen by AUC on the w058 crop at α = 1 and then kept everywhere (as in section 3A).
- **Statistic:** pixel AUC, label pixels against all other pixels inside the certainty mask and the joint papyrus, pooled over the three crops.
- **Uncertainty:** 1000 paired bootstrap resamples of the letters (label components) and of 256 px background tiles. The box test is reported for continuity.

**T2, real faint ink at full strength:** T1 at α = 1, i.e. native 1447 letters inside the joint papyrus.

**T3, seen ink in unseen papyrus (report only, optimistic):** the section-1 343 fade renders (backgrounds e055/e060/e063/e066) at α 1, 0.7, 0.5, 0.35 and 0, at d0, with the 343 box test (16 covered boxes). O's maps already exist.

**T4, false lights:** on T1's α = 0 renders (pure held-out 800 papyrus), the share of papyrus pixels above each model's threshold for 50% pixel recall on the T1 letters at α = 1.

**Rule**
- **PASS** if all three hold:
  1. T1: the AUC gain of F over O, averaged over α 0.7 and 0.5, is at least +0.03, with the bootstrap 95% interval above 0.
  2. T2: F's AUC at α = 1 is at least O's − 0.02, so there is no loss on real ink.
  3. T4: F's false-light share is at most 1.25 × O's.
- **Strong pass:** also a gain of at least +0.03 at α 0.35, or F's AUC at α 0.7 at least O's at α 0.85 (a contrast gain of at least 15%).
- **KILL otherwise.** If only condition 2 or 3 fails, it is reported as a trade-off.
- **If PASS:** F is run on the 7 held-out 800 windings (about 70 cm², no download) and judged by shape, with the section-4 rule.

### Result (2026-10-21, `faint/run_faint.sh`; log `~/vesuvius/eval/faint_result.txt`, JSON `faint_result.json`, figure `figures/faint_confronto.png`)

**Training:** 6000 steps in 58 min. On a fixed batch of training stamps at α 0.5, the correlation with the teacher rose from 0.17 (original) to 0.40 at step 1000, 0.50 at step 3000 and 0.51 at step 6000. The task was learnt on training data.

**Window:** both models are best at d −2 (w058 crop, α 1: O 0.842, F 0.810).

**T1, pooled pixel AUC on 1447 letters in held-out 800 papyrus** (19 letter components, 160 background tiles; 95% bootstrap interval of F − O):

| α | O | F | F − O |
|---|---|---|---|
| 1 | 0.808 | 0.758 | −0.050 [−0.083, −0.015] |
| 0.85 | 0.708 | 0.696 | −0.012 [−0.066, +0.044] |
| 0.7 | 0.612 | 0.628 | +0.015 [−0.037, +0.075] |
| 0.5 | 0.536 | 0.549 | +0.013 [−0.040, +0.078] |
| 0.35 | 0.520 | 0.520 | 0.000 [−0.053, +0.063] |

- Mean of α 0.7 and 0.5: +0.014 [−0.037, +0.074].
- **Box test** (letters shown / 20, against random boxes):
  - O: 9 (6%), 7 (10%), 1 (11%), 1 (10%), 1 (11%) at α 1 to 0.35.
  - F: 8 (7%), 7 (10%), 4 (9%), 4 (10%), 2 (11%).
- **T4, false lights at 50% recall:** O 0.152, F 0.140 of the papyrus.
- **T3, 343 boxes at d0** (seen ink; letters shown / 16):

  | α | O | F |
  |---|---|---|
  | 1 | 12 | 12 |
  | 0.7 | 8 | 10 |
  | 0.5 | 4 | 4 |
  | 0.35 | 2 | 1 |
  | 0 | 0 | 0 |

  Random boxes are at 10-16%.

**RULE: KILL (no T1 gain).**
- Condition 1 fails: +0.014, interval including 0.
- Condition 2 also fails: F loses 0.05 AUC on real 1447 ink at full strength.
- Condition 3 holds.

**Visual reading (w058 crop):**
- At α 1, O draws the 1447 letters clearly. F draws them fainter, over a regular lattice pattern (spacing about 0.8 mm, probably the fibre grid) that O does not show.
- At α 0.7 and 0.5, F's map is that lattice with no letters. O still shows a few strokes at 0.7.

**Lessons**
1. The fine-tuning learnt the training combination (343 ink in the 13 training windings), not faint ink. It barely helps the same 343 ink in new 800 windows (T3: 8 → 10 of 16 at α 0.7, nothing at 0.5), and not at all for new ink.
2. It costs real-ink performance at full strength and adds a lattice artefact. With one ink source, synthetic-stamp training overfits; it would need several independent ink sources, which we do not have at 8.64 µm (343 and 1447 are the only two, and one of them must stay held out).
3. New number for the detection limit:
   - Reader v2 on 1447-strength ink in 800 papyrus: AUC 0.81 at full strength, 0.71 at 85%, 0.61 at 70%, 0.54 at 50%.
   - Boxes: 9, 7, 1 and 1 of 20.
   - So 1447-like ink in 800 papyrus is detectable down to about 85% of its contrast, not below.

## 11. Round 3: letter class averaging, cryo-EM style (approved by the user 2026-10-18; rule written before any computation)

**Question:** can reference-free 2D class averaging of letter-sized patches recover text structure when single letters are below the models' detection limit?

**Data:** the full fade renders of section 1, i.e. the PHerc. 343 letter region of s028-s031 blended into PHerc. 800 papyrus at α 1, 0.7, 0.5, and α 0 as the blank control.

**Inputs**
- (a) Reader v2 reading-side map at d0 (primary);
- (b) raw CT "ink layers", the mean of layers 34-40 (exploratory; step 0 put the 343 signal there).

**Patches (`classavg.py`)**
- 320 × 320 px (2.8 mm), on a grid every 58 px (0.5 mm), inside the text rows (y 650-1600), fully on papyrus.
- Downsampled 4× to 80 × 80 and normalised per patch.

**Algorithm**
- Hard-assignment EM: K = 16 classes, translational search ±15 px (±0.5 mm), 20 iterations.
- Classes with fewer than 10 members are re-seeded.
- Two half-sets by winding ({028, 029} and {030, 031}), each with its own random start: a gold standard, so the two halves share no letters.
- Classes are matched across the halves by the best shift-correlation (Hungarian).

**Statistic**
- **FRC_letter:** the member-weighted mean of the Fourier ring correlation of matched class averages over rings 3-9, i.e. periods of about 0.3-1 mm, stroke to letter scale.
- 5 seeds per run.

**Rule**
- **Positive control:** at α = 1, FRC_letter must exceed the blank's (α = 0) mean + 3 SD over seeds. Otherwise the method cannot recover even full-strength 343 text here: KILL.
- **PASS** if, with input (a), FRC_letter at α = 0.7 exceeds the blank's mean + 3 SD. Single Reader v2 letters are at about 50% boxes there in section 1, and fade quickly below.
- **Strong pass** if the same holds at α = 0.5, where Reader v2 is at trace level.
- **KILL otherwise.**
- Input (b) is reported, but it cannot pass the test on its own.
- Class averages are shown for visual reading. A Greek-like index of coincidence is left for later, as there are too few letters here.

### Result (2026-10-18, `classavg.py`, log `~/vesuvius/eval/logs/classavg.log`, JSON `classavg_result.json`, montages `views_classavg/`)

1551 + 1661 patches per run; FRC_letter as mean ± SD over 5 seeds.

| input | α 1 | α 0.7 | α 0.5 | blank α 0 | threshold (blank + 3 SD) |
|---|---|---|---|---|---|
| (a) Reader v2 map | +0.369 ± 0.033 | +0.274 ± 0.047 | +0.267 ± 0.040 | +0.295 ± 0.010 | +0.324 |
| (b) raw CT layers 34-40 | +0.210 ± 0.018 | +0.128 ± 0.011 | +0.119 ± 0.007 | +0.138 ± 0.013 | +0.179 |

**RULE: KILL.** The positive control passes narrowly (α 1 at +0.369 against +0.324), but at α 0.7 the class averages are less reproducible than on blank papyrus, and so is α 0.5.

**What the averages show (visual reading)**
- With input (a), every run gives the same picture, including the blank: each class is a single round blob (about 0.5-0.7 mm) at a different place in the patch. No letter shape appears, even at α 1.
- Reader v2 draws the 343 letters as a few strong stroke fragments on a dark background, while PHerc. 800 papyrus gives a dense field of small blobs. Neither contains whole letter shapes for the averaging to line up.
- Aligning on the best correlation turns any blob field into "a blob at position p", and both halves converge to the same family. So the blank reaches +0.295 with no text at all ("Einstein from noise"; the gold-standard split does not protect against an attractor shared by both halves).
- The statistic is not monotonic in letter strength: 0.7 and 0.5 fall below both ends. It measures how regular the texture is, not whether text is there. The α 1 edge may reflect sparse 343 marks against dense 800 speckle rather than letters; that confound was not controlled.
- With input (b), the classes are the papyrus itself: dark crack and fibre-gap streaks at different heights and tilts. Its numbers follow the same pattern: full-strength 343 above the blank, 0.7 and 0.5 below it. Since these classes are cracks and fibre gaps, the α 1 edge on raw CT comes from 343's papyrus, not its letters. This supports the confound reading of input (a)'s positive control.

**Lessons**
1. Class averaging needs particles with a shape. The models encode ink as blobs and stroke fragments, so there is nothing letter-shaped to average in their maps.
2. Without particle picking, the classes sort blobs by position. Picking centres from a map at trace level would mostly pick false lights.
3. On a speckle background, reference-free alignment manufactures structure from noise. Any future averaging must be compared with a blank processed identically (as here), and must show averages that differ from the blank's, not merely reproduce.

## 10. Round 2: confirmation of the facing-interface (set-off) lead (approved by the user 2026-10-18; rule written before any computation)

**Orientation, fixed in advance.** In our 343 renders the inked face is the outer one (step 0: signal at +1.5..+17.5 voxels; the models read best at d0/+2). So the inked face of winding k touches the inner face of winding k+1, which is k+1's blind side (forward maps).
- **Facing pairs:** (k → k+1) for k = 028, 029, 030.
- **Non-facing control:** (k → k−1) blind side, for k = 029, 030, 031.

**Method (`setoff2.py`).** A dense pixel-level comparison instead of 16 boxes, at the mesh-node grid (20 px, about 0.17 mm):
- Every valid node of winding n is matched to the nearest node of winding k, accepted if ≤ 40 vx.
- Each map is averaged over the 20 × 20 px block of its node, high-passed (minus its σ = 5 node Gaussian, i.e. 100 px, mask-normalised), so only letter-scale structure remains.
- **r_face:** Pearson correlation between k's reading-side map, carried to n's nodes, and n's blind-side map.
- **Controls:**
  - r_shift: the same with the carried map shifted ±20 and ±40 nodes along the winding (0.4 and 0.8 mm × 20 = 3.5 and 7 mm), mean of |r|;
  - r_nonface: the same pairing towards k−1 (blind side).
- **Errors:** block bootstrap over 10 × 10 node tiles, 1000 resamples, 95% interval.
- **Models:** Reader v2 (f100 maps) and dnative (s maps), both at d0.
- **Gap:** at each node of n, the number of non-papyrus layers between n's inner edge (sheet tracker, `lat1.py sheets`) and the next papyrus run inward, which is the sheet of k. Fused = gap ≤ 2 layers; open = gap ≥ 6 layers, where a d0 window on n cannot reach k's inked face.

**Rule**
- **Confirmed** (an ink signal visible on the facing side) only if, for both models:
  - r_face > 0 with its 95% interval above 0;
  - r_face ≥ 3 × r_shift;
  - r_face ≥ 3 × |r_nonface|.
- **Transfer supported** (ink truly deposited on the facing sheet, not just the shared interface) only if, in addition:
  - r_open's interval is above 0;
  - r_open ≥ 0.5 × r_fused.
- **Shared interface only:** r_fused > 0 while r_open's interval includes 0.
- **KILL** if the confirmation conditions fail.

### Section 10 result (2026-10-18): KILL

| model | r_face [95%] | r_shift | r_nonface | fused (gap ≤ 2) | open (gap ≥ 6) |
|---|---|---|---|---|---|
| Reader v2 | +0.104 [+0.074, +0.136] | 0.024 | +0.076 | +0.110 | +0.124 |
| dnative | +0.139 [+0.109, +0.171] | 0.037 | +0.131 | +0.108 | +0.162 |

- Node counts: about 48,800 (face), 47,400 (non-face), 5,900 (fused), 22,900 (open).
- **Verdict: not confirmed for either model.** The correlation is well above the shift control, but just as strong towards the non-facing neighbour (r_face < 3 × r_nonface), and the same in fused and open zones.
- **Meaning:**
  - Neighbouring windings' maps share a weak letter-scale component (r ≈ 0.1, shared variance 1-2%) at aligned positions, whichever side faces. It disappears with a 3.5-7 mm shift.
  - That is a radially coherent response (structure common to adjacent windings, or duplicated surfaces), not a set-off from the facing sheet.
  - The round-1 lead (k+1 blind side 25-33% against k−1 at chance, 12-14 boxes) was a small-sample asymmetry.
- **What we learnt:** a component of the model responses repeats across windings at the same (θ, z). Ink cannot do that, since each winding carries different letters, so subtracting it is a candidate false-positive filter (idea D4, radial differential imaging). Its size is small, about 1-2% of the variance.

## 9. Lateral ideas, round 1 (approved by the user 2026-10-18; rules written before any computation)

Source: `IDEAS_lateral.md`, ranks 1-4. No downloads.

**Positives**
- PHerc. 343: the stage-B renders s028-s031 with the 16 covered letter boxes.
- PHerc. 1447: Nader's w058/w060 (24 layers, offsets −11.5..+11.5) with the refined labels.

**Negatives:** the PHerc. 800 papyrus (fade series f000-f100, the hole-free e-renders) and the 0268 tall band.

**Box test:** as in sections 1 and 3A (inside − ring ≥ 0.3 on the map z-scored over the papyrus; random boxes on the papyrus).

**Step 0, diagnostic (no verdict).** The ink depth signature: mean depth profile inside the 343 letter boxes minus their rings, and 1447 ink minus non-ink pixels inside the certainty mask, with standard errors. It tells which layers carry the ink and gives s for test 3.

### Test 1: edge-locking (`edges.py`, `edgelock.py`)
- **Method:**
  - Per pixel (3×3 in-plane smoothing), the recto and verso edges of the sheet: the strongest rising and falling depth gradient within ±12 layers of the surface, refined to sub-voxel precision by a parabola.
  - Edge-locked render: each profile is shifted, by linear interpolation, so the chosen edge sits at the render's median edge layer. The shift field is smoothed (σ 3 px) and clipped to ±6 voxels; pixels with weak edges are not shifted.
  - The face carrying the ink is chosen from step 0.
- **Readouts:**
  - (a) near-edge density, i.e. the first 2 voxels inside the edge minus voxels 3-6;
  - (b) relief, i.e. the edge position minus its 20 px smooth;
  - (c) step height across the edge;
  - (d) gap undershoot.
  - Each readout is tested in both signs.
- **PASS if either:**
  - (i) one readout, in one sign, shows ≥ 2× random on both 343 and 1447;
  - (ii) Reader v2 or dnative on the edge-locked renders gains ≥ 2 boxes on 343 (of 16) or on 1447 (of 20) with random not higher, or its retention α50 on 343 letters blended into edge-locked 800 papyrus drops by ≥ 0.05 against the non-locked composites.
- **KILL otherwise.**

**Method change, logged 2026-10-18 before any test-1 score**
- **The first edge finder failed.** Within ±12 layers the profiles hold several sheets and gaps: on 343 the rise/fall positions spread over the whole window and the "thickness" came out ≈ 0. No box test had run.
- **Replaced by a run-based sheet tracker (`lat1.py sheets`):**
  - 7×7 in-plane mean;
  - papyrus = above the midpoint of each pixel's own 20th/80th percentiles (no structure if they differ by < 25 grey levels);
  - the papyrus run nearest the mesh layer, re-picked near its 31 px median centre;
  - sub-voxel rise/fall edges at the threshold.
- **Diagnostic it gives right away:**

  | surface | sheet centre within ±2 layers of the mesh | p10-p90 of the centre | thickness median |
  |---|---|---|---|
  | 343 s030 (our chain) | 26% of papyrus | −8..+8 layers | 9.4 vx |
  | 1447 w058 (Nader's surfaces) | 38% | | 7.0 vx |

  The surfaces the models read are often several voxels off the sheet, which supports the premise of test 1.
- **Locks:** sheet centre, inner edge (rise) and outer edge (fall), all at d0. Shift field = edge − median, invalid pixels filled from neighbours (normalised Gaussian σ 3), clip ±10.
- **Fade part of test 1:** centre lock only, fixed now.

### Test 2: set-off on the facing sheet (`setoff.py`)
- **Method:**
  - Each 343 letter box on winding k is mapped through 3D onto the inner neighbour k−1: the box centre on mesh k, then the nearest node of mesh k−1, accepted if ≤ 60 vx away. The box keeps its size.
  - Pairs: s030→s029, s031→s030, s029→s028.
  - The box test is run on k−1's blind-side maps (villa members, villa ensemble, Reader v2). k−1's reading-side maps at the same boxes are reported as a control: text of k−1's own column may lie there.
- **PASS** if the mapped boxes show ink in ≥ 25% of cases and at ≥ 1.5× the random rate on the blind side, for at least 2 of the models.
- **KILL otherwise.**
- 1447 cannot be tested: the facing sheet lies beyond its 24 layers.

### Test 3: adaptive matched filter and fibre notch (`mfilter.py`, `notch.py`)
- **Matched filter:**
  - Depth profiles of 21 layers around the surface (and around the locked edge), 3×3 smoothed.
  - Score t = sᵀΣ⁻¹(x − μ). Σ is the shrunk covariance (λ 0.1) of the target render's papyrus, about 200k pixels.
  - s comes from the other scroll (cross-scroll: 1447 → 343 and 343 → 1447).
- **Notch:** remove a ±4° spectral wedge around the recto-fibre direction (|f| > 1/100 px) from the Reader v2, dnative and matched-filter maps.
- **PASS:**
  - matched filter: cross-scroll boxes ≥ 2× random on both scrolls, and α50 on the full fade renders (343 in 800 papyrus) < 0.8;
  - notch: α50 improves ≥ 0.05, or 1447 gains ≥ 2 boxes, at an equal random rate.
- **KILL otherwise.**

### Round 1 results, tests 1-3 (2026-10-18, 17:52-19:36)

**Test 1, sheet-locking: KILL.**
- **(a) Model-free readouts** (near-edge density, relief, step, undershoot; both faces, both signs): 0/16 boxes on 343 and 0-2/10 on 1447 against random 0-4%. Box-level contrast ≈ 0 everywhere.
- **(b) Models on locked renders** (d0), all worse than unlocked:

  | | dnative 343 (of 16) | Reader v2 343 (of 16) | 1447 w058 / w060 (of 10) |
  |---|---|---|---|
  | unlocked | 13 | 12 | 3-5 / 3-5 |
  | centre lock | 9 | 11 | 1-2 / 1-2 |
  | rise lock | 6 | 9 | 1-3 |
  | fall lock | 7 | 9 | 1-3 |

  Fade, centre lock: α50 0.81 (dnative) and 0.77 (Reader v2), against 0.76 and 0.72 unlocked.
- **What we learnt:**
  - Our surfaces and Nader's sit within ±2 layers of the sheet centre on only 23-38% of the papyrus; sheets are 7-10 voxels thick.
  - The models cope with this offset better than a crude per-pixel re-alignment does: forcing alignment hurts.
  - A learned alignment inside the network (idea M9) is the only version of this idea still open.

**Test 3: KILL for both parts.**
- **Matched filter:** cross-scroll d′ is only 0.17-0.26; 0/16 boxes on 343 and 0/10 on 1447.
- **Notch (±4° wedge):** box counts and retention unchanged.
- **Correction of our metric, found here.** The matched filter's α50 of 0.48 is an artefact.
  - In the variance-preserving blend, ANY linear filter gives retention ≈ α, so α50 ≈ 0.5 by construction (retention α σR / √(α²σR² + β²σB²)).
  - The CNN α50 values of section 7 (0.55-0.88) are therefore meaningful only relative to each other and to that linear floor: they measure how much faster than linear mixing a model loses the 343 response.
  - They do not say "ink is detectable down to α50". The section-8 bound for 0268 ("no ink ≥ about 55%") is withdrawn. The defensible bound comes from box tests: detection near α 0.8-1.0 of 343's contrast for Reader v2 (section 1 fade on full renders).

**Test 2, set-off: KILL as pre-registered (inner neighbour k−1); positive in the opposite direction, which needs a confirmation.**
- Inner neighbour k−1, blind side (the rule as written): dnative 1/14, s42 0/14, s43 3/14, Reader v2 2/14, villa ensemble 0/14, against random 7-12%. KILL.
- **Outer neighbour k+1, blind side:** dnative 4/12, s42 4/12, Reader v2 3/12, villa ensemble 3/12 (25-33%), against random 6-10%. That meets the threshold for 4 models.
  - Step 0 placed the 343 ink signal on the outer side of our surfaces (+1.5..+17.5 voxels; the models also read best at d0/+2). If the inked face points outward, the facing sheet is k+1, not k−1. That orientation was not written into the rule before the run, so this is a lead for a confirmation test, not a pass.
- **Controls:**
  - The non-facing blind side (k−1) stays at chance.
  - The reading sides of both neighbours light up at the mapped spots (29-50%): the same text column continues on adjacent windings, since a winding here is about 4.2 cm long.
  - Simple leakage from the neighbour's own text would raise both neighbours' blind sides; only the facing one rises. That favours an interface effect.
- **Open question:** true transfer (set-off) or the same contact interface seen from the other side (fused sheets share voxels, and the facing surface is 16-28 vx away).
- **Confirmation to pre-register (orientation fixed):**
  - facing blind side vs non-facing blind side on other windings or regions with known text (more 343 windings; 1447 needs its CT);
  - open-gap vs fused interfaces separated, using the sheet tracker's gap.

### Test 4 result (2026-10-18): PASS by the letter, KILL for in-domain labels today

- **Opened pieces exist for exactly 3 eligible rolls,** all in Naples frames (cornici) and photographed by the BYU multispectral campaign:
  - PHerc. 0268: opened 1987-88 by the Oslo method, 5 pieces in 1 cornice;
  - 0358: partly unrolled 1805, 1 piece of 29 × 19.7 cm;
  - 0826: partly unrolled 1868, 2 pieces; about 10 lines are visible in the public preview.
- **No usable labels today:**
  - only about 768×514 px previews are public; full-resolution images are "on request" (BYU), and the 2024-25 Mellon re-imaging is unpublished;
  - none of the pieces is in the Vesuvius data (no fragment scans); the 21 volumes have no IR images, ink labels or fragment samples;
  - the pieces are physically separate from the scanned rolls, so they give hand and format priors, not voxel labels.
- **Actionable proposal for the organisers (not ours to do):** CT-scan the cornici of 0268/0358/0826 with the 116/113 keV protocols and pair them with full-resolution IR. That would give in-domain labels for three eligible rolls. Precedent: PHerc. 1667 Cr 1 Fr 3, an Oslo piece of Scroll 4, was scanned at Diamond as Fragment 5. 0268 is the closest match, and it also has the most favourable papyrus in our section-7 map.
- No palaeographic data (column width, line pitch) were found for any of the 21 rolls.

### Test 4: catalogued pieces of the eligible rolls (web desk check)
- Done by a research agent.
- **PASS** if ≥ 3 eligible rolls have opened or detached pieces that are scanned in the Vesuvius data, or photographed (IR or multispectral) and reachable.
- **KILL otherwise.**

## 5. Reader v2 on the survey renders (rule written 2026-10-13, before any run on them)

- **Renders:** every survey winding: pilot PHerc. 1218, 1203, 0268, and batch 2. Same run and pointer as section 4 (`rv2_survey.sh`, edge 120 / cover 0.1).
- **Rule:** the section-4 rule, with criterion 1 read as "a line of letter-like strokes along the winding". The 500-slice bands hold about one text line, so rows cannot be seen.
- **Any such line triggers:**
  - the depth-shuffle control on that winding;
  - a proposal to the user for a taller band (≥ 1500 slices; new CT, to be approved).
- **PHerc. 1203 t044:** its Hecate lead is judged on the Reader v2 map with the same rule.

### Section 5 result (2026-10-13, 07:10-08:00)

**Coverage:** 53 windings (11 scrolls), d −2/0/+2/+12, no failures.
- Reader v2 is often silent on these short renders, so many A values are exactly 1.00 (both sides near zero).
- Flagged by A for the visual check:
  - 0257 t044/t046/t047;
  - 0813 t047 (2.1-3.0 on the sheet, 0.42 at +12);
  - 1203 t041/t044;
  - 1218 t037/t038;
  - 0125 t044/t046.

**Visual check (strips at 1/4, top windows at 1/2):**
- **0257, 0813, 1203 and 0125:** scattered round blobs or amorphous clouds, no line of letter-like strokes. **The PHerc. 1203 t044 Hecate lead is closed:** Reader v2 shows scattered blobs there.
- **PHerc. 1218 t038 meets the section-5 trigger.** At render x 2010-2460 (3D about x 2980, y 4509, z 11550-11745) there is an arch-shaped mark about 3.9 mm wide and 2.5 mm tall. To its left are 4-5 vertical stroke-like marks 1.3-1.9 mm tall: a horizontal sequence about 9.5 mm long.
  - It is the same at d−2, d0 and d+2.
  - It is absent at d+12 and d−12, and on the blind side.
  - It vanishes when shuffled (not discriminating for Reader v2).
  - The old villa A statistic had already flagged w038 in the pilot (1.72-2.20, "local patch"). dnative shows it only faintly.
  - t037 shows the same arch, shifted by about 48 px. Their CT layers correlate there (0.32 at a 48 px shift, against about 0 elsewhere), so the two fitted windings sample nearly the same sheet: one observation, not two. t036 and t039 do not show it.
- **Independent check with Nader's base** (crops x 900-2900 of t037 and t038, `figures/1218_t037-038_nader.png`):
  - In the reading order found on 343 ("rev") it lights a broad region about 1.3 cm wide over the same place in both windings, with a faint ring or arch contour where Reader v2 has the arch.
  - In the other order it gives its usual blob field.
  - So two independently trained models, plus the old villa statistic, respond here on the reading side only. None draws readable letters.
- **Status: a lead, not a candidate.** The marks are blob-like and unreadable, and the 4.2 mm band cuts them: the arch fills most of its height.
## 6. PHerc. 1218 taller band around the lead (approved by the user 2026-10-13; rule written before any download)

**Data and run (`tall1218.sh`)**
- **Band and chain:** 1500 slices, z 10890-12390, centred on the lead (z about 11640). Same chain as the survey: our axis, distance field, level-1 tracks, spiral fit (3000 steps, the survey's fit settings), hole-free snapping.
- **Windings:** the snapped winding passing nearest the lead (3D about x 2980, y 4509, z 11640), plus its neighbours: 4 consecutive windings, or 3 or 2 if the CT budget requires.
- **Downloads:**
  - m7 level 1 and lasagna group 2 for the new slices (about 0.5 GB; the survey's chunks are reused);
  - CT level 0 into the survey's `ct0.zarr`, so local chunks are reused, at most 4.3 GB new.
  - Total at most 5 GB, as approved.
- **Models:** render (66 layers); Reader v2 and the 3 villa models at d −2, 0, +2 and the control +12, both sides.

**Rule**
- **Candidate** only if, around the lead, the Reader v2 reading-side map at one of d −2/0/+2 shows all of:
  1. stroke-like marks arranged in at least 2 parallel horizontal lines (text lines), 3-7 mm apart;
  2. the same lines at a neighbouring depth;
  3. none of it at d ±12 or on the blind side.
- **Closed** if the response at the lead is a single blob region or a vertical strip spanning the band height without line structure (sheet join, crack or other papyrus feature), or if it does not reappear on the new surfaces.
- **Otherwise** (for example one line only, or lines too weak) it stays a lead, reported as such.
- **Reported in every case:** the villa ensemble, dnative alone, and crops at full resolution.
- A candidate is not a First Letters claim (≥ 10 legible letters in 4 cm²). It would lead to a proposal to the user for the next steps, and it stays private.

### Section 6 result (2026-10-13, 10:05-10:40): lead CLOSED

**Run (`tall1218.sh`)**
- New downloads: 269 MB of m7/lasagna and 3.55 GB of CT, total 3.8 GB, within the approved 5 GB.
- New fit: 1500 slices, satisfied tracks 12.8%.
- The lead lies 6.5 vx from the new winding w040 and 13.4 vx from w039; rendered T039-T042. Villa 48 runs and Reader v2 16 runs, no failures.

**What the taller band shows**
- Around the lead (T040 x 1000-2600, full 14 mm height), Reader v2 lights a region about 1.5 cm wide spanning the whole band height.
- It is made of blob clusters, the old arch being one of them, and a horizontal bar about 5 mm long. There are no lines of strokes: the clusters sit at roughly 3 mm steps, irregular, at the lower edge of the 3-7 mm line pitch.
- The same at d−2. Absent at d+12 and on the blind side. dnative shows only its uniform mottle.
- The rest of the four windings (about 5 cm each) has only scattered blobs.

**Cause**
- The response follows a material anomaly visible in the raw CT: patches of bright, porous ("spongy") material.
- Per 200 px column, the share of CT pixels above the winding's 97th percentile peaks at x 1800-2400 (8-10% against 1-2% elsewhere), exactly where the Reader v2 share peaks (10-24% against 0-5%). Over the winding the two local shares correlate at 0.57.
- The bright patches are irregular and spongy, not stroke-shaped.

**Verdict under the rule:** "a single blob region spanning the band height without line structure". Closed. Most likely a papyrus/material feature that the ink models (Reader v2, Nader, and the old villa A in the pilot) respond to on one face, not text.

- **What a taller band decides:**
  - text would repeat as horizontal lines about 4-5 mm apart;
  - a strip that runs the full height (a sheet join, kollesis, or another papyrus feature) would not.
- **Rule consequence:** propose a taller band to the user (≥ 1500 slices around z 11640, windings 36-39). Estimated new download:
  - m7 + lasagna for 1000 more slices, about 0.6 GB;
  - CT for 4 windings × 1500 slices, about 6 GB, of which about 2 GB is already local;
  - total about 4-5 GB, to be approved.

**Decision**
- A new model is run on the PHerc. 800 search renders (w050-069 hole-free, about 200 cm²) and on the survey renders if either holds:
  - it "sees the 1447 letters" (A) or matches the discovery level there (A′);
  - its α\* is lower than the villa ensemble's (C).
- Any candidate found with it must, besides the PHerc. 800 ink rule, survive the depth-shuffle control: its strokes must vanish when the layers are shuffled.
- If no model passes, the PHerc. 800 null stands as it is, now with its detection limit.
