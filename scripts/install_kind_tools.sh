#!/usr/bin/env bash
set -euo pipefail
# Installs only kind and kubectl into ./tools/bin; does not need sudo.
cd "$(dirname "$0")/.."
system=$(uname -s | tr '[:upper:]' '[:lower:]')
machine=$(uname -m)
case "$machine" in
  x86_64) machine=amd64 ;;
  aarch64|arm64) machine=arm64 ;;
  *) echo "Unsupported architecture: $machine"; exit 1 ;;
esac
case "$system" in linux|darwin) ;; *) echo "Use macOS, Linux or Windows WSL2."; exit 1 ;; esac
mkdir -p tools/bin
temp_dir=$(mktemp -d)
trap 'rm -rf "$temp_dir"' EXIT
curl -fsSL "https://github.com/kubernetes-sigs/kind/releases/download/v0.31.0/kind-${system}-${machine}" -o "$temp_dir/kind"
curl -fsSL "https://github.com/kubernetes-sigs/kind/releases/download/v0.31.0/kind-${system}-${machine}.sha256sum" -o "$temp_dir/kind.sha256"
curl -fsSL "https://dl.k8s.io/release/v1.35.0/bin/${system}/${machine}/kubectl" -o "$temp_dir/kubectl"
curl -fsSL "https://dl.k8s.io/release/v1.35.0/bin/${system}/${machine}/kubectl.sha256" -o "$temp_dir/kubectl.sha256"
python3 - "$temp_dir" <<'PY'
import hashlib, pathlib, sys
folder = pathlib.Path(sys.argv[1])
for name in ("kind", "kubectl"):
    expected = (folder / (name + ".sha256")).read_text().split()[0]
    actual = hashlib.sha256((folder / name).read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f"Checksum mismatch for {name}")
    print(f"Verified {name}")
PY
install -m 0755 "$temp_dir/kind" tools/bin/kind
install -m 0755 "$temp_dir/kubectl" tools/bin/kubectl
echo 'Run: export PATH="$PWD/tools/bin:$PATH"'
