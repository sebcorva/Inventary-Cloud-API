output "s3_bucket_name" {
  description = "Nombre del bucket S3 creado"
  value       = aws_s3_bucket.assets.id
}

output "s3_bucket_arn" {
  description = "ARN del bucket S3 para políticas IAM"
  value       = aws_s3_bucket.assets.arn
}

output "sqs_queue_url" {
  description = "URL de la cola principal de SQS para publicar eventos"
  value       = aws_sqs_queue.main.url
}

output "sqs_queue_arn" {
  description = "ARN de la cola principal de SQS para políticas IAM"
  value       = aws_sqs_queue.main.arn
}

output "sqs_dlq_url" {
  description = "URL de la Dead Letter Queue (DLQ)"
  value       = aws_sqs_queue.dlq.url
}

output "sqs_dlq_arn" {
  description = "ARN de la Dead Letter Queue (DLQ)"
  value       = aws_sqs_queue.dlq.arn
}
