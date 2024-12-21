data "aws_caller_identity" "current" {}

resource "aws_iam_user" "tech_admin_user" {
  name = var.user_name
}

resource "aws_iam_group_membership" "admins_membership" {
  name  = "admins-membership"
  group = var.group_name
  users = [aws_iam_user.tech_admin_user.name]
}

resource "aws_iam_role" "tech_role" {
  name = var.role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}


resource "aws_iam_policy" "tech_role_policy" {
  name        = var.role_policy_name
  description = "Permite acesso genérico ao S3 (será atualizado após criação do bucket)"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = ["s3:ListBucket", "s3:GetObject", "s3:PutObject"],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_s3_policy" {
  role       = aws_iam_role.tech_role.name
  policy_arn = aws_iam_policy.tech_role_policy.arn
}
