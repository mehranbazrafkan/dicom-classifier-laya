# Results of the run

- **Source log:** [`output.txt`](output.txt) (5,328 lines, 390 KB — verbatim copy of the run)
- **Machine-readable rows:** [`results.csv`](results.csv)
- **Full per-series table:** [`per-series-predictions.md`](per-series-predictions.md)

---

## 1. What was run

`python main.py` was executed against `./data/dicoms` and the stdout was captured as
`output.txt`. The run:

- discovered **394 DICOM files** in **3 studies / 36 series**;
- made **36 `agent.predict()` calls** (one per series), each answering **9 questions**
  → **324 answers**, each with a full probability distribution.

Scoring method used below: the *expected* BIDS label for each series is taken from the vendor
`SeriesDescription` / `ProtocolName`, which in this dataset already contains BIDS-style names
(`ses-pre_T1w`, `task-uebung_bold`, `acq-15_dir-ap_dwi`, …). This is a **sanity-check proxy for
ground truth, not an independent annotation** — the model can also read those strings, so the
numbers should be read as "does the pipeline agree with its own naming", not as a benchmark
score. 15 of the 36 series have no BIDS equivalent and are excluded from the accuracy figures.

---

## 2. Dataset overview

| Study | Series | DICOM files | Content |
|---|---|---|---|
| 1 (`…00005`) | 9 | 45 | localizer, Phoenix SR report, `ses-pre` run-01/02 field maps, sparse/rest BOLD, T1w |
| 2 (`…00007`) | 10 | 62 | 4 scout/localizer images, Phoenix SR report, `ses-post` field maps, `task-mb` BOLD + SBRef + physio log |
| 3 (`…00009`) | 17 | 287 | 4 scouts, Phoenix SR report, T2w, `task-dmaging` ×2 + `task-uebung` (BOLD + SBRef + physio log each), 3 DWI series (117 / 1 / 1 instances) |
| **Total** | **36** | **394** | |

- **Modalities:** 33 × `MR`, 3 × `SR` (the `PhoenixZIPReport` series).
- **Scanner:** Siemens Healthineers **MAGNETOM Prisma**, 3 T, `syngo MR XA30` (33 series).
- **Anonymised:** `study_description` is the literal string `Studyname Studyname` for all 36
  series and `study_date` is `20250526` for all of them — so study-level context carries almost
  no discriminating information.
- Study 3 alone holds **287 of the 394 files (73 %)**; the single 117-instance
  `acq-15_dir-ap_dwi` series is the largest series in the dataset.

---

## 3. Evidence gaps in the state

Before looking at the answers it helps to know what evidence the model actually received.
Fill rate of each field in the `target_series` state, out of 36 series:

| Field | Series with a usable value | Comment |
|---|---|---|
| `series_description`, `protocol_name`, `modality`, `image_type`, `instance_numbers` | **36 / 36** | the informative core |
| `manufacturer` | 36 / 36 | constant (`Siemens Healthineers`) |
| `study_date`, `study_time`, `study_description` | 36 / 36 | constant across all series |
| `mr_acquisition_type` | 30 / 36 | 20 × 2D, 10 × 3D |
| `magnetic_field_strength`, `rows`, `columns` | 30 / 36 | `3` T, matrix 64–512 |
| `manufacturer_model_name`, `software_versions` | 33 / 36 | constant |
| `spacing_between_slices` | 20 / 36 | 1.5 – 8.4 mm |
| `echo_time`, `repetition_time`, `flip_angle` | **3 / 36** | and only on the physiology-log series (`0.05` / `0.5` / `62`) |
| `slice_thickness` | 0 / 36 | only the literal value `0` |
| `acquisition_times` | 3 / 36 | |
| `inversion_time` | **0 / 36** | yet the `inversion` question is asked 36 times |
| `image_orientation_patient` | **0 / 36** | |
| `in_plane_phase_encoding_direction` | **0 / 36** | yet the `direction` question is asked 36 times |
| `echo_number` | 0 / 36 | only `0` |
| `scanning_sequence`, `sequence_variant`, `sequence_name`, `scan_options`, `number_of_averages` | **0 / 36** | all empty |

**Conclusion:** for `direction`, `echo`, `flip` and `inversion` — and effectively `mt` — the
state contains *no supporting evidence at all*. Whatever the model answers for those five
questions is a prior, not an inference from this dataset.

---

## 4. Headline results

| Question | Scored | Correct | Accuracy | Notes |
|---|---|---|---|---|
| **datatype** | 21 | **19** | **90.5 %** | only series whose name implies a BIDS data type |
| **suffix** | 15 | **2** | **13.3 %** | only `T1w` and `T2w` correct |
| run (series whose name contains `run-01`/`run-02`) | 12 | 3 | 25 % | random would be 11 % |

### Per study

| Study | datatype correct |
|---|---|
| 1 | 7 / 7 |
| 2 | 4 / 4 |
| 3 | 8 / 10 (both misses are DWI series) |

### Per expected data type

| Expected datatype | Series | Correct | Accuracy |
|---|---|---|---|
| fmap | 6 | 6 | 100 % |
| func (bold + sbref) | 10 | 10 | 100 % |
| anat (T1w + T2w) | 2 | 2 | 100 % |
| dwi | 3 | **1** | 33 % |

The two failures are `acq-15_dir-ap_dwi` → `func` (p = 0.26) and `acq-15_dir-pa_dwi` →
`func` (p = 0.25), even though both carry `ImageType: ['ORIGINAL','PRIMARY','DIFFUSION','NONE']`
and `…_dwi` in the description. The third DWI series (`acq-15b0_dir-ap_dwi`) was labelled `dwi`
with p = 0.21 — i.e. the three near-identical series received three different confidence levels
around a 0.21–0.26 band.

---

## 5. What works

1. **Coarse data type is right most of the time (19/21).** `fmap`, `func` and `anat` were all
   identified perfectly; only diffusion was unreliable.
2. **Explicit structural suffixes are recognised confidently:** `ses-pre_T1w` → `T1w` (p = 0.98)
   and `acq-space_T2w` → `T2w` (p = 0.97). These are the only two answers in the whole run above
   0.9, and they are the two that the description states verbatim.
3. **Context assembly works mechanically:** every series received its siblings (8, 9 and 16
   related series for studies 1–3) and no file paths leaked into the prompt (`files` is stripped).
4. **Robustness:** 394/394 files parsed, zero `[WARNING] Could not read DICOM` messages in the
   log, and non-BIDS content (SR reports, localizers, physiology logs) did not break the run.

---

## 6. What does not work

### 6.1 The `suffix` answers collapse to a field-map prior

Answer distribution over all 36 series (34 possible suffixes):

| Answer | Count | Share |
|---|---|---|
| `phase2` | 22 | 61 % |
| `phase1` | 11 | 31 % |
| `T1w` | 1 | 3 % |
| `T2w` | 1 | 3 % |
| `bold` | 1 | 3 % |

**33 of 36 suffix predictions are `phase1`/`phase2`.** Every BOLD run, every `SBRef` and all
three DWI series — **13 of the 15 scorable series**, whose suffix should be `bold`, `sbref` or
`dwi` — were labelled `phase2`. This is the single biggest error in the run: the model does not
appear to be reading the BIDS names at all for the suffix question; it falls back to a
field-map-flavoured default.

### 6.2 The model only ever uses 5 of 34 suffix options

The remaining 29 options (including `dwi`, `sbref`, `epi`, `phasediff`, `magnitude1/2`,
`FLAIR`, `T1map`, …) never appear as an answer.

### 6.3 Several questions are effectively constant

| Question | Answers chosen | Observation |
|---|---|---|
| `mt` | `on` × 36 | constant; no MT evidence exists in the state |
| `part` | `phase` × 35, `real` × 1 | `_part-` is meaningless for `T1w`/`bold`/`dwi`, yet it is always emitted |
| `direction` | `i` × 31, `k` × 5 | phase-encoding direction is empty in every state |
| `echo` | `1` × 29 | `echo_number` is empty in every state |
| `flip` | `1` × 31 | `flip_angle` empty in 33/36 series |
| `datatype` | `func` × 16, `anat` × 13, `fmap` × 6, `dwi` × 1 | `perf`, `pet`, `mrs` never chosen |

### 6.4 Non-BIDS series are classified anyway

15 of 36 series have no BIDS equivalent, but they all received full answers:

- 9 localizers/scouts → `datatype: anat` (8×) / `func` (1×), `suffix: phase1/phase2`
- 3 `PhoenixZIPReport` structured reports (`Modality: SR`) → `datatype: anat`, `suffix: phase1`
- 3 `*_PhysioLog` series → `datatype: func`

Anatomical/functional labels for an `SR` report or a localizer are wrong by construction; a
correct pipeline should be able to answer "exclude this series".

---

## 7. Confidence and calibration

Mean top-1 probability assigned by the model, compared with the uniform baseline for that
question:

| Question | Options | Mean top-1 p | Uniform | Ratio | Range |
|---|---|---|---|---|---|
| datatype | 7 | 0.267 | 0.143 | 1.9 × | 0.21 – 0.35 |
| suffix | 34 | 0.502 | 0.029 | 17.1 × | 0.25 – 0.98 |
| part | 4 | 0.372 | 0.250 | 1.5 × | 0.31 – 0.46 |
| direction | 6 | 0.359 | 0.167 | 2.2 × | 0.27 – 0.53 |
| run | 9 | 0.309 | 0.111 | 2.8 × | 0.15 – 0.50 |
| echo | 9 | 0.328 | 0.111 | 3.0 × | 0.16 – 0.54 |
| flip | 5 | 0.281 | 0.200 | 1.4 × | 0.22 – 0.43 |
| inversion | 5 | 0.261 | 0.200 | 1.3 × | 0.22 – 0.50 |
| mt | 2 | 0.643 | 0.500 | 1.3 × | 0.53 – 0.79 |

Readings:

- **`datatype` is barely above chance.** The top-1 probability never exceeds 0.35 and the
  distribution is flat, so the pipeline is picking the "least bad" option rather than asserting
  a class.
- **Confidence does not separate right from wrong:** correct `datatype` answers averaged
  p = 0.275, incorrect ones p = 0.256 — the two are indistinguishable, so the probabilities
  cannot be used as a rejection threshold.
- **`suffix` is confidently wrong.** 0.50 mean top-1 probability over 34 classes is 17× the
  uniform baseline, yet 13 of the 15 scorable suffix answers contradict the series name
  (and 33 of 36 overall collapse to `phase1`/`phase2`).

---

## 8. Interpretation

1. The pipeline **architecture** works: discovery → hierarchy → contextual state → model →
   structured answers, all in one pass, with no failures on 394 files.
2. The **datatype-level** classification is usable as a first pass (19/21) but is not
   self-aware — it cannot tell when it is unsure.
3. The **entity-level** classification (suffix, part, run, echo, flip, inversion, direction, mt)
   is not usable as-is: it is dominated by priors because
   (a) the evidence needed for those entities is missing from the extracted state, and
   (b) there is no way to say "this entity does not apply" or "this series is not BIDS".
4. `T1w`/`T2w` succeeding shows the model *can* use the description when the token is
   unambiguous — so the failure mode is likely prompt/option design rather than an incapable
   model.

---

## 9. Recommended next steps

1. **Add an `exclude`/`none` option** to `datatype` and `suffix`, and short-circuit localizers,
   `Modality: SR` and `*_PhysioLog` before calling the model.
2. **Ask only applicable questions** — `part` only for field-map/complex images, `flip`/`inversion`
   only when `FlipAngle`/`InversionTime` exist, `mt` only when the protocol suggests MT prep.
3. **Fill the evidence gaps:** read Siemens CSA/private tags (or `ImageOrientationPatient`,
   `InPlanePhaseEncodingDirection`, `EchoTime`, `RepetitionTime`, `FlipAngle`, `InversionTime`)
   so that `direction`, `echo`, `flip` and `inversion` become answerable.
4. **Persist results:** `json.dump(all_results, ...)` / CSV instead of relying on stdout.
5. **Constrain or hint the suffix list** (e.g. only offer field-map suffixes when
   `datatype == fmap`), or provide a few-shot example with a BIDS-named series.
6. **Evaluate properly** on a dataset with real BIDS ground truth (e.g. an OpenNeuro session
   converted from the same DICOMs), rather than on names the model can also read.
7. **Add consistency constraints** after prediction: magnitude/phase pairs must come from the
   same field-map acquisition, `run` must be contiguous within a datatype, `SBRef` must share
   `run`/`echo` with its `bold` parent.

---

## 10. Report contents

| File | Contents |
|---|---|
| [`README.md`](README.md) | Main report — index, headline numbers, data-handling note |
| [`how-the-code-works.md`](how-the-code-works.md) | Stage-by-stage explanation of `main.py` |
| [`results.md`](results.md) | This document — analysis of the run |
| [`per-series-predictions.md`](per-series-predictions.md) | All 36 series × 9 answers with probabilities |
| [`results.csv`](results.csv) | The same rows as comma-separated values |
| [`output.txt`](output.txt) | Raw, unmodified run log (5,328 lines) |

[Back to the main report](README.md)
