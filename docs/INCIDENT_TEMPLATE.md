# Incident note — replace every placeholder with your observations

**Exercise:** failed deployment, triggered intentionally to practice diagnosis and rollback

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

I didn't capture an exact timestamp for when I finished reading the diagnosis output, so I'm not claiming a precise mean-time-to-diagnose figure — only the two timestamps I actually recorded (fault introduced, deadline exceeded) and the fact that the rollback itself was issued about 24 minutes later, after I'd worked through the `describe`/`events`/`logs` output.

## Cause and recovery

**Cause:** setting `FORCE_NOT_READY=true` made the application's `/readyz` endpoint return `503` for any pod built from that revision. The Deployment's rolling update strategy is `maxUnavailable: 0, maxSurge: 1`, so Kubernetes created exactly one new candidate pod rather than replacing the existing ones, and refused to promote it because it never passed its readiness probe. This is also why the running application was never actually interrupted — the two pods on the previous revision were never touched.

**Recovery:** `kubectl rollout undo deployment/portfolio --to-revision=1` pointed the Deployment back at the ReplicaSet (`portfolio-564596b456`) that was already running and already healthy, so there was no new pod to schedule or wait on. That's why the undo command and `successfully rolled out` landed in the same second.

**Verification:** three independent checks, not just one:
1. `kubectl rollout status` → `successfully rolled out`
2. `kubectl get pods` → 2/2 `Running`, failed candidate pod gone entirely
3. `python3 scripts/smoke_test.py http://127.0.0.1:8080 --expected-version local` → `PASS: healthy application, release local`, confirming the live application responded correctly, not just that the Deployment object looked healthy

**Image/revision:** image `portfolio:local`; rolled back from revision `2` (the bad config) to revision `1` (the recorded `$GOOD_REVISION`).

## What I would improve

Right now, recovering from a failed rollout depends on a person noticing the stuck deployment and running `rollout undo` manually. A tool like Argo Rollouts or Flagger could watch the same readiness signal and roll back automatically the moment the progress deadline is exceeded, removing the human-reaction-time step entirely. The tradeoff is real: it adds another controller to install, configure and keep up to date, and an automatic rollback could mask a change that was only slow to become ready rather than genuinely broken, so it would need a deliberately conservative deadline to avoid rolling back good deploys.

## Evidence

See [`docs/evidence/README.md`](evidence/README.md), Part 3 (Kubernetes recovery), for the full screenshot sequence: the fault being introduced, the failing readiness probe, the old pods remaining ready throughout, the rollback command, and the passing smoke test after recovery.
