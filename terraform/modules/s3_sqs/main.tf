# Obtener datos de la cuenta de AWS para nombres únicos globales
data "aws_caller_identity" "current" {}

# ==============================================================================
# 1. Bucket de Amazon S3 (Almacenamiento Multimedia)
# ==============================================================================
resource "aws_s3_bucket" "assets" {
  bucket = var.bucket_name != "" ? var.bucket_name : "${var.project_name}-${var.environment}-assets-${data.aws_caller_identity.current.account_id}"

  # Evita borrado accidental en producción
  force_destroy = var.environment == "dev" ? true : false

  tags = {
    Name        = "${var.project_name}-${var.environment}-assets"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

# Versionado de objetos (Recuperación ante borrados accidentales)
resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.assets.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Cifrado en reposo del lado del servidor (SSE-S3 con algoritmo AES-256)
resource "aws_s3_bucket_server_side_encryption_configuration" "encryption" {
  bucket = aws_s3_bucket.assets.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Configuración CORS para permitir peticiones web seguras
resource "aws_s3_bucket_cors_configuration" "cors" {
  bucket = aws_s3_bucket.assets.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST", "HEAD"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

# ==============================================================================
# 2. Dead Letter Queue (DLQ) para Amazon SQS
# ==============================================================================
resource "aws_sqs_queue" "dlq" {
  name                      = "${var.project_name}-${var.environment}-events-dlq"
  message_retention_seconds = 1209600 # 14 días de retención 
  sqs_managed_sse_enabled   = true

  tags = {
    Name        = "${var.project_name}-${var.environment}-events-dlq"
    Environment = var.environment
    Project     = var.project_name
    Type        = "DeadLetterQueue"
    ManagedBy   = "Terraform"
  }
}

# ==============================================================================
# 3. Cola Principal de Eventos SQS
# ==============================================================================
resource "aws_sqs_queue" "main" {
  name                       = "${var.project_name}-${var.environment}-events-queue"
  visibility_timeout_seconds = var.sqs_visibility_timeout_seconds
  message_retention_seconds  = 345600 # 4 días de retención
  sqs_managed_sse_enabled    = true

  # Política de reintento: Si falla X veces, trasladar automáticamente a la DLQ
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = var.sqs_max_receive_count
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-events-queue"
    Environment = var.environment
    Project     = var.project_name
    Type        = "EventQueue"
    ManagedBy   = "Terraform"
  }
}
