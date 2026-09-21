variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "project_name" {
  type    = string
  default = "devops-portfolio"
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,22}$", var.project_name))
    error_message = "Use 3-23 lowercase letters, numbers or hyphens, starting with a letter."
  }
}

variable "bootstrap_image_tag" {
  type        = string
  default     = "bootstrap"
  description = "Push this initial image into ECR before apply."
}

variable "github_repository" {
  type        = string
  description = "Exact case-sensitive OWNER/REPOSITORY."
  validation {
    condition     = can(regex("^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", var.github_repository))
    error_message = "Use OWNER/REPOSITORY without https:// or .git."
  }
}

variable "existing_github_oidc_provider_arn" {
  type        = string
  default     = ""
  description = "Reuse an existing token.actions.githubusercontent.com provider if present."
}

variable "enable_email_alerts" {
  type        = bool
  default     = false
  description = "Optional CloudWatch alarm and SNS email subscription; check pricing first."
}

variable "alert_email" {
  type    = string
  default = ""
  validation {
    condition     = !var.enable_email_alerts || can(regex("^[^@ ]+@[^@ ]+\\.[^@ ]+$", var.alert_email))
    error_message = "When enable_email_alerts is true, supply an email address you control."
  }
}
