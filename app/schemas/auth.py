from pydantic import BaseModel, Field


class UsuarioCreateDTO(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    nombre_completo: str | None = None


class UsuarioResponseDTO(BaseModel):
    id: int
    username: str
    nombre_completo: str | None = None
    is_active: bool

    class Config:
        from_attributes = True


class TokenDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"
