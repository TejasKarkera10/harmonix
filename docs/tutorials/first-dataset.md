# Tutorial: Your First Dataset

In this tutorial we walk through harmonizing the APPLES dataset using HARMONIX end-to-end. APPLES has 1,105 subjects across 5 sites, all using the Alice4 PSG system — a good representative real-world case.

---

## Prerequisites

- HARMONIX installed (`pip install -e .`)
- Luna v1.2+ in your PATH
- ERISTwo cluster access
- APPLES EDFs at `/data/nsrr/working/apples-edfs/`

---

## Step 1 — Scaffold the project

```bash
harmonix scaffold --dataset apples --path /data/nsrr/working/apples
cd /data/nsrr/working/apples
```

Check what was created:

```bash
ls
# files/  sl/  tmp/  res/  cmd/  nap/  dist/  viz/  README.md
```

Open `README.md` and fill in **Section 1 (Key design factors)**:
- 1,105 individuals, one EDF each
- 5 sites: SU, UA, SM, SL, BW
- All studies: Alice4 PSG system
- Each subject has a STAGE.csv file

---

## Step 2 — Build the sample list

```bash
luna --build ../apples-edfs/ > sl/s0.lst
# wrote 1105 EDFs to the sample list
```

---

## Step 3 — PHI validation

```bash
harmonix phi --sl sl/s0.lst
```

Expected output:
```
PHI check: 1105 subjects scanned
PASS: 1103
SOFT [non-standard filename]: 2 subjects → review_queue.txt
README §3 updated.
```

---

## Step 4 — Generate cmap

```bash
harmonix cmap --sl sl/s0.lst --out cmd/cmap.txt
```

The tool will show you any low-confidence mappings and ask you to confirm:

```
? C3-M2 → C3 [confidence: 0.97] ✓ auto-accepted
? C4-M1 → C4 [confidence: 0.96] ✓ auto-accepted
? "EEG Cz-ref" → ?? [confidence: 0.61] — please confirm:
  Options: [1] CZ  [2] skip  [3] custom
```

---

## Step 5 — Run QC pipeline

Submit to SLURM:

```bash
harmonix qc --sl sl/s0.lst --cmap cmd/cmap.txt --jobs 20
```

This submits 20 array jobs. Monitor with:

```bash
squeue -u $USER
```

When complete:

```bash
harmonix qc --merge --out res/qc_summary.txt
```

---

## Step 6 — Review coverage dashboard

```bash
harmonix coverage --res res/ --out res/coverage_report.html
```

Open `res/coverage_report.html` in a browser. Review the inclusion/exclusion table and adjust thresholds if needed.

---

## Step 7 — Work through review queue

```bash
cat res/review_queue.txt
```

Open hard-flagged subjects in LunaScope first. Resolve or document each one. Add resolution notes to `res/issues.md`.

---

## Step 8 — Generate issues file

```bash
harmonix issues --res res/ --out res/issues.md
```

Add narrative context to any entries that need it.

---

## Step 9 — Finalize report

```bash
harmonix report --readme README.md --out dist/apples_harmonization_report.html
```

Your report is ready at `dist/apples_harmonization_report.html`.

---

!!! success "Done"
    You've harmonized APPLES. The `dist/` folder contains harmonized EDFs, the issues file, and the full harmonization report — ready for NSRR deposit.
