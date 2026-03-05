# Tools

HARMONIX is composed of seven tools, each targeting a specific bottleneck in the harmonization process. Each tool can be run independently or as part of the full pipeline.

---

## Status

| Tool | Status | CLI Command |
|------|--------|-------------|
| [Project Scaffolder](scaffolder.md) | 🚧 In development | `harmonix scaffold` |
| [PHI Validator](phi-validator.md) | 🚧 In development | `harmonix phi` |
| [cmap Generator](cmap-generator.md) | 🚧 In development | `harmonix cmap` |
| [QC Pipeline](qc-pipeline.md) | 🚧 In development | `harmonix qc` |
| [Coverage Dashboard](coverage-dashboard.md) | 🚧 In development | `harmonix coverage` |
| [Issues Generator](issues-generator.md) | 🚧 In development | `harmonix issues` |
| [Report Finalizer](report-finalizer.md) | 🚧 In development | `harmonix report` |

---

## Running the full pipeline

```bash
harmonix run --dataset apples --path /data/nsrr/working/apples --jobs 20
```

This runs all stages sequentially, pausing on hard flags for manual resolution before continuing.

---

## Running individual tools

Each tool can be run standalone:

```bash
harmonix scaffold --dataset apples --path /data/nsrr/working/apples
harmonix phi --sl sl/s0.lst
harmonix cmap --sl sl/s0.lst --ref reference/aliases.txt
harmonix qc --sl sl/s0.lst --jobs 20
harmonix coverage --res res/
harmonix issues --res res/
harmonix report --readme README.md
```
