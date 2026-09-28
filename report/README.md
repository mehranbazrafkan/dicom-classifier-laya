# DICOM → BIDS classification with the Laya decision model — project report

This folder contains the documentation for `dicom-classifier-laya`: **how the code works** and
**what the run actually produced**.

Everything here is derived from a single executed run; the raw log is included unchanged so
every number below can be traced back to it.

---

## TL;DR

| | |
|---|---|
| **Pipeline** | `main.py` (1,493 lines) reads DICOM **headers only**, groups them into Study → Series, builds a contextual state per series and asks the **Laya** decision model 9 BIDS questions. |
| **Input** | `./data/dicoms` → **394 DICOM files**, **3 studies**, **36 series** (33 MR + 3 SR) on a Siemens MAGNETOM Prisma 3 T. |
| **Output** | **36 × 9 = 324 answers**, each with a full probability table → [`output.txt`](output.txt) (5,328 lines). |
| **What works** | BIDS **data type**: **19 / 21 correct (90 %)** — `fmap` 6/6, `func` 10/10, `anat` 2/2, `dwi` 1/3. |
| **What fails** | BIDS **suffix**: **2 / 15 correct (13 %)** — 33 of 36 answers collapse to `phase1`/`phase2`; `run`/`echo`/`flip`/`inversion`/`direction`/`mt` are near-constant because the state contains no evidence for them. |

---

## Report map

| # | File | What it answers |
|---|---|---|
| 1 | [`how-the-code-works.md`](how-the-code-works.md) | How does `main.py` work, stage by stage? What is sent to the model? What are the design limitations? |
| 2 | [`results.md`](results.md) | How good are the results? Accuracy, per-study/per-datatype breakdown, calibration, evidence gaps, recommendations. |
| 3 | [`per-series-predictions.md`](per-series-predictions.md) | All 36 series with every predicted entity and its probability, marked ✔/✘. |
| 4 | [`results.csv`](results.csv) | The same rows, machine-readable (36 rows × 30 columns). |
| 5 | [`output.txt`](output.txt) | The raw, unmodified run log — the single source of truth for everything above. |

Start with [how-the-code-works.md](how-the-code-works.md) if you have not read the code, or with
[results.md](results.md) if you only care about the numbers.

---

## Headline numbers

```
Datatype  ████████████████████████████████████░░░░  19 / 21   (90.5 %)
Suffix    █████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   2 / 15   (13.3 %)
```

- The model identifies the **coarse data type** reliably (all `fmap`, `func` and `anat` series
  correct; 2 of 3 DWI series mislabelled `func`).
- The model identifies **explicit structural suffixes** confidently (`T1w` p = 0.98,
  `T2w` p = 0.97) but labels every BOLD, SBRef and DWI series as `phase2`.
- Confidence is **flat and uninformative**: correct and incorrect `datatype` answers average
  p = 0.275 vs 0.256 — probability cannot be used to reject a bad prediction.
- 4 of the 9 questions (`direction`, `echo`, `flip`, `inversion`) are asked even though their
  evidence is missing: `in_plane_phase_encoding_direction`, `image_orientation_patient` and
  `inversion_time` are empty in **all 36** series, and `echo_time`/`flip_angle` exist in only 3
  (the physiology logs).

Full analysis, including the calibration table and recommended fixes:
[results.md](results.md).

---

## How to read this report

- Every table in `results.md` and `per-series-predictions.md` was produced by parsing
  `output.txt`; nothing was re-run or hand-transcribed.
- **Expected labels** used for scoring come from the vendor `SeriesDescription`/`ProtocolName`,
  which in this dataset already contain BIDS-style names. This is a sanity-check proxy for
  ground truth, **not** an independent annotation — see
  [the scoring caveat](results.md#1-what-was-run).
- 15 of the 36 series (9 localizers, 3 DICOM SR reports, 3 physiology logs) have **no BIDS
  equivalent** and are excluded from the accuracy figures; the pipeline still classifies them,
  which is itself a finding.

---

## Reproducing the run

```bash
# 1. install dependencies (pydicom + the "laya" package; versions are not pinned in the repo)
pip install pydicom laya

# 2. put DICOM files under ./data/dicoms  (this folder is git-ignored)

# 3. run and capture the log
python main.py > output.txt

# 4. regenerate this report's tables from the log
#    (the parser used is described in how-the-code-works.md §4)
```

The model `convaiinnovations/laya` is downloaded from the Hugging Face Hub on first run.

---

## Data-handling note

The `data/` folder contains medical imaging data (DICOM files and an inventory) and is listed in
`.gitignore`, so it is **never staged, committed or pushed** to the remote
(`github.com/mehranbazrafkan/dicom-classifier-laya`).

Verify at any time:

```bash
git check-ignore -v data/        # -> .gitignore:225:data/  data/dicoms/...
git status --short               # -> data/ must NOT appear
```

The report itself only contains aggregate statistics, UIDs and series descriptions that were
already printed in the log — no pixel data and no patient identifiers are reproduced here
(the source study is already anonymised: `Studyname Studyname`, single date `20250526`).

---

[how-the-code-works.md](how-the-code-works.md) · [results.md](results.md) ·
[per-series-predictions.md](per-series-predictions.md) · [output.txt](output.txt)
