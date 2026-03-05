"""
harmonix.scaffold
-----------------
Creates the standard NSRR folder structure and initializes
a README.md pre-filled with sections 0-13.
"""

import os
import click
from datetime import date


FOLDERS = [
    "files",
    "sl",
    "tmp",
    "res",
    "cmd",
    "nap",
    "dist",
    "viz",
]


README_TEMPLATE = """\
<!---
pandoc --standalone -c github-markdown.css -f gfm -t html -o {dataset}.html --metadata title="{dataset_upper}|NSRR" README.md
--->

# {dataset_upper}

_version 0.1 | {date}_

This document both contains and describes the steps used to process
PSG data from the __{dataset_upper}__ study. That is, this document is not only a
summary of the steps performed; rather it is a verbosely-commented
actual script, that should contain sufficient information to
allow most steps to be reproduced with only moderate effort.

Below, to process these data we use Luna (documented
[here](http://zzz.bwh.harvard.edu/luna)) as well as R and standard unix
command-line tools. 

Key points in this document:

 - creation of the harmonized set of EDFs and annotation files
 - alignment and checking of staging data and EDF signals
 - identification of duplicate or truncated files
 - review of distributions for key signals
 - flagging site-to-site variation in signals
 - visual summary reviews created for each EDF
 - confirmation of expected properties for key macro- and micro-architecture metrics


## Table of Contents

 0) [Preliminaries](#0-preliminaries)
 1) [Key design factors](#1-key-design-factors)
 2) [EDF checks](#2-edf-checks)
 3) [Identifiers](#3-identifiers)
 4) [Signal review](#4-signal-review)
 5) [Annotation review](#5-annotation-review)
 6) [Manual staging](#6-manual-staging)
 7) [NAP signal mappings](#7-nap-signal-mappings)
 8) [NAP annotation mappings](#8-nap-annotation-mappings)
 9) [Encodings](#9-encodings)
 10) [Interim report](#10-interim-report)
 11) [Running NAP](#11-running-nap)
 12) [Compiling the distribution dataset](#12-compiling-the-distribution-dataset)
 13) [Depositing an _as is_ dataset](#13-depositing-an-as-is-dataset)


## 0) Preliminaries

### ERIS Folder structure

This pipeline was run on the ERISTwo cluster.

| Folder | Description |
|----|----|
| `{path}/{dataset}-edfs/` | Original deposited data |
| `{path}/` | Working directory for processing |

Folder structure created by `harmonix scaffold`:

| Folder | Contents |
|----|----|
| `files/` | Other relevant, original non-data files (e.g. descriptive PDFs, meta-data as XLS/PPTs, etc) |
| `sl/` | All derived sample lists |
| `tmp/` | Scratch folder, e.g. including all raw outputs from Luna runs (`.db` files prior to extraction to `res/`) |
| `cmd/` | Any Luna scripts |
| `res/` | Final compiled higher-level outputs |
| `nap/` | NAP automatically generates this folder with NAP output and harmonized EDFs/annotations |
| `dist/` | Final distribution folder, i.e. copied EDFs/annotations from `nap/` that will be imported into NSRR |
| `viz/` | Final visual summaries (auto-generated HTML) for the distribution dataset |

```
cd {path}
mkdir files sl tmp res nap dist cmd viz
```


## 1) Key design factors

<!-- 
TODO: Fill in manually.
- Number of subjects
- Number of EDFs per subject
- Sites
- PSG system used
- Staging source
- Any known dataset quirks
-->

_[ To be completed manually ]_


## 2) EDF checks

<!-- Auto-populated by: harmonix phi -->

Build an EDF-only sample list:

```
luna --build {dataset}-edfs/ > sl/s0.lst
```

Check validity of all EDFs:

```
luna sl/s0.lst -s DESC
```

Run HEADERS to summarize EDF headers:

```
luna sl/s0.lst -o tmp/headers.db -s 'HEADERS signals'
```

_[ Results will be populated by harmonix phi ]_


## 3) Identifiers

<!-- Auto-populated by: harmonix phi -->

_[ Results will be populated by harmonix phi ]_


## 4) Signal review

<!-- Auto-populated by: harmonix qc + harmonix coverage -->

_[ Results will be populated by harmonix qc and harmonix coverage ]_


## 5) Annotation review

<!-- Auto-populated by: harmonix qc -->

_[ Results will be populated by harmonix qc ]_


## 6) Manual staging

<!-- Fill in manually if staging required special handling -->

_[ To be completed manually if applicable ]_


## 7) NAP signal mappings

<!-- Auto-populated by: harmonix cmap -->

_[ Results will be populated by harmonix cmap ]_


## 8) NAP annotation mappings

<!-- Fill in manually -->

_[ To be completed manually ]_


## 9) Encodings

<!-- Auto-populated -->

_[ To be populated ]_


## 10) Interim report

<!-- Auto-populated by: harmonix issues -->

_[ Results will be populated by harmonix issues ]_


## 11) Running NAP

<!-- Auto-populated -->

_[ To be populated ]_


## 12) Compiling the distribution dataset

<!-- Auto-populated -->

_[ To be populated ]_


## 13) Depositing an _as is_ dataset

<!-- Auto-populated -->

_[ To be populated ]_
"""


def scaffold(dataset: str, path: str, readme_only: bool = False):
    """
    Create NSRR harmonization folder structure and initialize README.
    """
    path = os.path.abspath(path)

    # Create working directory if it doesn't exist
    os.makedirs(path, exist_ok=True)

    if not readme_only:
        # Create standard folders
        created = []
        for folder in FOLDERS:
            folder_path = os.path.join(path, folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                created.append(folder)
            else:
                click.echo(f"  [skip] {folder}/ already exists")

        if created:
            click.echo(f"\n  Created folders in {path}:")
            for f in created:
                click.echo(f"    + {f}/")

    # Write README
    readme_path = os.path.join(path, "README.md")
    if os.path.exists(readme_path):
        click.echo(f"\n  [skip] README.md already exists — not overwriting")
    else:
        readme_content = README_TEMPLATE.format(
            dataset=dataset.lower(),
            dataset_upper=dataset.upper(),
            date=date.today().strftime("%d-%b-%Y"),
            path=path,
        )
        with open(readme_path, "w") as f:
            f.write(readme_content)
        click.echo(f"\n  Created README.md")

    click.echo(f"\n  ✓ Project scaffolded at: {path}")
    click.echo(f"  Next step: fill in README Section 1 (key design factors),")
    click.echo(f"  then run: harmonix phi --sl sl/s0.lst\n")


@click.command()
@click.option("--dataset", required=True, help="Dataset name (e.g. apples)")
@click.option("--path", required=True, help="Working directory path")
@click.option("--readme-only", is_flag=True, default=False, help="Only create README, skip folders")
def scaffold_cmd(dataset, path, readme_only):
    """
    Scaffold a new HARMONIX harmonization project.

    Creates the standard NSRR folder structure and initializes
    a README.md pre-filled with sections 0-13.

    Example:

        harmonix scaffold --dataset apples --path /data/nsrr/working/apples
    """
    click.echo(f"\n  HARMONIX scaffold")
    click.echo(f"  dataset : {dataset.upper()}")
    click.echo(f"  path    : {os.path.abspath(path)}\n")
    scaffold(dataset, path, readme_only)
