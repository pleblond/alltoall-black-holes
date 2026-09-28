#!/usr/bin/env bash
# Reproducible acquisition of the NMMA SVD grids used by D7 milestones 1-4.
# Usage: bash d7_public_models/fetch_models.sh [destdir (default ./nmma_models)]
# Downloads ~550 MB (core + ps1 griz for nsbh/Ka2017 + lm core for the audit).
# Verifies against d7_public_models/SHA256SUMS when sha256sum is present.
set -euo pipefail
DEST="${1:-./nmma_models}"
BASE="https://gitlab.com/Theodlz/nmma-models/raw/main/models"
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$DEST/Bu2019nsbh" "$DEST/Ka2017"
fetch() { curl -sSL -o "$DEST/$1" "$BASE/$1"; echo "got $1"; }
fetch Bu2019nsbh.joblib
fetch Ka2017.joblib
fetch Bu2019lm.joblib
for f in ps1__g ps1__r ps1__i ps1__z; do
  fetch "Bu2019nsbh/$f.joblib"
  fetch "Ka2017/$f.joblib"
done
if command -v sha256sum >/dev/null; then
  (cd "$DEST" && sha256sum -c "$HERE/SHA256SUMS")
else
  echo "sha256sum not found; skipping verification"
fi
