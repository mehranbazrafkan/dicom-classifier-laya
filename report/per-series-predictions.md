# Per-series predictions (all 36 series)

Every row is one DICOM series that was sent to the Laya decision model. Values are `answer (top-1 probability)`; the probability is the model's own confidence for the choice it made, taken from the raw log.

Scoring columns:

- **Expected datatype / suffix** — derived from the vendor `SeriesDescription` / `ProtocolName`, which in this dataset already contain BIDS-style names (e.g. `ses-pre_T1w`, `task-uebung_bold`, `acq-15_dir-ap_dwi`). This is a sanity-check proxy for ground truth, not an independent annotation.
- **`n/a`** — the series has no BIDS equivalent (localizer, DICOM SR report, physiology log), so it is excluded from the accuracy numbers.
- **`—`** — field not scored (the description does not pin down a single value, e.g. which `fmap` suffix a field-map series should get).

**Headline:** datatype `19/21` (90%) correct · suffix `2/15` (13%) correct — see [results.md](results.md) for the analysis.

## Study 1

`1.3.12.2.1107.5.2.43.66080.30000025052607162980300000005` — 9 series

| # | Series description | Kind | DICOM files | Expected datatype | Expected suffix | datatype | suffix | part | dir | run | echo | flip | inv | mt |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | localizer_20ch_head-coil | localizer (not BIDS) | 2 | n/a | n/a | anat (0.23) | phase2 (0.40) | phase (0.36) | i (0.50) | 1 (0.44) | 1 (0.54) | 1 (0.39) | 1 (0.30) | on (0.77) |
| S99 | PhoenixZIPReport | DICOM SR report (not BIDS) | 6 | n/a | n/a | anat (0.31) | phase1 (0.51) | phase (0.46) | k (0.31) | 9 (0.41) | 1 (0.39) | 1 (0.32) | 1 (0.37) | on (0.63) |
| S2 | ses-pre_run-01_fmap | field map | 2 | **fmap** | — | fmap (0.24) ✔ | phase2 (0.58) | phase (0.38) | i (0.29) | 1 (0.30) | 1 (0.39) | 1 (0.29) | 2 (0.25) | on (0.62) |
| S3 | ses-pre_run-01_fmap | field map | 1 | **fmap** | — | fmap (0.24) ✔ | phase2 (0.50) | phase (0.38) | i (0.31) | 1 (0.36) | 1 (0.43) | 1 (0.27) | 1 (0.27) | on (0.65) |
| S4 | ses-pre_task-sparse_bold | functional | 10 | **func** | **bold** | func (0.29) ✔ | phase2 (0.50) ✘ | phase (0.40) | i (0.27) | 1 (0.26) | 1 (0.30) | 4 (0.21) | 4 (0.22) | on (0.59) |
| S6 | ses-pre_T1w | structural | 1 | **anat** | **T1w** | anat (0.27) ✔ | T1w (0.98) ✔ | phase (0.42) | k (0.33) | 1 (0.28) | 9 (0.49) | 1 (0.25) | 1 (0.28) | on (0.62) |
| S7 | ses-pre_run-02_fmap | field map | 2 | **fmap** | — | fmap (0.25) ✔ | phase2 (0.53) | phase (0.37) | i (0.30) | 7 (0.34) | 1 (0.23) | 1 (0.24) | 2 (0.26) | on (0.63) |
| S8 | ses-pre_run-02_fmap | field map | 1 | **fmap** | — | fmap (0.26) ✔ | phase2 (0.57) | phase (0.38) | i (0.33) | 8 (0.46) | 8 (0.39) | 1 (0.28) | 1 (0.26) | on (0.66) |
| S9 | ses-pre_task-rest_bold | functional | 20 | **func** | **bold** | func (0.35) ✔ | phase2 (0.61) ✘ | phase (0.41) | i (0.40) | 1 (0.15) | 1 (0.21) | 4 (0.25) | 4 (0.22) | on (0.63) |

## Study 2

`1.3.12.2.1107.5.2.43.66080.30000025052607162980300000007` — 10 series

| # | Series description | Kind | DICOM files | Expected datatype | Expected suffix | datatype | suffix | part | dir | run | echo | flip | inv | mt |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | AAHead_Scout_64ch-head-coil | localizer (not BIDS) | 1 | n/a | n/a | anat (0.23) | phase1 (0.41) | real (0.31) | i (0.46) | 1 (0.38) | 1 (0.38) | 1 (0.42) | 1 (0.30) | on (0.64) |
| S2 | AAHead_Scout_64ch-head-coil_MPR_sag | localizer (not BIDS) | 1 | n/a | n/a | anat (0.23) | phase2 (0.29) | phase (0.34) | i (0.45) | 1 (0.28) | 1 (0.32) | 1 (0.32) | 2 (0.28) | on (0.74) |
| S3 | AAHead_Scout_64ch-head-coil_MPR_cor | localizer (not BIDS) | 1 | n/a | n/a | anat (0.23) | phase1 (0.33) | phase (0.34) | i (0.53) | 1 (0.28) | 1 (0.29) | 1 (0.28) | 1 (0.24) | on (0.79) |
| S4 | AAHead_Scout_64ch-head-coil_MPR_tra | localizer (not BIDS) | 1 | n/a | n/a | anat (0.25) | phase1 (0.33) | phase (0.35) | i (0.53) | 4 (0.50) | 4 (0.29) | 1 (0.24) | 2 (0.23) | on (0.77) |
| S99 | PhoenixZIPReport | DICOM SR report (not BIDS) | 3 | n/a | n/a | anat (0.28) | phase1 (0.49) | phase (0.46) | i (0.33) | 1 (0.25) | 1 (0.37) | 1 (0.37) | 1 (0.50) | on (0.61) |
| S5 | ses-post_run-01_fmap | field map | 2 | **fmap** | — | fmap (0.26) ✔ | phase2 (0.43) | phase (0.37) | i (0.33) | 5 (0.37) | 1 (0.34) | 1 (0.24) | 2 (0.27) | on (0.64) |
| S6 | ses-post_run-01_fmap | field map | 1 | **fmap** | — | fmap (0.25) ✔ | phase2 (0.50) | phase (0.39) | i (0.31) | 6 (0.45) | 1 (0.35) | 1 (0.27) | 1 (0.24) | on (0.64) |
| S10 | ses-post_task-mb_bold_PhysioLog | physiology log (not BIDS) | 1 | n/a | n/a | func (0.26) | phase1 (0.35) | phase (0.37) | i (0.32) | 1 (0.18) | 8 (0.37) | 1 (0.31) | 1 (0.24) | on (0.61) |
| S7 | ses-post_task-mb_bold_SBRef | fMRI reference | 1 | **func** | **sbref** | func (0.28) ✔ | phase2 (0.57) ✘ | phase (0.36) | i (0.33) | 7 (0.40) | 1 (0.43) | 1 (0.25) | 1 (0.23) | on (0.56) |
| S8 | ses-post_task-mb_bold | functional | 50 | **func** | **bold** | func (0.32) ✔ | phase2 (0.63) ✘ | phase (0.34) | i (0.32) | 4 (0.16) | 8 (0.17) | 1 (0.22) | 4 (0.22) | on (0.63) |

## Study 3

`1.3.12.2.1107.5.2.43.66080.30000025052607162980300000009` — 17 series

| # | Series description | Kind | DICOM files | Expected datatype | Expected suffix | datatype | suffix | part | dir | run | echo | flip | inv | mt |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | AAHead_Scout_64ch-head-coil | localizer (not BIDS) | 1 | n/a | n/a | anat (0.23) | phase1 (0.39) | phase (0.31) | i (0.46) | 1 (0.38) | 1 (0.40) | 1 (0.43) | 1 (0.31) | on (0.68) |
| S2 | AAHead_Scout_64ch-head-coil_MPR_sag | localizer (not BIDS) | 1 | n/a | n/a | func (0.22) | phase2 (0.29) | phase (0.34) | i (0.44) | 1 (0.24) | 2 (0.28) | 1 (0.33) | 2 (0.27) | on (0.74) |
| S3 | AAHead_Scout_64ch-head-coil_MPR_cor | localizer (not BIDS) | 1 | n/a | n/a | anat (0.23) | phase1 (0.34) | phase (0.34) | i (0.49) | 3 (0.23) | 1 (0.29) | 1 (0.30) | 1 (0.26) | on (0.77) |
| S4 | AAHead_Scout_64ch-head-coil_MPR_tra | localizer (not BIDS) | 1 | n/a | n/a | anat (0.24) | phase1 (0.35) | phase (0.35) | i (0.47) | 4 (0.42) | 1 (0.22) | 1 (0.25) | 1 (0.24) | on (0.76) |
| S99 | PhoenixZIPReport | DICOM SR report (not BIDS) | 8 | n/a | n/a | anat (0.28) | phase1 (0.47) | phase (0.46) | k (0.30) | 9 (0.31) | 1 (0.37) | 1 (0.31) | 1 (0.33) | on (0.59) |
| S5 | acq-space_T2w | structural | 1 | **anat** | **T2w** | anat (0.24) ✔ | T2w (0.97) ✔ | phase (0.40) | k (0.31) | 5 (0.26) | 1 (0.28) | 1 (0.24) | 1 (0.25) | on (0.59) |
| S9 | task-dmaging_run-01_bold_PhysioLog | physiology log (not BIDS) | 1 | n/a | n/a | func (0.34) | bold (0.25) | phase (0.40) | i (0.36) | 9 (0.44) | 9 (0.42) | 1 (0.31) | 1 (0.26) | on (0.59) |
| S6 | task-dmaging_run-01_bold_SBRef | fMRI reference | 1 | **func** | **sbref** | func (0.29) ✔ | phase2 (0.54) ✘ | phase (0.35) | i (0.31) | 6 (0.42) | 1 (0.33) | 1 (0.26) | 2 (0.23) | on (0.53) |
| S7 | task-dmaging_run-01_bold | functional | 50 | **func** | **bold** | func (0.30) ✔ | phase2 (0.55) ✘ | phase (0.31) | i (0.33) | 1 (0.18) | 1 (0.23) | 1 (0.24) | 4 (0.23) | on (0.66) |
| S13 | task-dmaging_run-02_bold_PhysioLog | physiology log (not BIDS) | 1 | n/a | n/a | func (0.32) | phase1 (0.25) | phase (0.36) | i (0.32) | 1 (0.23) | 1 (0.29) | 1 (0.28) | 1 (0.24) | on (0.59) |
| S10 | task-dmaging_run-02_bold_SBRef | fMRI reference | 1 | **func** | **sbref** | func (0.28) ✔ | phase2 (0.44) ✘ | phase (0.33) | i (0.30) | 1 (0.28) | 1 (0.36) | 1 (0.27) | 2 (0.24) | on (0.55) |
| S11 | task-dmaging_run-02_bold | functional | 50 | **func** | **bold** | func (0.30) ✔ | phase2 (0.56) ✘ | phase (0.31) | i (0.34) | 4 (0.19) | 1 (0.19) | 2 (0.23) | 2 (0.23) | on (0.66) |
| S14 | task-uebung_bold_SBRef | fMRI reference | 1 | **func** | **sbref** | func (0.30) ✔ | phase2 (0.57) ✘ | phase (0.38) | k (0.31) | 1 (0.37) | 1 (0.42) | 1 (0.26) | 1 (0.23) | on (0.60) |
| S15 | task-uebung_bold | functional | 50 | **func** | **bold** | func (0.30) ✔ | phase2 (0.74) ✘ | phase (0.37) | i (0.33) | 4 (0.19) | 1 (0.15) | 5 (0.22) | 4 (0.25) | on (0.59) |
| S17 | acq-15_dir-ap_dwi | diffusion | 117 | **dwi** | **dwi** | func (0.26) ✘ | phase2 (0.57) ✘ | phase (0.42) | i (0.32) | 4 (0.23) | 1 (0.17) | 5 (0.24) | 1 (0.22) | on (0.66) |
| S18 | acq-15b0_dir-ap_dwi | diffusion | 1 | **dwi** | **dwi** | dwi (0.21) ✔ | phase2 (0.57) ✘ | phase (0.39) | i (0.30) | 1 (0.22) | 1 (0.34) | 1 (0.26) | 2 (0.22) | on (0.57) |
| S19 | acq-15_dir-pa_dwi | diffusion | 1 | **dwi** | **dwi** | func (0.25) ✘ | phase2 (0.72) ✘ | phase (0.40) | i (0.29) | 1 (0.26) | 1 (0.40) | 1 (0.26) | 3 (0.22) | on (0.60) |

---

[Back to the main report](README.md) · [Results analysis](results.md) · [Raw log](output.txt) · [CSV version of this table](results.csv)
