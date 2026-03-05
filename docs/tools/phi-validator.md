# PHI + File Naming Validator

**Stage:** 01 | **Mode:** Auto | **Time:** ~15 min

---

## What it does

Scans all EDF headers across the dataset for protected health information (PHI) and validates file naming conventions. Outputs a structured report and populates README §3 (Identifiers).

---

## Usage

```bash
harmonix phi --sl <sample_list> [options]
```

**Example:**
```bash
harmonix phi --sl sl/s0.lst --out res/phi_report.txt
```

---

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--sl` | Yes | Path to Luna sample list |
| `--out` | No | Output report path (default: `res/phi_report.txt`) |
| `--readme` | No | README path to auto-populate §3 (default: `README.md`) |

---

## Checks performed

### PHI checks (EDF header fields)

| Field | Check |
|-------|-------|
| Patient ID | Must be numeric or anonymized format |
| Patient name | Must be empty or anonymized |
| Start date | Must be anonymized (01.01.85 standard) |
| Birthdate | Must be empty or anonymized |
| Recording field | Must not contain technician name or site name |

### File naming checks

| Check | Description |
|-------|-------------|
| Consistent prefix | All files should follow the same naming pattern |
| No PHI in filename | Filenames must not contain dates, names, or MRNs |
| Unique IDs | No duplicate subject IDs across the sample list |
| EDF type consistency | All files expected to be same type (EDF vs EDF+) |

---

## Fallback logic

| Outcome | Trigger | Action |
|---------|---------|--------|
| ✅ Pass | All checks clear | Write summary to README §3, continue |
| 🟡 Soft flag | Unexpected date format, non-standard filename | Add to `review_queue.txt`, continue |
| 🔴 Hard flag | Real name in header, duplicate IDs | Add to `review_queue.txt`, pause subject |

---

## Output

**`res/phi_report.txt`** — per-subject pass/fail for each check

**`res/review_queue.txt`** — flagged items appended with category `[PHI]`

**`README.md §3`** — populated with summary counts and any issues found

---

## Luna commands used

```bash
luna sl/s0.lst -s 'HEADERS'
luna sl/s0.lst -s 'DESC'
```
