# Results behind REPORT.md

Numbers only (AUCs, bootstrap intervals, clutter indices, sheet and texture statistics). No labels, masks or images. Paths inside the files are relative to our data root. T1 = the main bench (PHerc. 1447 letters in PHerc. 800 papyrus); T1b = the same letters in other 800 windings.

| file | round | what |
| --- | --- | --- |
| `setoff2_result.json` | 2 | set-off on the facing winding |
| `classavg_result.json` | 3 | class averaging of letter-sized patches |
| `faint_result.json` | 4 | fine-tuning on faint 343 stamps; T1 bench, Reader v2 |
| `r5_audit.json`, `r5_noise.json`, `r5_gap.json`, `r5_specks.json`, `r5_wise_result.json` | 5 | logit audit, noise-versus-clutter budget, recto gap, lead specks, WiSE-FT |
| `r6_result.json` | 6 | in-domain fine-tuning on 1447 letters (ceiling probe) |
| `r7_result.json` | 7 | column periodicity |
| `r8_disbond.json` | 8 | gap to the next winding |
| `r9_result.json` | 9 | areal mass under ink; edge width |
| `r10_ensemble.json`, `r10_scale.json`, `r10_depth.json` | 10 | model families and α₀.₆₅; scale and phase tests; depth fingerprint |
| `r11_result.json` | 11 | depth-profile peakedness filter |
| `r12_rank.json`, `r12_local.json`, `r12_density.json` | 12 | readability of 12 scrolls (1447 letters, Reader v2); quiet zones; density |
| `r13_result.json` | 13 | noise or structure in the 9.362 µm scans |
| `r17_screen.json` | 17 | PHerc. 0268 stage-2 tile screening (Reader v2) |
| `r18_t1.json`, `r18_rank.json`, `r18_screen.json` | 18 | Reader V3: T1 bench, readability, search screening |
| `r19_result.json` | 19 | texture inside sheets against at edges; fringes; edge widths |
| `r20_align.json`, `r20_rank.json` | 20 | PHerc. 0841 ink: alignment and readability with Reader v2 and V3 |
| `r21_result.json` | 21 | blur-matched readability, four combinations |
| `r22_result.json` | 22 | sheet check: PHerc. 0268 against 800 |
| `r23_result.json` | 23 | ring and spectral-tilt signatures in raw CT |
| `r24_result_run1.json`, `r24_result_27-w00.json` | 24 | 0841 at 9.37 µm: 113 keV / 1.2 m scan against the downsampled 77 keV / 0.22 m scan. The first run is valid for the auto-grown segment only; w00 was rerun on its labelled half |
| `per_scroll.csv` | 21 (post hoc) | the 12-scroll table: campaign, clutter index, AUC at α 1 / 0.85 / 0.7 in the four combinations, difference to PHerc. 800 with 95% interval |
| `r25_1447.json`, `r25_0841.json` | 25 | pipeline control: survey renders of 1218 and 0268 with the round-18/20 bench, Reader V3 |
| `r26_1447.json`, `r26_0841.json` | 26 | voxel-size control: native and resampled (8.64 ↔ 9.362 µm) survey renders, cut crops |
| `r27_stats.json`, `r27_result.json` | 27 | texture statistics per render and their Spearman correlation with AUC (clutter index against simpler measures) |
| `r28_result.json`, `r28_posthoc.json` | 28 | ideal linear observer (Hotelling on 3D patches) against Reader v2 and V3 on T1: AUC per α, gain with bootstrap, controls, d′; post-hoc in-sample, same-winding and depth-shift diagnostics |
| `r29_result.json` | 29 | power-law exponent β of the papyrus clutter (renders of 14 sources) and of the Reader V3 maps on blank papyrus, with spectra, intervals, two-band slopes and the size law |
| `r30_result.json` | 30 | PHerc. 0139 original against the pag0 and pag50 re-retrievals: renderer check, label-free physics per reconstruction, native-ink AUC of Reader v2 and V3 with paired bootstrap. The file's `verdict` field records the unamended INVALID of the renderer check (the official w044 render is offset by 12 px); the amended check and the WORSE OR AMBIGUOUS verdict are in the preregistration log, section 38 |
| `r31_result.json` | 31 | in-plane deconvolution before inference: seven variants on T1b, the primary and the unsharp baseline on T1 with Reader V3 and v2 |
| `r32_result.json` | 32 | PHerc. 0841 letters at 9.366 µm (Reader V3, v2) and 2.403 µm (canonical 2 µm model) blended into the same blank papyrus: fits, native AUC of the 2 µm port, AUC per α, α₀.₆₅, equivalent contrast, bootstrap |
| `tx_demo.txt` | tools | tifxyz adapter on the three official PHerc. 0841 segments: renderer check against the official surface volumes, sheet check |
| `tx800_demo.txt` | tools | the same on the six official PHerc. 800 segments (8.64 µm) |
