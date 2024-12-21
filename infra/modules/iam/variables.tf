variable "user_name" {
  description = "Nome do usuário IAM"
  type        = string
}

variable "group_name" {
  description = "Nome do grupo IAM"
  type        = string
}

variable "role_name" {
  description = "Nome da Role IAM"
  type        = string
}

variable "role_policy_name" {
  description = "Nome da política da Role IAM"
  type        = string
}

variable "bucket_name" {
  description = "Nome do bucket S3"
  type        = string
}
