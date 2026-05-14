from app.core.security import hash_password, verify_password
from app.models.domain import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.auth import UsuarioCreateDTO


class AuthService:
    def __init__(self, repository: UsuarioRepository):
        self.repository = repository

    def authenticate_user(self, username: str, password: str) -> Usuario | None:
        user = self.repository.obtener_por_username(username)
        if user is None:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def crear_usuario(self, usuario_dto: UsuarioCreateDTO) -> Usuario:
        existing_user = self.repository.obtener_por_username(usuario_dto.username)
        if existing_user is not None:
            raise ValueError("El nombre de usuario ya existe")

        usuario = Usuario(
            username=usuario_dto.username,
            hashed_password=hash_password(usuario_dto.password),
            nombre_completo=usuario_dto.nombre_completo,
            is_active=True,
        )
        return self.repository.crear(usuario)
