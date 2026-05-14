from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.database import get_db
from app.core.security import create_access_token, get_current_user
from app.models.domain import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.auth import TokenDTO, UsuarioCreateDTO, UsuarioResponseDTO
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["Autenticacion"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(UsuarioRepository(db))


@router.post("/token", response_model=TokenDTO)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    user = service.authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenDTO(access_token=access_token)


@router.post("/register", response_model=UsuarioResponseDTO, status_code=status.HTTP_201_CREATED)
def register_user(
    usuario: UsuarioCreateDTO,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return service.crear_usuario(usuario)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/me", response_model=UsuarioResponseDTO)
def read_current_user(current_user: Usuario = Depends(get_current_user)):
    return current_user
