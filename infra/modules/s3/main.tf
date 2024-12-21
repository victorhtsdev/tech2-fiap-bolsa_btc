data "aws_caller_identity" "current" {}

resource "aws_s3_bucket" "bucket" {
  bucket = var.bucket_name

  tags = {
    Name        = var.bucket_name
    Environment = "Development"
  }
}

resource "aws_s3_bucket_policy" "bucket_policy" {
  bucket = aws_s3_bucket.bucket.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        # Negar acesso sem transporte seguro
        Effect = "Deny",
        Principal = "*",
        Action    = "s3:*",
        Resource  = [
          "${aws_s3_bucket.bucket.arn}",
          "${aws_s3_bucket.bucket.arn}/*"
        ],
        Condition = {
          Bool: {
            "aws:SecureTransport": "false"
          }
        }
      },
      {
        # Permitir acesso ao grupo Admins
        Effect = "Allow",
        Principal = {
          AWS = [
            "arn:aws:iam::${data.aws_caller_identity.current.account_id}:group/Admins"
          ]
        },
        Action = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
        Resource = [
          "${aws_s3_bucket.bucket.arn}",
          "${aws_s3_bucket.bucket.arn}/*"
        ]
      },
      {
        # Permitir acesso à role techRole
        Effect = "Allow",
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/techRole"
        },
        Action = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
        Resource = [
          "${aws_s3_bucket.bucket.arn}",
          "${aws_s3_bucket.bucket.arn}/*"
        ]
      }
    ]
  })
}
