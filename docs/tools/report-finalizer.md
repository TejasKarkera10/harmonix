# Report Finalizer

**Stage:** 07 | **Mode:** Auto | **Time:** ~auto

---

## What it does

Compiles the living README (populated throughout the pipeline) into a clean, shareable HTML report. Mirrors the NSRR APPLES README structure exactly. No writing required — everything was populated as the pipeline ran.

---

## Usage

```bash
harmonix report --readme <readme_path> [options]
```

**Example:**
```bash
harmonix report --readme README.md --out dist/report.html
```

---

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--readme` | Yes | Path to populated README.md |
| `--out` | No | Output HTML path (default: `dist/report.html`) |
| `--css` | No | Custom CSS (default: NSRR github-markdown style) |

---

## What the report contains

The report is a direct render of the README, which by this point contains:

| Section | Populated by |
|---------|-------------|
| §0 Preliminaries | Scaffolder |
| §1 Key design factors | You (manual) |
| §2 EDF checks | PHI Validator |
| §3 Identifiers | PHI Validator |
| §4 Signal review | QC Pipeline + Coverage Dashboard |
| §5 Annotation review | QC Pipeline |
| §6 Manual staging | You (manual, if applicable) |
| §7 NAP signal mappings | cmap Generator |
| §8 NAP annotation mappings | You (manual) |
| §9 Encodings | Auto |
| §10 Interim report | Issues Generator |
| §11 Running NAP | Auto |
| §12 Distribution dataset | Auto |
| §13 As-is dataset | Auto |

---

## Under the hood

Uses `pandoc` to convert README.md to standalone HTML:

```bash
pandoc --standalone -c github-markdown.css \
  -f gfm -t html \
  -o dist/report.html \
  --metadata title="DATASET|NSRR" \
  README.md
```

!!! tip "The README IS the report"
    The core design principle of HARMONIX is that documentation is generated, not written. Every tool writes into the README as it runs. By the time you call `harmonix report`, the only sections requiring manual content are §1 (study design) and §8 (annotation mappings) — everything else is already populated.
