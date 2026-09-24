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
    AWS_REGION: str
    S3_BUCKET_NAME: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore" 
    )


settings = Settings()