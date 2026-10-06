# ==========================================
# Stage 1: Build & Dependencies
# ==========================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Instalar dependencias del sistema necesarias para compilar paquetes si aplica
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Instalar dependencias de Python en un directorio aislado
RUN pip install --no-cache-dir --user -r requirements.txt

# ==========================================
# Stage 2: Runtime Image
# ==========================================
FROM python:3.12-slim AS runner

WORKDIR /app

# Instalar solo la librería de runtime para Postgres
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear un usuario no privilegiado para ejecutar la app
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -s /bin/bash -m appuser

# Copiar paquetes instalados desde la etapa de compilación
COPY --from=builder /root/.local /home/appuser/.local

# Copiar el código fuente del proyecto y configuraciones
COPY --chown=appuser:appgroup ./app ./app
COPY --chown=appuser:appgroup ./alembic ./alembic
COPY --chown=appuser:appgroup ./alembic.ini .

# Ajustar variables de entorno para el usuario no-root
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER appuser

EXPOSE 8000

# Endpoint de healthcheck integrado para Docker / ECS
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]