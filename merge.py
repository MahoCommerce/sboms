#!/usr/bin/env python3
"""
Merge Grype + Trivy JSON scan output into a unified findings list.

Usage: merge.py <grype.json> <trivy.json>

Output (stdout): {"findings": [...]} sorted by severity desc, then CVE id.
Each finding is deduped by (cve, package, version) and records which
scanner(s) flagged it. When scanners disagree on severity, the higher
value wins.
"""

import json
import sys
from typing import Any

SEVERITY_ORDER = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1,
    "Negligible": 0,
    "Unknown": -1,
}


def normalize_severity(sev: str | None) -> str:
    if not sev:
        return "Unknown"
    s = sev.strip().capitalize()
    return s if s in SEVERITY_ORDER else "Unknown"


def from_grype(data: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for m in data.get("matches") or []:
        v = m.get("vulnerability") or {}
        a = m.get("artifact") or {}
        out.append({
            "cve": v.get("id"),
            "package": a.get("name"),
            "version": a.get("version"),
            "purl": a.get("purl"),
            "severity": normalize_severity(v.get("severity")),
            "fixed_in": list((v.get("fix") or {}).get("versions") or []),
            "source": "grype",
        })
    return out


def from_trivy(data: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for r in data.get("Results") or []:
        for v in r.get("Vulnerabilities") or []:
            ident = v.get("PkgIdentifier") or {}
            fixed = v.get("FixedVersion")
            out.append({
                "cve": v.get("VulnerabilityID"),
                "package": v.get("PkgName"),
                "version": v.get("InstalledVersion"),
                "purl": ident.get("PURL"),
                "severity": normalize_severity(v.get("Severity")),
                "fixed_in": [fixed] if fixed else [],
                "source": "trivy",
            })
    return out


def merge(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    bucket: dict[tuple, dict[str, Any]] = {}
    for f in findings:
        key = (f["cve"], f["package"], f["version"])
        if key not in bucket:
            entry = {k: v for k, v in f.items() if k != "source"}
            entry["sources"] = [f["source"]]
            bucket[key] = entry
            continue
        entry = bucket[key]
        if f["source"] not in entry["sources"]:
            entry["sources"].append(f["source"])
        if SEVERITY_ORDER[f["severity"]] > SEVERITY_ORDER[entry["severity"]]:
            entry["severity"] = f["severity"]
        for fv in f["fixed_in"]:
            if fv not in entry["fixed_in"]:
                entry["fixed_in"].append(fv)
        if entry.get("purl") is None and f.get("purl"):
            entry["purl"] = f["purl"]
    return list(bucket.values())


def main() -> None:
    if len(sys.argv) != 3:
        print("usage: merge.py <grype.json> <trivy.json>", file=sys.stderr)
        sys.exit(2)

    with open(sys.argv[1]) as fp:
        grype = from_grype(json.load(fp))
    with open(sys.argv[2]) as fp:
        trivy = from_trivy(json.load(fp))

    merged = merge(grype + trivy)
    merged.sort(key=lambda f: (-SEVERITY_ORDER[f["severity"]], f["cve"] or ""))

    counts: dict[str, int] = {}
    for f in merged:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1

    json.dump({"summary": counts, "findings": merged}, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
