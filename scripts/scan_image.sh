#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
image=${1:?Usage: bash scripts/scan_image.sh IMAGE}
scan_dir=$(mktemp -d)
trap 'rm -rf "$scan_dir"' EXIT
docker save "$image" -o "$scan_dir/image.tar"
# Scan an exported image; the scanner gets no Docker socket or AWS credentials.
docker run --rm -v "$scan_dir:/scan" aquasec/trivy:0.74.0 image \
  --input /scan/image.tar --scanners vuln --format json --output /scan/trivy.json
cp "$scan_dir/trivy.json" trivy.json
python3 scripts/check_scan.py trivy.json
