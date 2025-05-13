from typing import List
from app import db
from app.models import Category

class CategoryRepository:
    """
    Repository for Category entity (Single Responsibility Principle).
    """

    def save(self, category: Category) -> Category:
        db.session.add(category)
        db.session.commit()
        return category

    def update(self, category: Category, id: int) -> Category:
        entity = self.find(id)
        if entity is None:
            return None

        entity.name = category.name
        entity.is_favorite = category.is_favorite
        entity.is_recurring = category.is_recurring

        db.session.add(entity)
        db.session.commit()
        return entity

    def delete(self, category: Category) -> None:
        db.session.delete(category)
        db.session.commit()

    def all(self) -> List[Category]:
        return db.session.query(Category).all()

    def find(self, id: int) -> Category:
        if id is None or id == 0:
            return None
        try:
            return db.session.query(Category).filter(Category.id == id).one()
        except:
            return None

    def find_by_name(self, name: str) -> Category:
        return db.session.query(Category).filter(Category.name == name).one_or_none()

    def find_favorites(self) -> List[Category]:
        return db.session.query(Category).filter(Category.is_favorite == True).all()
