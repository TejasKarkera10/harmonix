# Pipeline Architecture

HARMONIX compresses a 5–7 day PSG harmonization process into a single day by automating discovery and front-loading all QC checks so that human time is spent only on resolving problems, not finding them.

---

## Design philosophy

The key insight is that most of the manual time in harmonization is spent **discovering** problems — opening files, scrolling through LunaScope, noticing things look wrong. HARMONIX automates discovery entirely. You spend human time only on the subset of cases that are genuinely unusual.

Three principles drive the design:

1. **Automation with fallback** — every check produces pass / soft flag / hard flag
2. **README as living document** — outputs are written into the README as the pipeline runs
3. **Luna-native** — all signal processing delegates to Luna commands directly

---

## Fallback tiers

Every automated check in HARMONIX produces one of three outcomes:

| Tier | Meaning | Action |
|------|---------|--------|
| ✅ **Pass** | Within expected range | Write to README, continue |
| 🟡 **Soft flag** | Unusual but not blocking | Add to review queue, continue |
| 🔴 **Hard flag** | Cannot proceed without human decision | Pause subject, add to review queue |

The review queue (`res/review_queue.txt`) is your prioritized checklist at the end of the automated run. Hard flags first, soft flags second.

---

## Stage-by-stage breakdown

### Stage 00 — Project Scaffolder
**Time: ~5 min | Mode: Auto**

Creates the standard NSRR folder structure and initializes a README pre-filled with sections 0–13 (matching the APPLES/NSRR standard).

```bash
harmonix scaffold --dataset mydata --path /data/nsrr/working/mydata
```

---

### Stage 01 — PHI + File Naming Validator
**Time: ~15 min | Mode: Auto**

Scans all EDF headers for PHI (names, dates, MRNs). Validates file naming conventions. Checks for duplicates and unexpected EDF types.

**Luna commands used:** `luna --build`, `luna --validate`, `HEADERS`, `DESC`, `ANON`

**Soft flags:** unexpected date format, non-standard filename  
**Hard flags:** real name in header, duplicate subject IDs

---

### Stage 02 — AI-assisted cmap Generator
**Time: ~30 min | Mode: AI + Human review**

Extracts channel inventory from all EDFs. Compares against a reference alias library built from NAPS, CHAT, nuMoM2b, and LOFT datasets. An LLM suggests canonical mappings with confidence scores. You review only the uncertain ones.

**Luna commands used:** `HEADERS signals`, `CANONICAL`, `ALIASES`

**Output:** ready-to-use `cmap.txt`, README §7 populated

**Soft flags:** low-confidence mappings queued for review

---

### Stage 03 — SLURM Parallel QC Pipeline
**Time: 2–3 hrs (parallel) | Mode: SLURM**

The most compute-intensive stage. Runs full signal quality checks across all subjects and channels in parallel on ERISTwo. Produces per-subject, per-epoch QC metrics for every domain.

**Luna commands used:** `SIGSTATS`, `STATS`, `SOAP`, `HYPNO`, `HRV`, `FILTER`, `PEAKS`, `POL`

**Soft flags:** amplitude >3×IQR, SOAP kappa <0.4, sleep efficiency <50%  
**Hard flags:** >40% epochs flat, staging/EDF duration mismatch, zero-variance channel

---

### Stage 04 — Signal Coverage Dashboard
**Time: 1–2 hrs review | Mode: Auto + Human review**

Extends the channel inventory tool. For each domain (EEG, ECG, respiratory, SpO2, EMG) shows % subjects with signal present and % passing QC, broken down by study type (diagnostic vs CPAP vs split-night). Auto-generates inclusion/exclusion rationale at configurable thresholds (default: present in >80% of subjects).

**Soft flags:** site-level outliers in amplitude distributions

---

### Stage 05 — Targeted LunaScope Inspection
**Time: 2–3 hrs | Mode: Manual**

Only flagged items from the review queue are opened in LunaScope. Instead of inspecting all subjects, you inspect only those with hard or soft flags. Hard flags reviewed first.

---

### Stage 06 — Auto Issues File Generator
**Time: 1 hr review | Mode: Auto + Human review**

Every QC check that fails writes a structured entry to the issues file automatically. Categories: signal quality, PHI/headers, file naming, annotation issues, unit errors, channel absence. You add narrative context only where needed.

---

### Stage 07 — README Report Finalizer
**Time: Auto | Mode: Auto**

Compiles the living README (populated throughout the pipeline) into a clean HTML report. Mirrors the NSRR APPLES README structure exactly.

```bash
harmonix report --readme README.md --out dist/report.html
```

---

## Full pipeline flow

```
New Dataset Arrives
        │
        ▼
[00] Project Scaffolder          ← 5 min
        │
        ▼
[01] PHI + File Validator         ← 15 min
        │
   ┌────┴────┐
 HARD       SOFT
 pause     queue
        │
        ▼
[02] AI cmap Generator            ← 30 min
        │
        ▼
[03] SLURM QC Pipeline            ← 2–3 hrs parallel
        │
   ┌────┴────┐
 HARD       SOFT
 pause     queue
        │
        ▼
[04] Signal Coverage Dashboard    ← auto + 1–2 hrs review
        │
        ▼
[05] Manual Review Queue          ← 2–3 hrs (flagged only)
        │
        ▼
[06] Issues File Generator        ← auto + 1 hr review
        │
        ▼
[07] README Report Finalizer      ← auto
        │
        ▼
Harmonized Dataset + README Report
```

**Total: ~1 working day**
