variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
  default     = "inventory-cloud"
}

variable "environment" {
  description = "Ambiente de despliegue"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "Región de AWS"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "Rango CIDR para la VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "database_name" {
  description = "Nombre de la base de datos PostgreSQL"
  type        = string
  default     = "inventory_db"
}

variable "database_username" {
  description = "Usuario administrador de PostgreSQL"
  type        = string
  default     = "postgresadmin"
}

variable "database_password" {
  description = "Contraseña de la base de datos PostgreSQL en RDS"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "Clave secreta para firmar tokens JWT"
  type        = string
  sensitive   = true
}

variable "container_image" {
  description = "URI de la imagen Docker en Amazon ECR"
  type        = string
  default     = "public.ecr.aws/docker/library/python:3.12-slim"
}
