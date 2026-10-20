output "api_endpoint_url" {
  description = "URL publica del Application Load Balancer para acceder a la API"
  value       = "http://${module.ecs.alb_dns_name}"
}

output "api_docs_url" {
  description = "URL directa a la documentacion Swagger UI en produccion"
  value       = "http://${module.ecs.alb_dns_name}/docs"
}

output "s3_bucket_name" {
  description = "Nombre del bucket S3 para multimedia"
  value       = module.s3_sqs.s3_bucket_name
}

output "sqs_queue_url" {
  description = "URL de la cola SQS de eventos"
  value       = module.s3_sqs.sqs_queue_url
}

output "sqs_dlq_url" {
  description = "URL de la Dead Letter Queue (DLQ)"
  value       = module.s3_sqs.sqs_dlq_url
}

output "rds_endpoint" {
  description = "Endpoint privado de conexion a PostgreSQL RDS"
  value       = module.rds.rds_endpoint
}

output "vpc_id" {
  description = "ID de la VPC creada"
  value       = module.vpc.vpc_id
}
