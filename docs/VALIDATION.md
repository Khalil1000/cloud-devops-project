# Validation record

Updated 4 October 2026. This record separates full AWS release verification from historical CI-only runs and recovery exercises.

## Latest AWS release verification - run #88

[Run #88](https://github.com/Khalil1000/cloud-devops-project/actions/runs/37166774042) passed on `main` for commit `cae347a70fa94f2000ab0165aae80d917aad0b6a`. Application tests, Terraform validation, the Docker build, Trivy scan, and Kubernetes rollout checks all passed. Both AWS authentication and publication/promotion steps ran successfully.

This verifies delivery after the exact repository-and-main OIDC trust restriction was applied. The release script verifies the candidate before moving `live` and checks the alias afterward. See [evidence Part 6](evidence/README.md#part-6-aws-release-verified-after-the-trust-policy-restriction).

## Scan-fix verification — run #66

[Run #66](https://github.com/Khalil1000/cloud-devops-project/actions/runs/37083931737), for merge commit `4728e7b5b69a6cd7721a7912ac3c1c04c4f31e70`, passed after [PR #13](https://github.com/Khalil1000/cloud-devops-project/pull/13) merged.

| Check | Result |
|---|---|
| Application and release checks | Passed: unit tests cover application behavior, readiness/liveness, structured error logs, scan policy and Lambda response validation |
| Terraform | Formatting, initialization without the backend, and provider-schema validation passed for both stacks |
| Container build | Passed with Python installation tools removed after dependency installation and checking |
| Trivy security gate | Passed: no findings met the fixable HIGH/CRITICAL blocking policy |
| Kubernetes | The built image passed rollout and HTTP smoke verification on an ephemeral `kind` cluster |
| AWS authentication and release | Intentionally skipped; `AWS_DEPLOY_ENABLED=false` |

The local rebuilt image also reported `0 fixable HIGH/CRITICAL vulnerabilities`. See [evidence Part 5](evidence/README.md#part-5-the-vulnerability-gate-blocks-delivery-then-passes-after-remediation) for the failed scan, remediation and successful runs. Scanner results are time-specific and do not establish that an image has no vulnerabilities of any severity.

## Completed deployment and recovery demonstrations

The [evidence record](evidence/README.md) contains screenshots and observations for:

- A merged change automatically deploying through GitHub OIDC and ECR to Lambda, with the `live` alias and release identifier verified (Part 1).
- An intentionally failing test blocking the pipeline, followed by restoration to green (Part 2).
- Kubernetes pod replacement and a failed readiness rollout recovered with rollback and an HTTP smoke test (Part 3).
- A deliberate Lambda execution error appearing in metrics and structured CloudWatch logs, plus alias rollback and restoration (Part 4).

The [incident report](INCIDENT_REPORT.md) records the Kubernetes diagnosis, timestamps, recovery and limitations of the timing evidence.

## Current operating scope

`AWS_DEPLOY_ENABLED` was enabled for run #88. Main and PR checks verify the application, infrastructure configuration, image and Kubernetes deployment; AWS release steps additionally require delivery to be enabled on main. Run #66 was CI-only, while run #88 verified the corrected image through AWS release promotion.

To make a deliberate new release, confirm the existing infrastructure and repository variables, set `AWS_DEPLOY_ENABLED=true` under **Settings > Secrets and variables > Actions > Variables**, and run **Portfolio pipeline** on `main`. Confirm both AWS steps and the candidate/live smoke checks pass, then record that run as new release evidence. Setting the switch back to `false` prevents later workflow releases but does not delete resources or stop all AWS charges; use the build guide's cleanup procedure for teardown.

CloudWatch alarm and email notification setup remain optional and were not configured. Runtime logs and metrics were demonstrated; email delivery was not. The Terraform action's Node.js 20 warning was resolved by merged PR #1. Main run #80 passed without check annotations; its AWS authentication and deployment steps were skipped.

On 3 October 2026, the live AWS deployment role's trust policy was verified to use StringEquals for the exact ID-based GitHub subject of this repository's main branch. Both wildcard subject patterns were removed. Run #88 on 4 October 2026 subsequently passed AWS authentication and deployment with that restriction.
