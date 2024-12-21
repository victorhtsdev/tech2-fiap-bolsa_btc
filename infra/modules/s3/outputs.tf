output "bucket_arn" {
  description = "ARN do bucket S3"
  value       = aws_s3_bucket.bucket.arn
}

output "bucket_name" {
  description = "Nome do bucket S3"
  value       = aws_s3_bucket.bucket.id
}

output "bucket_prefix" {
  description = "Prefixo do bucket S3"
  value       = var.prefix
}

output "bucket_region" {
  description = "Região do bucket S3"
  value       = var.region
}
