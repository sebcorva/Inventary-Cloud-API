import logging
from contextlib import asynccontextmanager
import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Logging global 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
)
logger = logging.getLogger("app.main")

from app.config import settings
from app.api.v1.endpoints import auth, products
from app.database import Base, engine
import app.models

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Las tablas y el esquema son gestionados con Alembic
    yield
    # Shutdown: Limpieza de recursos si fuera necesario

app = FastAPI(
    title = settings.PROJECT_NAME,
    version = "1.0.0",
    docs_url = "/docs",
    redoc_url = "/redoc",
    lifespan = lifespan,
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_correlation_id_and_timing(request: Request, call_next):
    """
    Middleware de observabilidad:
    - Extrae o genera un Correlation ID (X-Request-ID) único por petición.
    - Mide la latencia de procesamiento.
    - Inyecta los headers en la respuesta y emite logs estructurados para CloudWatch.
    """
    correlation_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = time.perf_counter() - start_time
    response.headers["X-Request-ID"] = correlation_id
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"

    logger.info(
        f"[{correlation_id}] {request.method} {request.url.path} "
        f"- Status: {response.status_code} - Duration: {process_time * 1000:.2f}ms"
    )
    return response

#Conectar rutas de autenticacion (/auth/register, /auth/login)
app.include_router(auth.router)
app.include_router(products.router)

@app.get("/health", tags=["System"])
def health_check():
    #Endpoint para monitorear el estado del ALB en AWS
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "service": settings.PROJECT_NAME,
    }
