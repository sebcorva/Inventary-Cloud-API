from datatime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

# Base compartida
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)

# Payload para registro de nuevo usuario
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

# Respuesta enviada al client
class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    # Permite que Pydantic lea los campos del modelo SQL directamente
    model_config = ConfigDict(from_attributes=True)
    