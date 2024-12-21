output "tech_role_arn" {
  description = "ARN da Role techRole"
  value       = aws_iam_role.tech_role.arn
}

output "tech_admin_user" {
  description = "Nome do usuário tech-admin"
  value       = aws_iam_user.tech_admin_user.name
}
