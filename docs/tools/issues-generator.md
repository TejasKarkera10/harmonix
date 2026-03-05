# Issues File Generator

**Stage:** 06 | **Mode:** Auto + Human review | **Time:** ~1 hr review

---

## What it does

Compiles all flagged items from the review queue into a structured issues file — categorized by type, severity, and subject. Every QC failure is auto-written as a structured entry. You add narrative context only where needed.

---

## Usage

```bash
harmonix issues --res <results_dir> [options]
```

**Example:**
```bash
harmonix issues --res res/ --out res/issues.md
```

---

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--res` | Yes | Path to results directory |
| `--out` | No | Output issues file (default: `res/issues.md`) |
| `--readme` | No | README to update (default: `README.md`) |

---

## Issue categories

| Category | Tag | Examples |
|----------|-----|---------|
| Signal quality | `[SQ]` | Flatline, clipping, amplitude outlier |
| PHI / headers | `[PHI]` | Name in header, real date |
| File naming | `[FILE]` | Non-standard naming, duplicate ID |
| Annotation | `[ANNOT]` | Stage gaps, duration mismatch |
| Unit errors | `[UNIT]` | mV vs uV mislabel |
| Channel absence | `[CH]` | Expected channel missing from site |

---

## Output format

```markdown
## Issues — APPLES dataset
_Generated 2026-03-05 by harmonix v0.1_

### Hard flags (require resolution before distribution)

**[PHI] id_140003** — Real subject name found in EDF Patient Name field.
Resolved: stripped with `ANON`, new EDF written.

**[ANNOT] id_220011** — Staging duration 6h12m vs EDF duration 8h45m.
Status: under review.

### Soft flags (documented, not blocking)

**[SQ] id_350094** — Recording duration 11.2h (dataset median 7.8h).
Note: confirmed valid long recording from site SU.

**[SQ] id_180022** — SOAP kappa 0.38 for C3-M2, typical for C4-M1.
Note: C3 electrode likely suboptimal; C4 retained as primary EEG.
```
