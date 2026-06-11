#!/usr/bin/env bash
#
# Enumerate public mahocommerce repos and (re)generate one CycloneDX SBOM per
# repo per ref (default branch + latest release tag) into sboms/<repo>/.
#
# Requires: gh, syft, git, jq.

set -euo pipefail

ORG="mahocommerce"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# --- enumerate active public, non-fork repos -----------------------------
echo "Enumerating $ORG public repos..."
gh repo list "$ORG" \
  --visibility public \
  --no-archived \
  --source \
  --limit 500 \
  --json name \
  --jq '.[].name' \
  | grep -Ev '^maho-language' \
  | sort > "$WORK/repos.txt"

echo "Found $(wc -l < "$WORK/repos.txt") repos."

# --- generate SBOMs ------------------------------------------------------
gen_sbom() {
  local repo="$1" ref="$2" outfile="$3" clonedir="$4"
  local clone_args=(--depth 1)
  [[ "$ref" != "__default__" ]] && clone_args+=(--branch "$ref")

  if ! git -c advice.detachedHead=false clone --quiet "${clone_args[@]}" "https://github.com/$ORG/$repo.git" "$clonedir" 2> >(grep -v 'is not a commit!' >&2); then
    echo "  ! clone failed for $repo@$ref, skipping"
    return 1
  fi

  mkdir -p "$(dirname "$outfile")"
  if ! syft scan "dir:$clonedir" -o "cyclonedx-json=$outfile" --quiet; then
    echo "  ! syft failed for $repo@$ref, skipping"
    return 1
  fi

  # Set the project's own license on the SBOM's main component. Syft resolves
  # dependency licenses but leaves the top-level (source) component empty; the
  # authoritative project license is what the repo declares in composer.json /
  # package.json. Best-effort: never fail the refresh over it.
  python3 inject_license.py "$clonedir" "$outfile" || true

  # Emit a REUSE/SPDX document from the repo's per-file SPDX headers (see #939).
  # This is the file-level license inventory that consumes the SPDX headers,
  # complementing the dependency-level CycloneDX SBOM above.
  if command -v reuse > /dev/null 2>&1; then
    local spdxout="spdx/${outfile#sboms/}"
    spdxout="${spdxout%.cdx.json}.spdx"
    mkdir -p "$(dirname "$spdxout")"
    if ! reuse --root "$clonedir" spdx > "$spdxout" 2> /dev/null; then
      echo "  ! reuse spdx failed for $repo@$ref, skipping SPDX doc"
      rm -f "$spdxout"
    fi
  fi
}

while IFS= read -r repo; do
  echo "= $repo"

  # default branch (always regenerate; main moves)
  gen_sbom "$repo" "__default__" "sboms/$repo/main.cdx.json" "$WORK/$repo-default" || true

  # every published release tag; skip ones already on disk (release tags are immutable)
  while IFS= read -r tag; do
    [[ -z "$tag" ]] && continue
    safe_tag="${tag//\//_}"
    out="sboms/$repo/$safe_tag.cdx.json"
    [[ -f "$out" ]] && continue
    gen_sbom "$repo" "$tag" "$out" "$WORK/$repo-$safe_tag" || true
  done < <(
    gh release list --repo "$ORG/$repo" \
      --limit 1000 \
      --json tagName,isDraft \
      --jq '.[] | select(.isDraft == false) | .tagName' \
      2>/dev/null || true
  )
done < "$WORK/repos.txt"

echo "Done."
