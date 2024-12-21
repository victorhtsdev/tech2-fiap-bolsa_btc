resource "aws_iam_user" "user" {
  name = var.user_name
}

resource "aws_iam_group" "group" {
  name = var.group_name
}

resource "aws_iam_policy" "admin_policy" {
  name        = "AdminPolicy"
  description = "Política administrativa equivalente ao root"

  policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = "*",
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_group_policy_attachment" "attach_admin_policy" {
  group      = aws_iam_group.group.name
  policy_arn = aws_iam_policy.admin_policy.arn
}

resource "aws_iam_group_membership" "membership" {
  name = "GroupMembership"
  group = aws_iam_group.group.name
  users = [aws_iam_user.user.name]
}

resource "aws_iam_access_key" "access_key" {
  user = aws_iam_user.user.name
}
