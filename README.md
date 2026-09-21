# Cloud DevOps Portfolio — a low-cost AWS project

A small Python application, packaged once as a Docker image, tested on local
Kubernetes, and deployed to AWS Lambda through GitHub Actions.

**Start with [the step-by-step build guide](docs/BUILD_GUIDE.md).** It explains
what to run, why each step exists, what success looks like, and how to recover
when something goes wrong.

## What you will demonstrate

- Terraform creates AWS infrastructure and keeps its main state in encrypted,
  versioned S3 storage with locking.
- Kubernetes Deployments, Services, probes and rolling updates run on your laptop
  using kind. The CI pipeline also creates an ephemeral kind cluster.
- A failed test or fixable HIGH/CRITICAL image vulnerability blocks delivery.
- GitHub Actions authenticates to AWS with a scoped role and short-lived OIDC credentials.
- AWS runs the same container image on Lambda. A new version is checked before
  the `live` alias moves to it.
- CloudWatch provides application logs and built-in Lambda metrics. One email
  alarm is an optional exercise.
- The guide includes failure drills, an incident note template and full cleanup.

## Cost scope

There are **no EKS clusters, EC2 instances, NAT gateways, load balancers,
provisioned concurrency settings, public function URLs or scheduled jobs**.
Kubernetes runs locally. AWS still supplies real application execution through
Lambda, private images through ECR, S3 state storage, IAM and CloudWatch.

Local work needs no AWS resources. The AWS portion may be free within your
account's allowances, but ECR, S3 and logs can incur small usage charges. The
guide shows a $1 budget alert, a pricing example, short log retention, release
pruning and teardown. A budget alert is not a spending cap.

## Files to understand first

| Path | Purpose |
| --- | --- |
| `app/app.py` | Web app, release identifier, health checks and JSON logs |
| `Dockerfile` | One image that runs locally, in Kubernetes and in Lambda |
| `k8s/` | Local cluster and application manifests |
| `infra/bootstrap/` | S3 state bucket, budget alert and ECR repository |
| `infra/environment/` | Lambda, IAM, GitHub OIDC and optional error alarm |
| `.github/workflows/pipeline.yml` | Tests, security scan, Kubernetes verification and AWS release |
| `scripts/` | Installation, smoke tests, deployment and cleanup helpers |
| `events/` | Authenticated Lambda test request payloads |
| `docs/` | Build guide, incident template and validation record |

## Quick local start

After installing Python and downloading this project:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r app/requirements.txt
python -m unittest discover -s tests -v
python app/app.py
```

Open <http://127.0.0.1:8080>. Continue in the build guide for Docker, Kubernetes,
AWS and the CI/CD workflow. This quick start does not create AWS resources.

## Honest project description

This is a learning and portfolio system with local Kubernetes and an AWS
serverless deployment. It is not a production EKS platform or a highly available
multi-region service. Explain these choices in interviews: they preserve the
delivery and troubleshooting lessons while controlling cost.

Before making claims about your results, run the guide and replace the
placeholders in your evidence and incident notes with your actual observations.
