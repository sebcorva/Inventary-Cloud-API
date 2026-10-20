terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# ==============================================================================
# 1. Módulo de Redes (VPC, Subredes Multi-AZ e Internet Gateway)
# ==============================================================================
module "vpc" {
  source       = "../../modules/vpc"
  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = var.vpc_cidr
}

# ==============================================================================
# 2. Módulo de Almacenamiento y Mensajería (S3, SQS y Dead Letter Queue)
# ==============================================================================
module "s3_sqs" {
  source       = "../../modules/s3_sqs"
  project_name = var.project_name
  environment  = var.environment
}

# ==============================================================================
# 3. Módulo de Cómputo (ECS Fargate, Application Load Balancer y Roles IAM)
# ==============================================================================
module "ecs" {
  source             = "../../modules/ecs"
  project_name       = var.project_name
  environment        = var.environment
  aws_region         = var.aws_region
  vpc_id             = module.vpc.vpc_id
  public_subnet_ids  = module.vpc.public_subnet_ids
  private_subnet_ids = module.vpc.private_subnet_ids

  container_image = var.container_image
  container_port  = 8000

  # Conexión dinámica a PostgreSQL en RDS
  database_url = "postgresql+psycopg://${var.database_username}:${var.database_password}@${module.rds.rds_endpoint}/${var.database_name}"
  secret_key   = var.secret_key

  # Permisos IAM y variables de S3 y SQS
  s3_bucket_name = module.s3_sqs.s3_bucket_name
  s3_bucket_arn  = module.s3_sqs.s3_bucket_arn
  sqs_queue_url  = module.s3_sqs.sqs_queue_url
  sqs_queue_arn  = module.s3_sqs.sqs_queue_arn
}

# ==============================================================================
# 4. Módulo de Base de Datos Relacional (PostgreSQL 16 en Amazon RDS)
# ==============================================================================
module "rds" {
  source                = "../../modules/rds"
  project_name          = var.project_name
  environment           = var.environment
  vpc_id                = module.vpc.vpc_id
  private_subnet_ids    = module.vpc.private_subnet_ids
  ecs_security_group_id = module.ecs.ecs_security_group_id

  database_name     = var.database_name
  database_username = var.database_username
  database_password = var.database_password
}
