from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1.endpoints import auth, products
from app.database import Base, engine
import app.models

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Las tablas y el esquema son gestionados profesionalmente con Alembic
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
