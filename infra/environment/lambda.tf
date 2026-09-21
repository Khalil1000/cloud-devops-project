data "aws_ecr_repository" "app" { name = var.project_name }

resource "aws_cloudwatch_log_group" "app" {
  name              = "/aws/lambda/${var.project_name}"
  retention_in_days = 1
}

resource "aws_iam_role" "lambda" {
  name = "${var.project_name}-lambda"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Principal = { Service = "lambda.amazonaws.com" }, Action = "sts:AssumeRole" }]
  })
}

resource "aws_iam_role_policy" "lambda_logs" {
  name = "write-own-logs"
  role = aws_iam_role.lambda.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["logs:CreateLogStream", "logs:PutLogEvents"]
      Resource = "${aws_cloudwatch_log_group.app.arn}:*"
    }]
  })
}

resource "aws_ecr_repository_policy" "lambda" {
  repository = data.aws_ecr_repository.app.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "LambdaPullOwnFunctionImage"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"]
      Condition = {
        ArnLike = { "aws:SourceArn" = ["arn:aws:lambda:${var.aws_region}:${data.aws_caller_identity.current.account_id}:function:${var.project_name}", "arn:aws:lambda:${var.aws_region}:${data.aws_caller_identity.current.account_id}:function:${var.project_name}:*"] }
      }
    }]
  })
}

resource "aws_lambda_function" "app" {
  function_name = var.project_name
  role          = aws_iam_role.lambda.arn
  package_type  = "Image"
  image_uri     = "${data.aws_ecr_repository.app.repository_url}:${var.bootstrap_image_tag}"
  architectures = ["x86_64"]
  memory_size   = 256
  timeout       = 10
  publish       = true
  # No function URL, API Gateway, provisioned concurrency, VPC or scheduled trigger.
  environment {
    variables = {
      AWS_LWA_PORT                 = "8080"
      AWS_LWA_READINESS_CHECK_PATH = "/healthz"
      AWS_LWA_ERROR_STATUS_CODES   = "500-599"
      ENABLE_DEMO_ERRORS           = "true"
    }
  }
  lifecycle { ignore_changes = [image_uri] }
  depends_on = [aws_iam_role_policy.lambda_logs, aws_ecr_repository_policy.lambda]
}

resource "aws_lambda_alias" "live" {
  name             = "live"
  function_name    = aws_lambda_function.app.function_name
  function_version = aws_lambda_function.app.version
  description      = "Only promote a version after the smoke tests pass."
  lifecycle { ignore_changes = [function_version] }
}
