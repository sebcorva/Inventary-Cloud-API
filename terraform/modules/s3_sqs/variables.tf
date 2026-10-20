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

variable "bucket_name" {
  description = "Nombre opcional personalizado para el bucket de S3"
  type        = string
  default     = ""
}

variable "sqs_visibility_timeout_seconds" {
  description = "Tiempo en segundos que un mensaje queda invisible mientras un consumidor lo procesa"
  type        = number
  default     = 60
}

variable "sqs_max_receive_count" {
  description = "Cantidad máxima de reintentos antes de enviar un mensaje fallido a la Dead Letter Queue"
  type        = number
  default     = 3
}
