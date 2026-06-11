#!/usr/bin/env python3
"""
Inject the project's declared license into a CycloneDX SBOM's
metadata.component.licenses.

Syft's directory scan leaves the top-level (source) component without a
license; it only resolves licenses for dependencies. The authoritative
license for the project itself is whatever the repo declares in its package
manifest, so we read it from composer.json (PHP) or package.json (JS) and
write it into metadata.component.licenses.

Usage: inject_license.py <clone_dir> <cdx_file>

No-op (exit 0) when no manifest/license is found or the SBOM already carries
a component license. Never fails the refresh.
"""

import json
import re
import sys
from pathlib import Path

# A bare SPDX license id (no spaces/operators): OSL-3.0, AFL-3.0, MIT, Apache-2.0
SPDX_TOKEN = re.compile(r"^[A-Za-z0-9.+-]+$")


def read_manifest_license(clone: Path):
    """Return ('expression', str) | ('ids', [str, ...]) | None."""
    composer = clone / "composer.json"
    if composer.is_file():
        try:
            lic = json.loads(composer.read_text()).get("license")
        except (ValueError, OSError):
            lic = None
        if isinstance(lic, str) and lic.strip():
            return ("ids", [lic.strip()])
        if isinstance(lic, list):
            ids = [x.strip() for x in lic if isinstance(x, str) and x.strip()]
            if ids:
                return ("ids", ids)

    pkg = clone / "package.json"
    if pkg.is_file():
        try:
            lic = json.loads(pkg.read_text()).get("license")
        except (ValueError, OSError):
            lic = None
        if isinstance(lic, str) and lic.strip():
            s = lic.strip()
            # package.json `license` is a single SPDX expression string.
            return ("ids", [s]) if SPDX_TOKEN.match(s) else ("expression", s.strip("()"))

    return None


def to_licenses(kind: str, value):
    """Map a parsed manifest license to a CycloneDX `licenses` array."""
    if kind == "expression":
        return [{"expression": value}]

    ids = value
    if len(ids) == 1:
        tok = ids[0]
        return [{"license": {"id": tok}}] if SPDX_TOKEN.match(tok) else [{"license": {"name": tok}}]

    # A composer `license` array is disjunctive (OR) per the Composer spec.
    if all(SPDX_TOKEN.match(t) for t in ids):
        return [{"expression": " OR ".join(ids)}]
    return [{"license": {"name": t}} for t in ids]


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(0)
    clone, cdx = Path(sys.argv[1]), Path(sys.argv[2])
    if not cdx.is_file():
        sys.exit(0)

    try:
        sbom = json.loads(cdx.read_text())
    except (ValueError, OSError):
        sys.exit(0)

    component = sbom.setdefault("metadata", {}).setdefault("component", {})
    if component.get("licenses"):
        sys.exit(0)  # syft already resolved a component license; leave it

    found = read_manifest_license(clone)
    if not found:
        sys.exit(0)

    component["licenses"] = to_licenses(*found)
    cdx.write_text(json.dumps(sbom, indent=2) + "\n")
    print(f"  + injected project license into {cdx.name}: {component['licenses']}")


if __name__ == "__main__":
    main()
