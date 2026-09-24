from fastapi import FastAPI
from app.config import settings

app = FastAPI(
    title = settings.PROJECT_NAME,
    version = "1.0.0",
    docs_url = "/docs",
    redoc_url = "/redoc",
)

@app.get("/health", tags=["System"])
def health_check():
    #Endpoint para monitorear el estado del ALB en AWS
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "service": settings.PROJECT_NAME,
    }
