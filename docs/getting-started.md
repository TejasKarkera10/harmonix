# Getting Started

## Prerequisites

Before using HARMONIX, you need:

- **Luna** v1.2+ installed and accessible via command line. See [Luna installation](https://zzz-luna.org/luna/download/).
- **Python** 3.9+
- **R** 4.0+ (for coverage dashboard and report generation)
- Access to an **SLURM cluster** (ERISTwo or equivalent) for the QC pipeline
- A **Luna sample list** for the dataset you want to harmonize

---

## Installation

Clone the repo and install:

```bash
git clone https://github.com/TejasKarkera10/harmonix
cd harmonix
pip install -e .
```

Install MkDocs if you want to build the docs locally:

```bash
pip install mkdocs-material
```

---

## Your first run

### 1. Scaffold a new project

```bash
harmonix scaffold --dataset apples --path /data/nsrr/working/apples
```

This creates the standard folder structure:

```
apples/
├── files/       # original non-data files (PDFs, XLS, etc.)
├── sl/          # sample lists
├── tmp/         # raw Luna outputs (.db files)
├── res/         # compiled higher-level outputs
├── cmd/         # Luna scripts
├── nap/         # NAP output and harmonized EDFs
├── dist/        # final distribution folder
└── viz/         # visual summaries (HTML)
```

And initializes a `README.md` pre-filled with the NSRR standard sections (0–13).

### 2. Run PHI validation

```bash
harmonix phi --sl sl/s0.lst --out res/phi_report.txt
```

### 3. Generate cmap

```bash
harmonix cmap --sl sl/s0.lst --ref reference/aliases.txt --out cmd/cmap.txt
```

### 4. Run QC pipeline

```bash
harmonix qc --sl sl/s0.lst --cmd cmd/ --out tmp/ --jobs 20
```

---

## Key concepts

### Sample lists

HARMONIX uses Luna sample lists (`.lst` files) as its primary input format. Build one with:

```bash
luna --build /path/to/edfs/ > sl/s0.lst
```

### The review queue

Every automated check writes flagged items to `res/review_queue.txt`:

```
[HARD] id_140003 — staging duration 6h12m vs EDF 8h45m
[SOFT] id_350094 — recording duration 11.2h, dataset median 7.8h
```

Hard flags pause processing for that subject. Soft flags continue but are queued for later review.

### README as living document

The README is not written at the end — it is populated throughout the pipeline. Every tool appends its outputs directly into the relevant README section. By the time you finish, documentation is already done.

---

## Next steps

- Read the [Architecture](architecture.md) page for the full pipeline design
- Browse the [Tools](tools/index.md) reference
- Follow the [Your First Dataset](tutorials/first-dataset.md) tutorial end-to-end
