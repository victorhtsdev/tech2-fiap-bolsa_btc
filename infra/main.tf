module "s3" {
  source      = "./modules/s3"
  bucket_name = "vhts-fiap-tech-challenge2"
  prefix      = "bolsa_bovespa/raw"
  region      = "us-east-1"
}

module "iam" {
  source           = "./modules/iam"
  user_name        = "tech-admin"
  group_name       = "Admins"
  role_name        = "techRole"
  role_policy_name = "TechRoleS3AccessPolicy"
  bucket_name      = "vhts-fiap-tech-challenge2"
}