output "alb_dns_name" {
  description = "Nombre DNS público del Application Load Balancer para acceder a la API desde Internet"
  value       = aws_lb.main.dns_name
}

output "alb_arn" {
  description = "ARN del Application Load Balancer"
  value       = aws_lb.main.arn
}

output "ecs_cluster_name" {
  description = "Nombre del clúster ECS"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "Nombre del servicio ECS"
  value       = aws_ecs_service.api.name
}

output "ecs_security_group_id" {
  description = "ID del Security Group de las tareas ECS (para autorizar el acceso en el Security Group de RDS)"
  value       = aws_security_group.ecs_tasks.id
}
