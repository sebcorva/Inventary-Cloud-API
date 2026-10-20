# ==============================================================================
# 1. DB Subnet Group (Asignación exclusiva a subredes privadas)
# ==============================================================================
resource "aws_db_subnet_group" "rds" {
  name        = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids  = var.private_subnet_ids
  description = "Grupo de subredes privadas para PostgreSQL RDS"

  tags = {
    Name        = "${var.project_name}-${var.environment}-db-subnet-group"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

# ==============================================================================
# 2. Security Group para RDS (Cortafuegos estricto)
# ==============================================================================
resource "aws_security_group" "rds" {
  name        = "${var.project_name}-${var.environment}-rds-sg"
  description = "Permitir trafico entrante a PostgreSQL SOLO desde el contenedor ECS de la API"
  vpc_id      = var.vpc_id

  # Regla Ingress: Solo puerto 5432 proveniente del Security Group de ECS
  ingress {
    description     = "Acceso seguro a PostgreSQL desde la API ECS"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.ecs_security_group_id]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-rds-sg"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

# ==============================================================================
# 3. Instancia Administrada Amazon RDS (PostgreSQL 16)
# ==============================================================================
resource "aws_db_instance" "postgres" {
  identifier     = "${var.project_name}-${var.environment}-postgres"
  engine         = "postgres"
  engine_version = "16.3"
  instance_class = var.instance_class

  allocated_storage     = var.allocated_storage
  max_allocated_storage = 50 # Auto-escalado de almacenamiento bajo demanda
  storage_type          = "gp3"

  db_name  = var.database_name
  username = var.database_username
  password = var.database_password
  port     = 5432

  db_subnet_group_name   = aws_db_subnet_group.rds.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false # Seguridad absoluta: cero acceso desde Internet

  # Opciones para entorno de desarrollo / portafolio
  skip_final_snapshot     = var.environment == "dev" ? true : false
  backup_retention_period = var.environment == "dev" ? 1 : 7
  deletion_protection     = false

  tags = {
    Name        = "${var.project_name}-${var.environment}-postgres"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}
