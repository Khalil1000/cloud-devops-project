output "aws_region" { value = var.aws_region }
output "function_name" { value = aws_lambda_function.app.function_name }
output "live_alias_arn" { value = aws_lambda_alias.live.arn }
output "ecr_repository_url" { value = data.aws_ecr_repository.app.repository_url }
output "github_role_arn" { value = aws_iam_role.github.arn }
output "application_log_group" { value = aws_cloudwatch_log_group.app.name }
output "alarm_name" { value = try(aws_cloudwatch_metric_alarm.errors[0].alarm_name, "disabled") }
output "function_console_url" {
  value = "https://${var.aws_region}.console.aws.amazon.com/lambda/home?region=${var.aws_region}#/functions/${var.project_name}?tab=monitoring"
}
