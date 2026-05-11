#!/usr/bin/env python3
"""
Render a top-level VULNERABILITIES.md from all vulns/<repo>/main.json files.

Sections:
- Summary table: severity counts per repo + totals.
- Details: one block per Critical/High finding, grouped by repo.

Medium/Low/Negligible counts are in the table; for full details consult
the per-repo JSON files in vulns/.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

SEVERITIES = ["Critical", "High", "Medium", "Low", "Negligible", "Unknown"]
DETAIL_SEVERITIES = ["Critical", "High"]


def cve_link(cve: str | None) -> str:
    if not cve:
        return "(unknown)"
    if cve.startswith("CVE-"):
        return f"[{cve}](https://nvd.nist.gov/vuln/detail/{cve})"
    if cve.startswith("GHSA-"):
        return f"[{cve}](https://github.com/advisories/{cve})"
    return cve


def main() -> None:
    vulns_dir = Path("vulns")
    repos: dict[str, dict] = {}
    if vulns_dir.exists():
        for path in sorted(vulns_dir.glob("*/main.json")):
            with open(path) as fp:
                repos[path.parent.name] = json.load(fp)

    lines: list[str] = []
    lines.append("# Vulnerability Report")
    lines.append("")
    lines.append(
        f"_Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_"
    )
    lines.append("")
    lines.append(
        "Generated from the HEAD-of-default-branch SBOM of each tracked repo, "
        "scanned by Grype and Trivy. Only vulnerabilities with an upstream fix "
        "available are included. Per-repo JSON with the full finding detail is "
        "in [`vulns/`](vulns/)."
    )
    lines.append("")

    if not repos:
        lines.append("_No scan data yet._")
        Path("VULNERABILITIES.md").write_text("\n".join(lines) + "\n")
        return

    # Summary table
    lines.append("## Summary")
    lines.append("")
    lines.append("| Repo | " + " | ".join(SEVERITIES) + " |")
    lines.append("|------|" + "|".join(["---"] * len(SEVERITIES)) + "|")

    totals = {s: 0 for s in SEVERITIES}
    for repo, data in repos.items():
        summary = data.get("summary") or {}
        cells = []
        for s in SEVERITIES:
            count = summary.get(s, 0)
            totals[s] += count
            cells.append(str(count) if count else "—")
        lines.append(f"| `{repo}` | " + " | ".join(cells) + " |")

    total_cells = [f"**{totals[s]}**" if totals[s] else "—" for s in SEVERITIES]
    lines.append("| **Total** | " + " | ".join(total_cells) + " |")
    lines.append("")

    # Detail sections
    for sev in DETAIL_SEVERITIES:
        lines.append(f"## {sev} findings")
        lines.append("")
        any_in_section = False
        for repo, data in repos.items():
            findings = [
                f for f in (data.get("findings") or []) if f.get("severity") == sev
            ]
            if not findings:
                continue
            any_in_section = True
            lines.append(f"### `{repo}`")
            lines.append("")
            for f in findings:
                cve = cve_link(f.get("cve"))
                pkg = f.get("package") or "?"
                ver = f.get("version") or "?"
                fixed = ", ".join(f.get("fixed_in") or []) or "—"
                sources = ", ".join(f.get("sources") or [])
                lines.append(
                    f"- {cve} in `{pkg}@{ver}` — fix: `{fixed}` (via {sources})"
                )
            lines.append("")
        if not any_in_section:
            lines.append("_None._")
            lines.append("")

    Path("VULNERABILITIES.md").write_text("\n".join(lines) + "\n")
    print("Wrote VULNERABILITIES.md")


if __name__ == "__main__":
    main()
