"""
harmonix.status
---------------
Terminal dashboard for a HARMONIX project.

Reads all generated outputs (res/, tmp/, README.md) and prints
a rich colored summary of pipeline progress, flags, and next steps.

Usage:
    harmonix status --path /data/nsrr/working/numom2b
"""

import os
import re
import click
from datetime import datetime
from collections import defaultdict

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.columns import Columns
    from rich import box
    from rich.text import Text
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

console = Console() if HAS_RICH else None


# ---------------------------------------------------------------------------
# Project state reader
# ---------------------------------------------------------------------------

TOOLS = [
    ("scaffold", "Project scaffolded",        "res/phi_report.txt",      None),
    ("phi",      "PHI + file naming check",   "res/phi_report.txt",      "harmonix phi --sl sl/s0.lst --path ."),
    ("cmap",     "Channel mapping",           "res/cmap_report.txt",     "harmonix cmap --sl sl/s0.lst --path ."),
    ("qc",       "Signal quality check",      "res/qc_report.txt",       "harmonix qc --sl sl/s0.lst --path ."),
    ("coverage", "Signal coverage dashboard", "res/coverage_report.txt", "harmonix coverage --path ."),
    ("issues",   "Issues file",               "res/issues.txt",          "harmonix issues --path ."),
    ("report",   "Final README report",       "dist/",                   "harmonix report --path ."),
]


def detect_dataset_name(path):
    """Try to read dataset name from README."""
    readme = os.path.join(path, "README.md")
    if not os.path.exists(readme):
        return os.path.basename(os.path.abspath(path)).upper()
    with open(readme) as f:
        for line in f:
            m = re.match(r"^# (.+)", line.strip())
            if m:
                return m.group(1).strip()
    return os.path.basename(os.path.abspath(path)).upper()


def check_scaffold(path):
    """Check if project was scaffolded."""
    required = ["files", "sl", "tmp", "res", "cmd", "nap", "dist", "viz"]
    existing = [d for d in required if os.path.isdir(os.path.join(path, d))]
    if len(existing) == len(required):
        return "done", f"All {len(required)} folders present"
    elif len(existing) > 0:
        return "partial", f"{len(existing)}/{len(required)} folders present"
    return "pending", None


def parse_phi_report(path):
    """Parse res/phi_report.txt for summary stats."""
    report = os.path.join(path, "res", "phi_report.txt")
    if not os.path.exists(report):
        return "pending", None

    stats = {}
    with open(report) as f:
        for line in f:
            line = line.strip()
            for key in ["PASS", "SOFT", "HARD", "Generated", "EDF types"]:
                if line.startswith(key):
                    parts = line.split(":")
                    if len(parts) >= 2:
                        stats[key] = parts[1].strip()

    hard = int(stats.get("HARD", 0))
    soft = int(stats.get("SOFT", 0))
    passed = int(stats.get("PASS", 0))
    generated = stats.get("Generated", "unknown")
    edf_types = stats.get("EDF types", "unknown")

    status = "done" if hard == 0 else "flagged"
    summary = f"{hard} HARD · {soft} SOFT · {passed} PASS  |  {edf_types}"
    return status, summary


def parse_generic_report(path, filename):
    """Parse any res/*_report.txt for basic summary."""
    report = os.path.join(path, "res", filename)
    if not os.path.exists(report):
        return "pending", None
    mtime = os.path.getmtime(report)
    run_time = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
    with open(report) as f:
        lines = [l.strip() for l in f if l.strip()]
    summary_lines = [l for l in lines if any(k in l for k in ["PASS", "HARD", "SOFT", "Total", "Coverage"])]
    summary = " · ".join(summary_lines[:3]) if summary_lines else f"run: {run_time}"
    return "done", summary


def parse_review_queue(path):
    """Parse res/review_queue.txt into categorized flags."""
    queue = os.path.join(path, "res", "review_queue.txt")
    if not os.path.exists(queue):
        return []

    flags = []
    with open(queue) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Format: [HARD][PHI] subj_id — message
            m = re.match(r"\[(\w+)\]\[(\w+)\]\s+(.+?)\s+—\s+(.+)", line)
            if m:
                flags.append({
                    "severity": m.group(1),
                    "tool":     m.group(2),
                    "subject":  m.group(3),
                    "message":  m.group(4),
                })
    return flags


def get_last_run(path):
    """Get the most recent modification time across res/ files."""
    res_dir = os.path.join(path, "res")
    if not os.path.isdir(res_dir):
        return "never"
    times = []
    for f in os.listdir(res_dir):
        fp = os.path.join(res_dir, f)
        if os.path.isfile(fp):
            times.append(os.path.getmtime(fp))
    if not times:
        return "never"
    return datetime.fromtimestamp(max(times)).strftime("%Y-%m-%d %H:%M")


def determine_next_step(tool_statuses):
    """Return the next recommended command."""
    next_steps = {
        "phi":      "harmonix phi --sl sl/s0.lst --path .",
        "cmap":     "harmonix cmap --sl sl/s0.lst --path .",
        "qc":       "harmonix qc --sl sl/s0.lst --path .",
        "coverage": "harmonix coverage --path .",
        "issues":   "harmonix issues --path .",
        "report":   "harmonix report --path .",
    }
    order = ["phi", "cmap", "qc", "coverage", "issues", "report"]
    for tool in order:
        if tool_statuses.get(tool) == "pending":
            return next_steps[tool]
    return "All tools complete — ready to deposit!"


# ---------------------------------------------------------------------------
# Rich dashboard renderer
# ---------------------------------------------------------------------------

def render_rich(path, dataset_name, tool_statuses, tool_summaries, flags, last_run, next_step):
    c = Console(width=80)

    # Header
    c.print()
    c.print(Panel(
        f"[bold white]HARMONIX[/]  ·  [bold cyan]{dataset_name}[/]  ·  last run: [dim]{last_run}[/]",
        box=box.DOUBLE,
        style="bold blue",
        padding=(0, 2),
    ))
    c.print()

    # Pipeline progress table
    c.print("[bold]  PIPELINE PROGRESS[/]")
    c.print("  " + "─" * 54)

    status_icons = {
        "done":    "[bold green]✅[/]",
        "flagged": "[bold yellow]⚠️ [/]",
        "partial": "[bold yellow]🔶[/]",
        "pending": "[dim]⬜[/]",
    }

    tool_labels = {
        "scaffold": "scaffold",
        "phi":      "phi     ",
        "cmap":     "cmap    ",
        "qc":       "qc      ",
        "coverage": "coverage",
        "issues":   "issues  ",
        "report":   "report  ",
    }

    for tool, label in tool_labels.items():
        status = tool_statuses.get(tool, "pending")
        icon = status_icons.get(status, "[dim]⬜[/]")
        summary = tool_summaries.get(tool, "")
        summary_str = f"[dim]{summary}[/]" if summary else "[dim]not run[/]"
        c.print(f"  {icon}  [cyan]{label}[/]  {summary_str}")

    c.print()

    # Review queue
    hard_flags = [f for f in flags if f["severity"] == "HARD"]
    soft_flags = [f for f in flags if f["severity"] == "SOFT"]

    c.print(f"[bold]  REVIEW QUEUE[/]  [dim]({len(flags)} items — {len(hard_flags)} HARD, {len(soft_flags)} SOFT)[/]")
    c.print("  " + "─" * 54)

    if not flags:
        c.print("  [dim green]No flags raised[/]")
    else:
        # Show all HARD first, then SOFT (max 15 total)
        shown = 0
        for f in hard_flags[:10]:
            c.print(f"  [bold red]🔴 HARD[/]  [[dim]{f['tool']}[/]]  [white]{f['subject']}[/]  [dim]— {f['message'][:55]}[/]")
            shown += 1
        for f in soft_flags[:5]:
            c.print(f"  [bold yellow]🟡 SOFT[/]  [[dim]{f['tool']}[/]]  [white]{f['subject']}[/]  [dim]— {f['message'][:55]}[/]")
            shown += 1
        remaining = len(flags) - shown
        if remaining > 0:
            c.print(f"  [dim]... and {remaining} more — see res/review_queue.txt[/]")

    c.print()

    # Next step
    c.print(Panel(
        f"[bold]NEXT STEP[/]  →  [bold cyan]{next_step}[/]",
        style="dim",
        padding=(0, 2),
    ))
    c.print()


# ---------------------------------------------------------------------------
# Fallback plain text renderer
# ---------------------------------------------------------------------------

def render_plain(path, dataset_name, tool_statuses, tool_summaries, flags, last_run, next_step):
    print(f"\n  HARMONIX  ·  {dataset_name}  ·  last run: {last_run}")
    print("  " + "=" * 54)
    print("\n  PIPELINE PROGRESS")
    print("  " + "-" * 54)
    for tool in ["scaffold", "phi", "cmap", "qc", "coverage", "issues", "report"]:
        status = tool_statuses.get(tool, "pending")
        icon = {"done": "[✅]", "flagged": "[⚠️]", "partial": "[🔶]", "pending": "[ ]"}.get(status, "[ ]")
        summary = tool_summaries.get(tool, "not run")
        print(f"  {icon}  {tool:<10}  {summary}")
    print(f"\n  REVIEW QUEUE  ({len(flags)} items)")
    print("  " + "-" * 54)
    if not flags:
        print("  No flags raised")
    else:
        for f in flags[:15]:
            print(f"  [{f['severity']}][{f['tool']}] {f['subject']} — {f['message'][:60]}")
        if len(flags) > 15:
            print(f"  ... and {len(flags) - 15} more — see res/review_queue.txt")
    print(f"\n  NEXT STEP  →  {next_step}")
    print()


# ---------------------------------------------------------------------------
# CLI command
# ---------------------------------------------------------------------------

@click.command()
@click.option("--path", default=".", show_default=True, help="Project working directory")
def status_cmd(path):
    """
    Show project status dashboard.

    Reads all generated outputs and prints a colored terminal
    summary of pipeline progress, flags, and next steps.

    Example:

        harmonix status --path /data/nsrr/working/numom2b
    """
    path = os.path.abspath(path)

    if not os.path.isdir(path):
        click.echo(f"  ✗ Path not found: {path}")
        return

    dataset_name = detect_dataset_name(path)
    last_run = get_last_run(path)
    flags = parse_review_queue(path)

    # Determine status of each tool
    tool_statuses = {}
    tool_summaries = {}

    # scaffold
    s, summary = check_scaffold(path)
    tool_statuses["scaffold"] = s
    tool_summaries["scaffold"] = summary or ""

    # phi
    s, summary = parse_phi_report(path)
    tool_statuses["phi"] = s
    tool_summaries["phi"] = summary or ""

    # cmap, qc, coverage, issues
    for tool, report_file in [
        ("cmap",     "cmap_report.txt"),
        ("qc",       "qc_report.txt"),
        ("coverage", "coverage_report.txt"),
        ("issues",   "issues.txt"),
    ]:
        s, summary = parse_generic_report(path, report_file)
        tool_statuses[tool] = s
        tool_summaries[tool] = summary or ""

    # report (check dist/ folder)
    dist_dir = os.path.join(path, "dist")
    if os.path.isdir(dist_dir) and os.listdir(dist_dir):
        tool_statuses["report"] = "done"
        tool_summaries["report"] = "distribution folder populated"
    else:
        tool_statuses["report"] = "pending"

    next_step = determine_next_step(tool_statuses)

    if HAS_RICH:
        render_rich(path, dataset_name, tool_statuses, tool_summaries, flags, last_run, next_step)
    else:
        render_plain(path, dataset_name, tool_statuses, tool_summaries, flags, last_run, next_step)
