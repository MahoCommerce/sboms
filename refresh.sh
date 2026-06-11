#!/usr/bin/env bash
#
# Enumerate public mahocommerce repos and (re)generate one CycloneDX SBOM per
# repo per ref (default branch + latest release tag) into sboms/<repo>/.
#
# Requires: gh, syft, reuse, git, jq, python3.

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

  # Summarize the project's own per-file SPDX headers (see #939) into a compact,
  # merged license report. `reuse lint --json` is REUSE's native machine-readable
  # report but enumerates every file (megabytes for a large repo); jq keeps REUSE's
  # `summary` verbatim and adds a per-license file count. Complements the
  # dependency-level CycloneDX SBOM above.
  #
  # reuse lint exits non-zero when a repo isn't fully REUSE-compliant (normal — not
  # every file carries a header) yet still emits valid JSON, so capture its output
  # and ignore its exit code; jq fails (non-zero) only on unparseable input.
  if command -v reuse > /dev/null 2>&1; then
    local reflabel licout lintjson
    reflabel="$(basename "${outfile%.cdx.json}")"
    licout="licenses/${outfile#sboms/}"
    licout="${licout%.cdx.json}.json"
    mkdir -p "$(dirname "$licout")"
    lintjson="$(reuse --root "$clonedir" lint --json 2> /dev/null || true)"
    if [[ -n "$lintjson" ]] && printf '%s' "$lintjson" | jq \
      --arg repo "$repo" --arg ref "$reflabel" '{
        repo: $repo,
        ref: $ref,
        reuse_spec_version: .reuse_spec_version,
        summary: .summary,
        license_file_counts: (
          [ (.files // [])[] | (.spdx_expressions // [])[] | .value ]
          | group_by(.) | map({key: .[0], value: length}) | from_entries
        )
      }' > "$licout"; then
      :
    else
      echo "  ! license summary failed for $repo@$ref, skipping"
      rm -f "$licout"
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
