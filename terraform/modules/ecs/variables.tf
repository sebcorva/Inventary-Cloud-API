variable "project_name" {
  description = "Nombre del proyecto para prefijo de recursos"
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

variable "vpc_id" {
  description = "ID de la VPC"
  type        = string
}

variable "public_subnet_ids" {
  description = "Subredes públicas para desplegar el Application Load Balancer (ALB)"
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "Subredes privadas para desplegar las tareas de ECS Fargate"
  type        = list(string)
}

variable "container_image" {
  description = "URI de la imagen Docker en Amazon ECR (ej: 123456.dkr.ecr.us-east-1.amazonaws.com/api:latest)"
  type        = string
  default     = "public.ecr.aws/docker/library/python:3.12-slim"
}

variable "container_port" {
  description = "Puerto en el que escucha la API FastAPI dentro del contenedor"
  type        = number
  default     = 8000
}

variable "database_url" {
  description = "URL completa de conexión a PostgreSQL construida desde el módulo RDS"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "Clave secreta para firmar tokens JWT"
  type        = string
  sensitive   = true
}

variable "s3_bucket_name" {
  description = "Nombre del bucket S3 para assets"
  type        = string
}

variable "s3_bucket_arn" {
  description = "ARN del bucket S3 para política IAM"
  type        = string
}

variable "sqs_queue_url" {
  description = "URL de la cola SQS para publicar eventos"
  type        = string
}

variable "sqs_queue_arn" {
  description = "ARN de la cola SQS para política IAM"
  type        = string
}
