# cmap Generator

**Stage:** 02 | **Mode:** AI-assisted + Human review | **Time:** ~30 min

---

## What it does

Extracts the full channel inventory from all EDFs in the dataset, compares against a reference alias library built from NAPS, CHAT, nuMoM2b, and LOFT datasets, and uses an LLM to suggest canonical Luna channel mappings. You review only the uncertain ones.

Output is a ready-to-use Luna `cmap.txt` file and a populated README §7.

---

## Usage

```bash
harmonix cmap --sl <sample_list> [options]
```

**Example:**
```bash
harmonix cmap --sl sl/s0.lst --ref reference/aliases.txt --out cmd/cmap.txt
```

---

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--sl` | Yes | Path to Luna sample list |
| `--ref` | No | Path to reference alias library (default: built-in NAPS/CHAT/nuMoM2b/LOFT library) |
| `--out` | No | Output cmap path (default: `cmd/cmap.txt`) |
| `--confidence` | No | Confidence threshold below which mappings are flagged for review (default: 0.85) |
| `--readme` | No | README path to auto-populate §7 (default: `README.md`) |

---

## How it works

### Step 1 — Extract channel inventory

Runs `HEADERS signals` across all subjects and compiles a frequency table of channel names:

```
ECG I          1105/1105   (100%)
C3-M2           982/1105   (89%)
THOR RES        801/1105   (73%)
Flow            655/1105   (59%)
...
```

### Step 2 — Match against reference library

Compares each channel name against the built-in alias library. Channels with exact or near-exact matches are auto-mapped with high confidence.

### Step 3 — LLM suggestions for uncertain mappings

Channel names that don't match the reference library are passed to an LLM with context about the dataset (PSG system, site, domain) to suggest canonical mappings. Each suggestion comes with a confidence score and reasoning.

### Step 4 — Human review of low-confidence mappings

Only mappings below the confidence threshold are presented for human confirmation. Everything else is auto-accepted.

---

## Output

**`cmd/cmap.txt`** — Luna-format channel alias file:

```
alias  ECG   ECG1   "ECG I"   "ECGI"   "EKG"
alias  THOR  Thor   "THOR RES"   "THORAX"
alias  C3    C3M2   "C3-M2"   "C3:M2"
```

**`res/channel_inventory.txt`** — full channel frequency table

**`res/review_queue.txt`** — low-confidence mappings flagged with category `[CMAP]`

**`README.md §7`** — populated with mapping table

---

## Luna commands used

```bash
luna sl/s0.lst -o tmp/headers.db -s 'HEADERS signals'
destrat tmp/headers.db +HEADERS -r CH > res/channel_inventory.txt
```

---

## Reference alias library

The built-in library covers channel aliases across:

- NAPS Consortium (Stanford, UCSF, Mayo, Emory, JHU, BWH)
- CHAT (pediatric adenotonsillectomy trial)
- nuMoM2b (nulliparous pregnancy outcomes)
- LOFT

Domains covered: EEG, EOG, EMG, ECG, respiratory (RIP, flow, thermistor), oximetry, audio, PAP/CPAP, position.

!!! note
    You can extend the reference library by adding entries to `reference/aliases.txt` in your local HARMONIX installation.
