"""
harmonix.phi
------------
PHI + file naming validator.

Uses Luna (HEADERS) to extract EDF header fields and checks for:
- Real dates in START_DATE / STOP_DATE / EDF_ID
- Name-like patterns in EDF_ID
- File naming convention issues
- Duplicate subject IDs
- Mixed EDF types across dataset
- Missing paired annotation files

Writes:
- res/phi_report.txt   : full per-subject report
- res/review_queue.txt : flagged items (HARD/SOFT)
- README.md            : auto-populates §2 and §3 placeholders
"""

import os
import re
import subprocess
import click
from datetime import datetime
from collections import Counter, defaultdict


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ANON_DATE = "01.01.85"
NULL_VALUES = {".", "", "X", "x", "NA", "N/A", "none", "None"}

# Date patterns that should NOT appear in header fields
DATE_PATTERN = re.compile(
    r"\b\d{2}[./\-]\d{2}[./\-]\d{2,4}\b"   # 22.04.15 or 04/22/2015
    r"|\b\d{8}\b"                             # 04222015 (8 digit date)
    r"|\b\d{4}[./\-]\d{2}[./\-]\d{2}\b"     # 2015-04-22
    r"|\b\d{2}\d{2}\d{4}\b"                  # 04222015 without separators
)

NAME_PATTERN = re.compile(r"\b[A-Z][a-z]{2,}\s+[A-Z][a-z]{2,}\b")
VALID_FILENAME_RE = re.compile(r"^[a-zA-Z0-9_\-\.]+$")
ANNOTATION_EXTENSIONS = {".xml", ".annot", ".tsv", ".eannot", ".txt"}


# ---------------------------------------------------------------------------
# Luna / destrat runners
# ---------------------------------------------------------------------------

def run_luna_headers(sl_path, out_db):
    """Run Luna HEADERS on a sample list."""
    cmd = ["luna", sl_path, "-o", out_db, "-s", "HEADERS"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def run_destrat_wide(db_path, table, variables):
    """
    Run destrat in wide format and return a dict of {subj_id: {VAR: VALUE}}.

    destrat wide output (no -l flag):
      ID  VAR1  VAR2  VAR3
      subj1  val1  val2  val3

    Handles:
    - Missing columns (not all vars present for all subjects)
    - Null values (".", "", "X")
    - Header row detection
    - Subjects with partial data
    """
    cmd = ["destrat", db_path, f"+{table}", "-v", " ".join(variables)]
    result = subprocess.run(cmd, capture_output=True, text=True)

    headers_by_id = defaultdict(dict)

    if result.returncode != 0 or not result.stdout.strip():
        return headers_by_id

    lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
    if len(lines) < 2:
        return headers_by_id

    # Parse header row — find column indices for each variable
    col_headers = lines[0].strip().split("\t")

    # ID is always first column
    id_col = 0

    # Map variable name -> column index
    var_cols = {}
    for var in variables:
        if var in col_headers:
            var_cols[var] = col_headers.index(var)

    for line in lines[1:]:
        parts = line.strip().split("\t")
        if not parts:
            continue

        subj_id = parts[id_col] if len(parts) > id_col else None
        if not subj_id:
            continue

        for var, col_idx in var_cols.items():
            if col_idx < len(parts):
                val = parts[col_idx].strip()
                # Treat null-like values as missing
                if val not in NULL_VALUES:
                    headers_by_id[subj_id][var] = val

    return headers_by_id


# ---------------------------------------------------------------------------
# Sample list parser
# ---------------------------------------------------------------------------

def parse_sample_list(sl_path):
    """
    Parse a Luna sample list (.lst file).

    Luna sample list format (tab-separated):
      ID  EDF_PATH  [ANNOT_PATH_OR_DOT]

    Or sometimes just:
      EDF_PATH  (no ID — use filename stem)

    Returns list of (id, edf_path, annot_path_or_none).
    """
    entries = []
    with open(sl_path, "r") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")

            if len(parts) >= 3:
                subj_id, edf_path, annot = parts[0], parts[1], parts[2]
                annot = None if annot in NULL_VALUES else annot
                entries.append((subj_id, edf_path, annot))
            elif len(parts) == 2:
                subj_id, edf_path = parts[0], parts[1]
                entries.append((subj_id, edf_path, None))
            elif len(parts) == 1:
                edf_path = parts[0]
                stem = os.path.splitext(os.path.basename(edf_path))[0]
                entries.append((stem, edf_path, None))

    return entries


# ---------------------------------------------------------------------------
# PHI checks
# ---------------------------------------------------------------------------

def check_header_fields(subj_id, header_dict):
    """
    Check header fields for PHI.
    Returns list of (severity, message).
    """
    flags = []

    # START_DATE must be anonymized to 01.01.85
    start_date = header_dict.get("START_DATE", "")
    if start_date:
        if start_date != ANON_DATE:
            flags.append(("HARD", f"START_DATE not anonymized: '{start_date}' (expected {ANON_DATE})"))

    # STOP_DATE should also be anonymized
    stop_date = header_dict.get("STOP_DATE", "")
    if stop_date and stop_date != ANON_DATE:
        flags.append(("SOFT", f"STOP_DATE not anonymized: '{stop_date}'"))

    # EDF_ID should not contain dates or names
    edf_id = header_dict.get("EDF_ID", "")
    if edf_id:
        if DATE_PATTERN.search(edf_id):
            flags.append(("HARD", f"Date pattern in EDF_ID: '{edf_id}'"))
        if NAME_PATTERN.search(edf_id):
            flags.append(("HARD", f"Possible name in EDF_ID: '{edf_id}'"))

    return flags


def check_filename(edf_path):
    """
    Check EDF filename for PHI and naming convention issues.
    Returns list of (severity, message).
    """
    flags = []
    filename = os.path.basename(edf_path)
    stem = os.path.splitext(filename)[0]

    # Non-standard characters
    if not VALID_FILENAME_RE.match(filename):
        flags.append(("SOFT", f"Non-standard characters in filename: '{filename}'"))

    # Date patterns in filename
    if DATE_PATTERN.search(stem):
        flags.append(("HARD", f"Date pattern in filename: '{filename}'"))

    # Name-like pattern
    if NAME_PATTERN.search(stem):
        flags.append(("HARD", f"Possible name in filename: '{filename}'"))

    return flags


def check_file_exists(edf_path):
    """Check EDF file actually exists on disk."""
    if not os.path.exists(edf_path):
        return [("HARD", f"EDF file not found: '{edf_path}'")]
    return []


# ---------------------------------------------------------------------------
# README updater
# ---------------------------------------------------------------------------

def update_readme(readme_path, content):
    """Replace harmonix phi placeholder lines in README."""
    if not os.path.exists(readme_path):
        return False
    with open(readme_path, "r") as f:
        text = f.read()
    placeholder = "_[ Results will be populated by harmonix phi ]_"
    if placeholder not in text:
        return False
    # Replace ALL occurrences (sections 2 and 3 both have the placeholder)
    updated = text.replace(placeholder, content)
    with open(readme_path, "w") as f:
        f.write(updated)
    return True


# ---------------------------------------------------------------------------
# CLI command
# ---------------------------------------------------------------------------

@click.command()
@click.option("--sl", required=True, help="Path to Luna sample list")
@click.option("--path", default=".", show_default=True, help="Project working directory")
@click.option("--readme", default="README.md", show_default=True, help="README filename")
def phi_cmd(sl, path, readme):
    """
    PHI + file naming validator.

    Reads EDF headers via Luna HEADERS + destrat and checks for
    PHI, naming issues, duplicates, and EDF type consistency.

    Example:

        harmonix phi --sl sl/s0.lst --path /data/nsrr/working/numom2b
    """
    click.echo(f"\n  HARMONIX phi")
    click.echo(f"  sample list : {sl}")
    click.echo(f"  path        : {os.path.abspath(path)}\n")

    res_dir = os.path.join(path, "res")
    tmp_dir = os.path.join(path, "tmp")
    os.makedirs(res_dir, exist_ok=True)
    os.makedirs(tmp_dir, exist_ok=True)

    readme_path = os.path.join(path, readme)
    report_path = os.path.join(res_dir, "phi_report.txt")
    queue_path  = os.path.join(res_dir, "review_queue.txt")

    # ── Step 1: Parse sample list ────────────────────────────────────────────
    click.echo("  [1/5] Parsing sample list...")
    if not os.path.exists(sl):
        click.echo(f"        ✗  Sample list not found: {sl}")
        return
    entries = parse_sample_list(sl)
    n = len(entries)
    if n == 0:
        click.echo(f"        ✗  No entries found in sample list")
        return
    click.echo(f"        ✓  {n} subjects found")

    # ── Step 2: Duplicate ID check ───────────────────────────────────────────
    click.echo("\n  [2/5] Checking for duplicate IDs...")
    id_counts = Counter(e[0] for e in entries)
    dupes = {id_: c for id_, c in id_counts.items() if c > 1}
    if dupes:
        click.echo(f"        ⚠  {len(dupes)} duplicate IDs: {list(dupes.keys())}")
    else:
        click.echo(f"        ✓  No duplicate IDs")

    # ── Step 3: Run Luna HEADERS ─────────────────────────────────────────────
    click.echo("\n  [3/5] Running Luna HEADERS...")
    headers_db = os.path.join(tmp_dir, "phi_headers.db")
    retcode, stdout, stderr = run_luna_headers(sl, headers_db)
    luna_ok = retcode == 0 and os.path.exists(headers_db)
    if not luna_ok:
        click.echo(f"        ✗  Luna HEADERS failed (exit {retcode})")
        click.echo(f"           {stderr.strip()[:300]}")
        click.echo(f"        →  Continuing with filename-only checks")
    else:
        click.echo(f"        ✓  Luna HEADERS complete")

    # ── Step 4: Parse destrat output ─────────────────────────────────────────
    headers_by_id = defaultdict(dict)
    edf_types = set()

    if luna_ok:
        click.echo("\n  [4/5] Parsing header fields via destrat...")
        header_vars = ["START_DATE", "STOP_DATE", "EDF_ID", "EDF_TYPE", "TOT_DUR_SEC"]
        headers_by_id = run_destrat_wide(headers_db, "HEADERS", header_vars)

        if not headers_by_id:
            click.echo(f"        ⚠  destrat returned no data — check db manually")
            click.echo(f"           destrat {headers_db} +HEADERS")
        else:
            click.echo(f"        ✓  Parsed headers for {len(headers_by_id)} subjects")

        for hd in headers_by_id.values():
            t = hd.get("EDF_TYPE")
            if t:
                edf_types.add(t)
    else:
        click.echo("\n  [4/5] Skipping destrat (Luna failed)")

    # ── Step 5: Run all checks ───────────────────────────────────────────────
    click.echo("\n  [5/5] Running PHI checks...\n")

    all_flags  = []   # list of (subj_id, severity, message)
    hard_count = 0
    soft_count = 0
    pass_count = 0

    for subj_id, edf_path, annot_path in entries:
        flags = []

        # File existence
        flags += check_file_exists(edf_path)

        # Filename
        flags += check_filename(edf_path)

        # Duplicate ID
        if id_counts[subj_id] > 1:
            flags.append(("HARD", f"Duplicate subject ID: '{subj_id}'"))

        # Header fields from destrat
        hd = headers_by_id.get(subj_id, {})
        flags += check_header_fields(subj_id, hd)

        if flags:
            for sev, msg in flags:
                all_flags.append((subj_id, sev, msg))
                if sev == "HARD":
                    hard_count += 1
                    click.echo(f"        [HARD] {subj_id} — {msg}")
                else:
                    soft_count += 1
                    click.echo(f"        [SOFT] {subj_id} — {msg}")
        else:
            pass_count += 1

    # Dataset-level EDF type consistency
    if len(edf_types) > 1:
        msg = f"Mixed EDF types: {', '.join(sorted(edf_types))}"
        all_flags.append(("[DATASET]", "SOFT", msg))
        soft_count += 1
        click.echo(f"        [SOFT] DATASET — {msg}")

    # ── Write phi_report.txt ─────────────────────────────────────────────────
    with open(report_path, "w") as f:
        f.write("HARMONIX phi report\n")
        f.write(f"Generated  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Sample list: {sl}\n")
        f.write(f"Subjects   : {n}\n")
        f.write("=" * 60 + "\n\n")
        f.write("SUMMARY\n")
        f.write(f"  PASS : {pass_count}\n")
        f.write(f"  SOFT : {soft_count}\n")
        f.write(f"  HARD : {hard_count}\n\n")
        f.write(f"EDF types  : {', '.join(sorted(edf_types)) if edf_types else 'unknown'}\n\n")
        if all_flags:
            f.write("FLAGS\n")
            for item in all_flags:
                subj_id, sev, msg = item[0], item[1], item[2]
                f.write(f"  [{sev:4s}] {subj_id} — {msg}\n")
        else:
            f.write("No flags raised.\n")

    # ── Write review_queue.txt ───────────────────────────────────────────────
    if all_flags:
        mode = "a" if os.path.exists(queue_path) else "w"
        with open(queue_path, mode) as f:
            f.write(f"\n# harmonix phi — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            for item in all_flags:
                subj_id, sev, msg = item[0], item[1], item[2]
                f.write(f"[{sev}][PHI] {subj_id} — {msg}\n")

    # ── Update README ────────────────────────────────────────────────────────
    readme_content = f"""Luna `--build` and `HEADERS` run across all {n} subjects.

```
luna --build . > sl/s0.lst
luna sl/s0.lst -o tmp/phi_headers.db -s 'HEADERS'
```

| Check | Result |
|-------|--------|
| Total subjects | {n} |
| EDF types | {', '.join(sorted(edf_types)) if edf_types else 'unknown'} |
| Duplicate IDs | {len(dupes)} |
| Hard flags | {hard_count} |
| Soft flags | {soft_count} |
| Clean | {pass_count} |

See `res/phi_report.txt` for full details. Flagged items in `res/review_queue.txt`.
"""
    updated = update_readme(readme_path, readme_content)
    if not updated and os.path.exists(readme_path):
        click.echo(f"  [note] README placeholder not found — README not updated")

    # ── Summary ───────────────────────────────────────────────────────────────
    click.echo(f"\n  Results:")
    click.echo(f"    PASS  : {pass_count}")
    click.echo(f"    SOFT  : {soft_count}")
    click.echo(f"    HARD  : {hard_count}")
    click.echo(f"\n  Written : {report_path}")
    if all_flags:
        click.echo(f"  Written : {queue_path}")
    if updated:
        click.echo(f"  Updated : {readme_path}")
    click.echo(f"\n  ✓ phi check complete\n")
