#!/usr/bin/env python3
"""
Condense `reuse lint --json` into a compact, REUSE-native license summary of a
repo's own source files.

`reuse lint --json` is REUSE's own machine-readable report, but it enumerates
every file (5+ MB for a large repo). This keeps REUSE's native `summary` object
verbatim (used_licenses, files_total, files_with_copyright_info,
files_with_licensing_info, compliant) and adds a per-license file count derived
from each file's `spdx_expressions`. The result is small and deterministic, so
the committed summary only changes when licensing actually changes.

Usage: reuse --root <dir> lint --json | license_summary.py <repo> <ref>

`reuse lint` exits non-zero when a repo is not fully REUSE-compliant (normal
here — not every file carries a header), but still emits valid JSON, so the
caller should ignore reuse's exit code and rely on this script: it exits
non-zero only when the input is not parseable JSON.
"""

import json
import sys
from collections import Counter


def main() -> None:
    repo = sys.argv[1] if len(sys.argv) > 1 else ""
    ref = sys.argv[2] if len(sys.argv) > 2 else ""

    try:
        data = json.load(sys.stdin)
    except (ValueError, OSError):
        sys.exit(1)

    counts: Counter = Counter()
    for entry in data.get("files", []):
        for expr in entry.get("spdx_expressions", []):
            # REUSE >= 6 emits {"value": "OSL-3.0", ...}; older versions a bare string.
            value = expr.get("value") if isinstance(expr, dict) else expr
            if value:
                counts[value] += 1

    summary = {
        "repo": repo,
        "ref": ref,
        "reuse_spec_version": data.get("reuse_spec_version"),
        "summary": data.get("summary", {}),
        "license_file_counts": dict(sorted(counts.items())),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
