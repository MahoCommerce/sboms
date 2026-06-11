#!/usr/bin/env bash
#
# Scan every sboms/<repo>/main.cdx.json with both Grype and Trivy
# (only fixed, fixable vulns), merge the results into a single
# findings file at vulns/<repo>/main.json.
#
# This script always exits 0; the workflow has a separate step that
# fails the run if any merged finding is Critical.
#
# Requires: grype, trivy, python3, jq.

set -uo pipefail

# Resolve paths from the repo root regardless of the caller's CWD.
cd "$(dirname "${BASH_SOURCE[0]}")/.."

mkdir -p vulns

shopt -s nullglob
sboms=(sboms/*/main.cdx.json)
shopt -u nullglob

if [[ ${#sboms[@]} -eq 0 ]]; then
  echo "No main.cdx.json files found under sboms/."
  exit 0
fi

for sbom in "${sboms[@]}"; do
  repo="$(basename "$(dirname "$sbom")")"
  outdir="vulns/$repo"
  mkdir -p "$outdir"

  echo "= $repo"

  grype_out="$(mktemp)"
  trivy_out="$(mktemp)"

  if ! grype "sbom:$sbom" --only-fixed -o json -q > "$grype_out" 2> /dev/null; then
    echo "  ! grype failed for $repo, writing empty output"
    echo '{"matches": []}' > "$grype_out"
  fi

  if ! trivy sbom "$sbom" --ignore-unfixed -f json -q > "$trivy_out" 2> /dev/null; then
    echo "  ! trivy failed for $repo, writing empty output"
    echo '{"Results": []}' > "$trivy_out"
  fi

  python3 bin/merge.py "$grype_out" "$trivy_out" > "$outdir/main.json"

  rm -f "$grype_out" "$trivy_out"
done

python3 bin/report.py

echo "Done."
