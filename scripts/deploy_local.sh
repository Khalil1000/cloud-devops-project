#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
image=${1:?Usage: bash scripts/deploy_local.sh IMAGE VERSION}
version=${2:?Supply the release version to verify}
context=kind-portfolio
namespace=portfolio
manifest=$(mktemp)
port_log=$(mktemp)
port_pid=""
cleanup() {
  if [[ -n "$port_pid" ]]; then kill "$port_pid" 2>/dev/null || true; fi
  rm -f "$manifest" "$port_log"
}
trap cleanup EXIT

# All kubectl calls are explicitly scoped to this local cluster.
kind load docker-image "$image" --name portfolio
kubectl --context "$context" apply -f k8s/namespace.yaml
previous=$(kubectl --context "$context" -n "$namespace" get deployment portfolio \
  -o 'jsonpath={.metadata.annotations.deployment\.kubernetes\.io/revision}' 2>/dev/null || true)

recover() {
  cat "$port_log"
  kubectl --context "$context" -n "$namespace" get pods -o wide || true
  kubectl --context "$context" -n "$namespace" describe deployment portfolio || true
  if [[ -n "$previous" ]]; then
    echo "Restoring previous Kubernetes revision $previous"
    kubectl --context "$context" -n "$namespace" rollout undo deployment/portfolio --to-revision="$previous"
    kubectl --context "$context" -n "$namespace" rollout status deployment/portfolio --timeout=180s
  else
    echo "First deployment failed; no previous revision exists. Inspect the pod events."
  fi
  exit 1
}

python3 scripts/render.py --image "$image" --version "$version" > "$manifest"
kubectl --context "$context" apply -f "$manifest"
kubectl --context "$context" -n "$namespace" rollout status deployment/portfolio --timeout=180s || recover
kubectl --context "$context" -n "$namespace" port-forward service/portfolio 18080:80 > "$port_log" 2>&1 &
port_pid=$!
python3 scripts/smoke_test.py http://127.0.0.1:18080 --expected-version "$version" || recover
kill -0 "$port_pid" 2>/dev/null || recover
echo "Local Kubernetes deployment verified."
