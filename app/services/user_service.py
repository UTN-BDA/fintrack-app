from typing import Optional, List
from app.models.user import User
from app.repository.user_respository import UserRepository

class UserService:
    def __init__(self, repo: UserRepository = None):
        self.repo = repo or UserRepository()

    def create_user(self, username: str, email: str, password: str) -> User:
        """Registra un nuevo usuario, hasheando su contraseña"""
        user = User(username=username, email=email)
        user.set_password(password)
        return self.repo.save(user)

    def authenticate(self, login: str, password: str) -> Optional[User]:
        """Verifica credenciales: intenta por username, si no busca email. Devuelve el User si coincide, o None"""
        user = self.repo.get_by_username(login) or self.repo.get_by_email(login)
        if user and user.check_password(password):
            return user
        return None

    def get_user(self, user_id: int) -> Optional[User]:
        """Obtiene un usuario por su ID"""
        return self.repo.get_by_id(user_id)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Obtiene un usuario por su nombre de usuario"""
        return self.repo.get_by_username(username)

    def list_users(self, page: int = 1, per_page: int = 20) -> List[User]:
        """Lista usuarios paginados"""
        return self.repo.get_all(page=page, per_page=per_page)

    def update_user(self, user_id: int, **updates) -> Optional[User]:
        """Actualiza username, email o password. Para password usa set_password."""
        user = self.get_user(user_id)
        if not user:
            return None

        allowed = {"username", "email", "password"}
        data = {k: v for k, v in updates.items() if k in allowed}
        if not data:
            return user

        if "password" in data:
            user.set_password(data.pop("password"))
        return self.repo.update(user, **data)

    def delete_user(self, user_id: int) -> bool:
        """Elimina (hard‑delete) un usuario por su ID."""
        user = self.get_user(user_id)
        if not user:
            return False
        self.repo.delete(user)
        return True
