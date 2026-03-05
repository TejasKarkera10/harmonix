# Coverage Dashboard

**Stage:** 04 | **Mode:** Auto + Human review | **Time:** 1–2 hrs review

---

## What it does

Extends the channel inventory with QC pass rates. For each signal domain, shows what percentage of subjects have the signal present and what percentage pass QC — broken down by study type and site. Auto-generates inclusion/exclusion rationale at configurable thresholds.

---

## Usage

```bash
harmonix coverage --res <results_dir> [options]
```

**Example:**
```bash
harmonix coverage --res res/ --threshold 0.8 --out res/coverage_report.html
```

---

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--res` | Yes | Path to results directory (from QC pipeline) |
| `--threshold` | No | Minimum proportion present to include signal (default: 0.8) |
| `--out` | No | Output HTML dashboard (default: `res/coverage_report.html`) |
| `--readme` | No | README path to auto-populate §4 (default: `README.md`) |

---

## Output table structure

| Domain | Channel | Present (%) | QC Pass (%) | Diagnostic | CPAP | Split-night | Decision |
|--------|---------|-------------|-------------|------------|------|-------------|----------|
| EEG | C3 | 98% | 94% | 99% | 97% | 91% | ✅ Include |
| ECG | ECG1 | 100% | 96% | 100% | 100% | 100% | ✅ Include |
| Resp | THOR | 87% | 71% | 92% | 85% | 74% | ✅ Include |
| Resp | ABDO | 84% | 68% | 90% | 82% | 71% | ✅ Include |
| Resp | Flow | 61% | 55% | 65% | 58% | 52% | 🟡 Review |

---

## Soft flags

- Any channel present in <80% of subjects for a specific site (site-level outlier)
- QC pass rate <60% for any included channel
- Large discrepancy in channel availability between study types
