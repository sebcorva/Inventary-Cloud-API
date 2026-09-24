# Inventory Cloud API

RESTful API de alto rendimiento para la gestión de inventario, catálogo de productos y almacenamiento de multimedia en la nube, construida con estándares profesionales de backend y preparada para despliegue en AWS.

## Tech Stack

- **Lenguaje:** Python 3.12
- **Framework Web:** FastAPI (ASGI con Uvicorn)
- **Base de Datos & ORM:** PostgreSQL 16, SQLAlchemy 2.0, Psycopg v3
- **Validación de Datos:** Pydantic v2 & Pydantic Settings
- **Contenedores:** Docker & Docker Compose
- **Servicios Cloud (AWS):** S3 (Almacenamiento de imágenes), ECS/ALB (Producción)

## Arquitectura del Proyecto

El backend sigue un patrón de diseño en capas para garantizar separación de responsabilidades, testabilidad y mantenibilidad:

´´´text
inventory-cloud-api/
├── app/
│   ├── config.py       # Configuración central y validación de variables con Pydantic
│   ├── database.py     # Engine, SessionLocal y Base declarativa de SQLAlchemy
│   ├── models/         # Modelos ORM (Mapeo a tablas físicas de PostgreSQL)
│   ├── schemas/        # Esquemas de entrada/salida y validación con Pydantic
│   ├── services/       # Lógica de negocio pura e integración con SDKs (Boto3)
│   ├── routers/        # Controladores HTTP y endpoints REST
│   └── main.py         # Instancia FastAPI, middlewares (CORS) y lifespan
├── docker-compose.yml  # Orquestación de servicios locales (PostgreSQL)
├── requirements.txt    # Dependencias fijadas para entornos reproducibles
├── .env.example        # Plantilla pública de variables de entorno
└── README.md           # Documentación técnica del proyecto
