output "rds_endpoint" {
  description = "Punto de enlace completo de conexión a RDS (host:port)"
  value       = aws_db_instance.postgres.endpoint
}

output "rds_address" {
  description = "Hostname de la base de datos PostgreSQL para armar DATABASE_URL"
  value       = aws_db_instance.postgres.address
}

output "rds_port" {
  description = "Puerto de conexión a PostgreSQL"
  value       = aws_db_instance.postgres.port
}

output "rds_security_group_id" {
  description = "ID del Security Group de la base de datos"
  value       = aws_security_group.rds.id
}

output "database_name" {
  description = "Nombre de la base de datos creada"
  value       = aws_db_instance.postgres.db_name
}
