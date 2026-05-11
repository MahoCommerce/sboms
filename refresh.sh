#!/usr/bin/env bash
#
# Enumerate public mahocommerce repos and (re)generate one CycloneDX SBOM per
# repo per ref (default branch + latest release tag) into sbom/<repo>/.
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

  if ! git clone --quiet "${clone_args[@]}" "https://github.com/$ORG/$repo.git" "$clonedir"; then
    echo "  ! clone failed for $repo@$ref, skipping"
    return 1
  fi

  mkdir -p "$(dirname "$outfile")"
  if ! syft scan "dir:$clonedir" -o "cyclonedx-json=$outfile" --quiet; then
    echo "  ! syft failed for $repo@$ref, skipping"
    return 1
  fi
}

while IFS= read -r repo; do
  echo "= $repo"

  # default branch (always regenerate; main moves)
  gen_sbom "$repo" "__default__" "sbom/$repo/main.cdx.json" "$WORK/$repo-default" || true

  # every published release tag; skip ones already on disk (release tags are immutable)
  while IFS= read -r tag; do
    [[ -z "$tag" ]] && continue
    safe_tag="${tag//\//_}"
    out="sbom/$repo/$safe_tag.cdx.json"
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
