variable "project_name" {
  description = "Nombre del proyecto para prefijo de recursos y tags"
  type        = string
  default     = "inventory-cloud"
}

variable "environment" {
  description = "Ambiente de despliegue (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "Rango de direcciones IP CIDR para la VPC completa"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Zonas de disponibilidad en AWS para garantizar alta disponibilidad (Multi-AZ)"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "public_subnet_cidrs" {
  description = "Rangos de IP para las subredes públicas (conectadas al Internet Gateway)"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "Rangos de IP para las subredes privadas (aisladas para ECS y RDS)"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.20.0/24"]
}
