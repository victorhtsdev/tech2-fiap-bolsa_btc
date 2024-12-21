variable "bucket_name" {
  description = "Nome do bucket S3"
  type        = string
  default     = "vhts-fiap-tech-challenge2"
}

variable "prefix" {
  description = "Prefixo da estrutura dentro do bucket"
  type        = string
  default     = "bolsa_bovespa/raw"
}


variable "role_policy_name" {
  description = "Nome da política da Role IAM"
  type        = string
  default     = "TechRoleS3AccessPolicy"
}
