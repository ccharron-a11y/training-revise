#!/usr/bin/env bash
# Package the scorm/ folder into an LMS-ready SCORM 1.2 zip (imsmanifest.xml at the zip root).
set -euo pipefail
cd "$(dirname "$0")"
out="dist/QAQC_Field_Documentation_Training_SCORM12.zip"
mkdir -p dist
rm -f "$out"
(cd scorm && zip -qr -X "../$out" .)
echo "Built $out"
