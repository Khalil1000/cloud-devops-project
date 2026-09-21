#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
system=$(uname -s | tr '[:upper:]' '[:lower:]')
machine=$(uname -m)
case "$machine" in x86_64) machine=amd64 ;; aarch64|arm64) machine=arm64 ;; *) exit 1 ;; esac
case "$system" in linux|darwin) ;; *) echo "Use macOS, Linux or Windows WSL2."; exit 1 ;; esac
version=1.14.6
archive="terraform_${version}_${system}_${machine}.zip"
temp_dir=$(mktemp -d)
trap 'rm -rf "$temp_dir"' EXIT
curl -fsSL "https://releases.hashicorp.com/terraform/$version/$archive" -o "$temp_dir/$archive"
curl -fsSL "https://releases.hashicorp.com/terraform/$version/terraform_${version}_SHA256SUMS" -o "$temp_dir/checksums"
python3 - "$temp_dir" "$archive" <<'PY'
import hashlib, pathlib, sys, zipfile
folder, name = pathlib.Path(sys.argv[1]), sys.argv[2]
expected = next(line.split()[0] for line in (folder / "checksums").read_text().splitlines() if line.split()[-1] == name)
if hashlib.sha256((folder / name).read_bytes()).hexdigest() != expected:
    raise SystemExit("Terraform checksum mismatch")
with zipfile.ZipFile(folder / name) as archive:
    archive.extract("terraform", folder)
print("Verified Terraform download")
PY
mkdir -p tools/bin
install -m 0755 "$temp_dir/terraform" tools/bin/terraform
echo 'Run: export PATH="$PWD/tools/bin:$PATH"'
