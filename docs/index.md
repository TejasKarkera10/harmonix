# HARMONIX

_A harmonization pipeline framework for polysomnography data_

---

**HARMONIX** is an open-source framework for harmonizing polysomnographic (PSG) data for public distribution via the [National Sleep Research Resource (NSRR)](https://sleepdata.org). It is built on top of [Luna](https://zzz-luna.org/luna/) and designed to compress a week-long harmonization process into a single day.

HARMONIX is developed at Brigham and Women's Hospital as part of the NAPS Consortium harmonization effort.

---

## What HARMONIX does

Harmonizing a PSG dataset for public release involves many steps: checking EDF files, removing PHI, mapping channel names, assessing signal quality, reviewing staging, documenting issues, and generating a distribution-ready dataset with full documentation. Done manually, this takes 5–7 days per dataset.

HARMONIX automates and accelerates every step of this process — with built-in fallback logic that flags unusual cases for human review rather than silently passing them.

## Core design principles

**Automation with human-in-the-loop fallback.**
Every automated check produces one of three outcomes: pass, soft flag (unusual — review later), or hard flag (pipeline pauses — review now). Nothing unusual is silently ignored.

**Documentation is generated, not written.**
The README follows the [APPLES/NSRR standard format](https://sleepdata.org). Every tool writes its outputs directly into the README as it runs. By the time processing finishes, the documentation is already done.

**Built on Luna.**
HARMONIX is a framework around [Luna](https://zzz-luna.org/luna/), not a replacement for it. All signal processing uses Luna commands directly.

---

## Pipeline overview

| Stage | Tool | Time |
|-------|------|------|
| 00 | Project Scaffolder | 5 min |
| 01 | PHI + File Naming Validator | 15 min |
| 02 | AI-assisted cmap Generator | 30 min |
| 03 | SLURM Parallel QC Pipeline | 2–3 hrs |
| 04 | Signal Coverage Dashboard | 1–2 hrs review |
| 05 | Manual Review Queue (LunaScope) | 2–3 hrs |
| 06 | Auto Issues File Generator | 1 hr review |
| 07 | README Report Finalizer | Auto |

See the [Architecture](architecture.md) page for the full pipeline diagram and fallback logic.

---

## Getting started

```bash
git clone https://github.com/your-github-username/harmonix
cd harmonix
pip install -e .
```

Then follow the [Getting Started](getting-started.md) guide, or jump straight to the [Your First Dataset](tutorials/first-dataset.md) tutorial.

---

## Things HARMONIX aims to do

- Scaffold standardized project directories for any new dataset
- Validate EDF headers for PHI and file naming compliance
- Generate Luna `cmap.txt` channel mappings with AI-assisted suggestions
- Run parallelized signal QC across all subjects on SLURM clusters
- Produce a signal coverage dashboard stratified by domain and study type
- Auto-generate a structured issues file from QC outputs
- Compile a fully-populated README report in NSRR standard format

## Things HARMONIX doesn't aim to do

- Replace Luna — all signal processing is delegated to Luna
- Perform clinical scoring or event detection
- Replace manual expert review — the goal is to minimize it, not eliminate it
- Support non-EDF data formats

---

!!! note "Status"
    HARMONIX is under active development. Tools are being built and documented incrementally. See the [Tools](tools/index.md) section for current status of each component.
