output "bucket_arn" {
  description = "ARN do bucket S3"
  value       = module.s3.bucket_arn
}

output "access_key_id" {
  description = "Access Key ID"
  value       = module.iam.access_key_id
  sensitive   = true
}

output "secret_access_key" {
  description = "Secret Access"
  value       = module.iam.secret_access_key
  sensitive   = true
}
