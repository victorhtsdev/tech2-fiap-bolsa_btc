variable "user_name" {
  description = "Nome do usuário IAM"
  type        = string
  default     = "tech-admin"
}

variable "group_name" {
  description = "Nome do grupo IAM"
  type        = string
  default     = "Admins"
}

variable "role_name" {
  description = "Nome da Role IAM"
  type        = string
  default     = "techRole"
}

variable "role_policy_name" {
  description = "Nome da política da Role IAM"
  type        = string
  default     = "TechRoleS3AccessPolicy"
}

variable "bucket_name" {
  description = "Nome do bucket S3"
  type        = string
  default     = "vhts-fiap-tech-challenge2"
}
