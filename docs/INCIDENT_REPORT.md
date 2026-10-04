# Incident report — Kubernetes readiness failure and rollback

**Exercise:** controlled readiness failure with diagnosis and rollback

**Date and environment:** 2026-10-01, local `kind` cluster (`kind-portfolio`, namespace `portfolio`)

## What happened

A configuration change (`FORCE_NOT_READY=true`) was applied to the `portfolio` Deployment on purpose. The new candidate pod could never pass its readiness probe and never received traffic. The two existing pods, still running the previous revision, kept serving requests throughout, so the application itself stayed available even though the rollout failed.

## Detection

`kubectl rollout status deployment/portfolio --timeout=150s` reported:
```
error: deployment "portfolio" exceeded its progress deadline
```
This was confirmed by a Kubernetes event on the new pod (`portfolio-b7df47557-5w9nr`):
```
Readiness probe failed: HTTP probe failed with statuscode: 503
```

## Timeline

| Time | Observation or action |
| --- | --- |
| 2026-10-01T00:06:13Z | Recorded the current good revision (`1`) before changing anything |
| 2026-10-01T00:06:14Z | Introduced the controlled fault: `kubectl set env deployment/portfolio FORCE_NOT_READY=true` |
| 2026-10-01T00:08:15Z | `rollout status` returned `error: deployment "portfolio" exceeded its progress deadline` |
| (between the deadline failure and the rollback below) | Diagnosed the cause: `get pods` showed the two old pods still `1/1 Running` and one new pod stuck at `0/1`; `describe deployment` showed `Progressing False / ProgressDeadlineExceeded`; `get events` showed `Readiness probe failed: HTTP probe failed with statuscode: 503` on the new pod |
| 2026-10-01T00:32:56Z | Ran `kubectl rollout undo deployment/portfolio --to-revision=1`; `rollout status` returned `successfully rolled out` in the same second |
| (immediately after) | Verified recovery: `get pods` showed 2/2 `Running` with no trace of the failed pod; `python3 scripts/smoke_test.py` returned `PASS: healthy application, release local` |

The diagnosis completion time was not recorded, so no precise diagnosis-duration metric is available. The rollback was issued about 24 minutes after the rollout deadline failure, following inspection of the deployment and pod events.

## Cause and recovery

**Cause:** setting `FORCE_NOT_READY=true` made the application's `/readyz` endpoint return `503` for any pod built from that revision. The Deployment's rolling update strategy is `maxUnavailable: 0, maxSurge: 1`, so Kubernetes created exactly one new candidate pod rather than replacing the existing ones, and refused to promote it because it never passed its readiness probe. This is also why the running application was never actually interrupted — the two pods on the previous revision were never touched.

**Recovery:** `kubectl rollout undo deployment/portfolio --to-revision=1` pointed the Deployment back at the ReplicaSet (`portfolio-564596b456`) that was already running and already healthy, so there was no new pod to schedule or wait on. The command and successful rollout response share the same recorded second.

**Verification:**

1. `kubectl rollout status` → `successfully rolled out`
2. `kubectl get pods` → 2/2 `Running`, failed candidate pod gone entirely
3. `python3 scripts/smoke_test.py http://127.0.0.1:8080 --expected-version local` → `PASS: healthy application, release local`, confirming the application responded with the expected release

**Image/revision:** image `portfolio:local`; rolled back from revision `2` (the bad config) to revision `1` (the recorded `$GOOD_REVISION`).

## Follow-up considerations

This exercise used a manual rollback. The existing `scripts/deploy_local.sh` provides rollout and HTTP checks with rollback to a previous revision on failure; the exercise commands were run directly to capture each diagnostic step. A future change could add an automated test of that recovery path, including delayed readiness, to verify that rollback triggers only after the configured failure conditions.

## Evidence

See [`docs/evidence/README.md`](evidence/README.md), Part 3 (Kubernetes recovery), for the full screenshot sequence: the fault being introduced, the failing readiness probe, the old pods remaining ready throughout, the rollback command, and the passing smoke test after recovery.
