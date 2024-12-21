provider "aws" {
  region = "us-east-1"
}

# Cria��o do recurso S3
module "s3" {
  source = "./modules/s3"

  bucket_name = "vhts-fiap-tech-challenge2"
  prefix      = "bolsa_bovespa/raw"
  region      = "us-east-1"
}

# M�dulo IAM para criar o usu�rio
module "iam" {
  source = "./modules/iam"

  user_name = "vhts"
  group_name = "devRole"
}
