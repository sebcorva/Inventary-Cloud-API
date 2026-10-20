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

variable "vpc_id" {
  description = "ID de la VPC donde se creará el Security Group de la base de datos"
  type        = string
}

variable "private_subnet_ids" {
  description = "Lista de subredes privadas donde residirá la base de datos"
  type        = list(string)
}

variable "ecs_security_group_id" {
  description = "ID del Security Group de la API ECS para autorizar conexiones entrantes a Postgres"
  type        = string
}

variable "database_name" {
  description = "Nombre de la base de datos inicial"
  type        = string
  default     = "inventory_db"
}

variable "database_username" {
  description = "Usuario administrador de PostgreSQL"
  type        = string
  default     = "postgresadmin"
}

variable "database_password" {
  description = "Contraseña maestra de PostgreSQL (marcada como sensible para no mostrarse en logs)"
  type        = string
  sensitive   = true
}

variable "allocated_storage" {
  description = "Almacenamiento en GB asignado a la base de datos"
  type        = number
  default     = 20
}

variable "instance_class" {
  description = "Tipo de instancia RDS (db.t4g.micro es elegible para la capa gratuita de AWS)"
  type        = string
  default     = "db.t4g.micro"
}
