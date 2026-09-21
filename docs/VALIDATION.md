# Validation record

Prepared on 7 September 2026. These are authoring checks, not evidence that
resources were deployed into your AWS account.

## Completed

- 13 Python unit tests passed, covering application behavior, readiness/liveness,
  structured error logs, image-scan policy and Lambda response validation.
- The app ran under Gunicorn locally and passed its HTTP smoke test.
- The running-app smoke test rejected an incorrect release identifier.
- Python source files parsed successfully.
- All Terraform files parsed as HCL; `terraform fmt -check -recursive infra` passed.
- Bash scripts passed `bash -n` syntax checks.
- Kubernetes and GitHub workflow YAML parsed successfully.
- The application manifest renderer produced the expected ServiceAccount,
  Deployment and Service with the requested image and release identifier.
- Lambda invocation event files parsed as JSON.
- Terraform declarations were checked for duplicate names, unresolved resource
  references and the absence of EKS, EC2, NAT gateways, load balancers,
  provisioned concurrency, API Gateway and public function URL resources.

## Checks to complete on your computer

- Full Terraform provider-schema validation: the provider download could not
  complete in the authoring environment. Run `terraform init` and
  `terraform validate` in both stacks as described in the guide.
- Docker image build, actual Trivy vulnerability results and Kubernetes rollout:
  a Docker engine was not available in the authoring environment.
- AWS resource creation, IAM/OIDC behavior, Lambda container execution, email
  confirmation and the live GitHub workflow require your accounts and were not
  executed here.

The workflow includes the same verification stages as gates. Current scanner
results and provider versions can change, so inspect real failures and update
the relevant component instead of bypassing a gate. Add your own completed
deployment evidence only after running the guide.
