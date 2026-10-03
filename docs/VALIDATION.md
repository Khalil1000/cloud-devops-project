# Validation record

Updated 3 October 2026. This record distinguishes current CI verification from earlier AWS demonstrations. The original authoring checks were recorded on 7 September 2026; the later runs below supersede the original outstanding Docker, Terraform-provider, Kubernetes and AWS demonstration checks.

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

The [incident note](INCIDENT_TEMPLATE.md) records the Kubernetes diagnosis, timestamps, recovery and limitations of the timing evidence.

## Current operating scope

The repository variable `AWS_DEPLOY_ENABLED` is currently `false`. Main and PR checks still verify the application, infrastructure configuration, image and local Kubernetes deployment. Earlier AWS evidence demonstrates that the delivery path worked at the recorded time; run #66 did not deploy the newly fixed image or revalidate the current AWS account.

To make a deliberate new release, confirm the existing infrastructure and repository variables, set `AWS_DEPLOY_ENABLED=true` under **Settings > Secrets and variables > Actions > Variables**, and run **Portfolio pipeline** on `main`. Confirm both AWS steps and the candidate/live smoke checks pass, then record that run as new release evidence. Setting the switch back to `false` prevents later workflow releases but does not delete resources or stop all AWS charges; use the build guide's cleanup procedure for teardown.

CloudWatch alarm and email notification setup remain optional and were not configured. Runtime logs and metrics were demonstrated; email delivery was not. The Terraform action's Node.js 20 warning was resolved by merged PR #1. Main run #80 passed without check annotations; its AWS authentication and deployment steps were skipped.

On 3 October 2026, the live AWS deployment role's trust policy was verified to use StringEquals for the exact ID-based GitHub subject of this repository's main branch. Both wildcard subject patterns were removed. An AWS-enabled pipeline run remains outstanding to verify deployment with the restricted policy.
