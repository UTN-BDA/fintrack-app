from typing import List
from app import db
from app.models import User

class UserRepository:
    """
    Repository for User entity, applying SRP and Repository Pattern (Martin Fowler).
    """

    def save(self, user: User) -> User:
        db.session.add(user)
        db.session.commit()
        return user

    def update(self, user: User, id: int) -> User:
        entity = self.find(id)
        if entity is None:
            return None

        entity.username = user.username
        entity.email = user.email

        if user.password_hash is not None:
            entity.password_hash = user.password_hash

        db.session.add(entity)
        db.session.commit()
        return entity

    def delete(self, user: User) -> None:
        db.session.delete(user)
        db.session.commit()

    def all(self) -> List[User]:
        return db.session.query(User).all()

    def find(self, id: int) -> User:
        if id is None or id == 0:
            return None
        try:
            return db.session.query(User).filter(User.id == id).one()
        except:
            return None

    def find_by_username(self, username: str) -> User:
        return db.session.query(User).filter(User.username == username).one_or_none()

    def find_by_email(self, email: str) -> User:
        return db.session.query(User).filter(User.email == email).one_or_none()