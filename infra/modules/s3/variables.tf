variable "bucket_name" {
  description = "Nome do bucket S3"
  type        = string
}

variable "prefix" {
  description = "Prefixo da estrutura dentro do bucket"
  type        = string
}

variable "region" {
  description = "Região do bucket S3"
  type        = string
}
