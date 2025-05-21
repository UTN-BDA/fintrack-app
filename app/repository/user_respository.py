from typing import List, Optional
from app.extensions import db
from app.models import User

class UserRepository:

    def save(self, user: User) -> User:
        """Inserta un nuevo usuario"""
        db.session.add(user)
        db.session.commit()
        return user
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Devuelve un usuario por su ID"""
        return User.query.get(user_id)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Devuelve un usuario por su ID"""
        return User.query.filter_by(username=username).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Busca un usuario por su email"""
        return User.query.filter_by(email=email).first()
    
    def get_all(self, page: int = 1, per_page: int = 20) -> List[User]:
        """Lista usuarios paginados"""
        pag = User.query.paginate(page=page, per_page=per_page, error_out=False)
        return pag.items

    def update(self, user: User, **kwargs) -> User:
        """Actualiza campos de un usuario dado (sin hacer save explícito)"""
        for attr, val in kwargs.items():
            setattr(user, attr, val)
        db.session.commit()
        return user

    def delete(self, user: User) -> None:
        """Elimina físicamente el usuario"""
        db.session.delete(user)
        db.session.commit()
