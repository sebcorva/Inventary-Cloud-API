from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Proyecto
    PROJECT_NAME: str = "Inventory Cloud API"
    ENVIRONMENT: str = "development"
    
    # Base de Datos
    DATABASE_URL: str
    
    # Seguridad JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # AWS
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = ""
    SQS_QUEUE_URL: str = ""
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore" 
    )


settings = Settings()