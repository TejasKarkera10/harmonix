# Project Scaffolder

**Stage:** 00 | **Mode:** Auto | **Time:** ~5 min

---

## What it does

Creates the standard NSRR folder structure for a new dataset and initializes a `README.md` pre-filled with sections 0–13, matching the APPLES/NSRR harmonization standard.

---

## Usage

```bash
harmonix scaffold --dataset <name> --path <working_dir>
```

**Example:**
```bash
harmonix scaffold --dataset apples --path /data/nsrr/working/apples
```

---

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--dataset` | Yes | Dataset name (used in README title and file prefixes) |
| `--path` | Yes | Working directory path to scaffold |
| `--readme-template` | No | Path to custom README template (default: NSRR standard) |

---

## Output

Creates the following folder structure:

```
<path>/
├── files/       # original non-data files (PDFs, XLS, metadata)
├── sl/          # Luna sample lists
├── tmp/         # raw Luna outputs (.db files)
├── res/         # compiled higher-level outputs
├── cmd/         # Luna scripts
├── nap/         # NAP output and harmonized EDFs/annotations
├── dist/        # final distribution folder
└── viz/         # visual summaries (auto-generated HTML)
```

And a `README.md` with all standard sections pre-populated:

```
0) Preliminaries
1) Key design factors
2) EDF checks
3) Identifiers
4) Signal review
5) Annotation review
6) Manual staging
7) NAP signal mappings
8) NAP annotation mappings
9) Encodings
10) Interim report
11) Running NAP
12) Compiling the distribution dataset
13) Depositing an as-is dataset
```

---

## README template

The README is initialized with dataset name, date, working paths, and placeholders for all sections. Subsequent HARMONIX tools populate these sections automatically as they run.

!!! tip
    You should fill in **Section 1 (Key design factors)** manually after scaffolding — this is where you document study design, number of subjects, sites, PSG system used, and any known quirks of the dataset.
