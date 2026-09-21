resource "aws_ecr_repository" "app" {
  name                 = var.project_name
  image_tag_mutability = "IMMUTABLE"
  force_delete         = true # Final bootstrap cleanup deletes this lab's images.
  image_scanning_configuration { scan_on_push = false }
}

# Tagged images are kept so that lifecycle rules cannot silently break rollback.
# Prune them with scripts/prune_releases.py after completing the guide.
resource "aws_ecr_lifecycle_policy" "app" {
  repository = aws_ecr_repository.app.name
  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Expire untagged images after one day"
      selection    = { tagStatus = "untagged", countType = "sinceImagePushed", countUnit = "days", countNumber = 1 }
      action       = { type = "expire" }
    }]
  })
}

output "ecr_repository_url" { value = aws_ecr_repository.app.repository_url }
