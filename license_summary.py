#!/usr/bin/env python3
"""
Condense `reuse spdx` output (a full per-file SPDX BOM — megabytes for a large
repo) into a compact, deterministic license summary of the project's own files.

Reads the SPDX tag-value document on stdin and writes a small JSON object:
  {repo, ref, files_total, files_licensed, files_unlicensed, licenses: {id: count}}

`licenses` aggregates the per-file `SPDX-License-Identifier` headers REUSE
extracted, so it answers "how is our own source licensed, and how much of it."

Deterministic by design: it ignores REUSE's volatile DocumentNamespace UUID and
Created timestamp, so the committed summary only changes when licensing actually
changes — no daily churn.

Usage: reuse --root <dir> spdx | license_summary.py <repo> <ref>
"""

import json
import sys
from collections import Counter

SKIP = {"NONE", "NOASSERTION", ""}


def main() -> None:
    repo = sys.argv[1] if len(sys.argv) > 1 else ""
    ref = sys.argv[2] if len(sys.argv) > 2 else ""

    files_total = 0
    files_licensed = 0
    in_file = False
    file_licensed = False
    licenses: Counter = Counter()

    for raw in sys.stdin:
        line = raw.rstrip("\n")
        if line.startswith("FileName:"):
            if in_file and file_licensed:
                files_licensed += 1
            in_file = True
            file_licensed = False
            files_total += 1
        elif line.startswith("LicenseInfoInFile:"):
            lic = line.split(":", 1)[1].strip()
            if lic not in SKIP:
                licenses[lic] += 1
                file_licensed = True
    if in_file and file_licensed:
        files_licensed += 1

    summary = {
        "repo": repo,
        "ref": ref,
        "files_total": files_total,
        "files_licensed": files_licensed,
        "files_unlicensed": files_total - files_licensed,
        "licenses": dict(sorted(licenses.items())),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
