#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
function_name=${1:?Usage: bash scripts/deploy_lambda.sh FUNCTION IMAGE_URI VERSION}
image_uri=${2:?Supply the ECR image URI}
app_version=${3:?Supply the release identifier}

read -r previous revision < <(aws lambda get-alias --function-name "$function_name" --name live --query '[FunctionVersion,RevisionId]' --output text)
echo "Previous live Lambda version: $previous"
aws lambda update-function-code --function-name "$function_name" --image-uri "$image_uri" > /dev/null
aws lambda wait function-updated-v2 --function-name "$function_name"
candidate=$(aws lambda publish-version --function-name "$function_name" --query Version --output text)
aws lambda wait function-active-v2 --function-name "$function_name" --qualifier "$candidate"

# Test the new immutable version before changing the live alias.
if ! python3 scripts/lambda_smoke.py --function-name "$function_name" \
    --qualifier "$candidate" --expected-version "$app_version"; then
  echo "Candidate $candidate failed. The live alias remains on version $previous."
  exit 1
fi

aws lambda update-alias --function-name "$function_name" --name live \
  --function-version "$candidate" --revision-id "$revision" > /dev/null
echo "Promoted Lambda version $candidate. Previous live version: $previous"
if ! python3 scripts/lambda_smoke.py --function-name "$function_name" \
    --qualifier live --expected-version "$app_version"; then
  echo "Live verification failed; restoring version $previous."
  read -r current_version current_revision < <(aws lambda get-alias --function-name "$function_name" --name live --query '[FunctionVersion,RevisionId]' --output text)
  if [[ "$current_version" == "$candidate" ]]; then
    aws lambda update-alias --function-name "$function_name" --name live --function-version "$previous" --revision-id "$current_revision" > /dev/null
  else
    echo "Another release changed live; leaving that version untouched."
  fi
  exit 1
fi
