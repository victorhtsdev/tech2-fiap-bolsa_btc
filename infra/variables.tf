variable "region" {
  default = "us-east-1"
}

variable "bucket_name" {
  description = "Nome do bucket S3"
  type        = string
}

variable "prefix" {
  description = "Prefixo para criar as pastas no bucket"
  type        = string
}

variable "user_name" {
  description = "Nome do usuário IAM"
  type        = string
}

variable "group_name" {
  description = "Nome do grupo IAM"
  type        = string
}
