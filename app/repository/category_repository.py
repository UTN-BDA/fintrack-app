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

    def update(self, category_id: int, **kwargs) -> Category | None:
        """Actualiza campos de la categoría indicada."""
        category = self.get_by_id(category_id)
        if not category:
            return None
        for attr, value in kwargs.items():
            setattr(category, attr, value)
        db.session.commit()
        return category

    def get_all(self) -> list[Category]:
        """Devuelve todas las categorías."""
        return Category.query.all()

    def get_by_id(self, category_id: int) -> Category | None:
        """Devuelve la categoría por su ID."""
        return Category.query.get(category_id)

    def get_by_name(self, name: str) -> Category:
        """Devuelve la categoría por su name."""
        return Category.query.filter_by(name=name).all()
    
    def get_favorites(self) -> list[Category]:
        """Devuelve sólo las categorías marcadas como favoritas."""
        return Category.query.filter_by(is_favorite=True).all()

    def get_recurring(self) -> list[Category]:
        """Devuelve sólo las categorías recurrentes."""
        return Category.query.filter_by(is_recurring=True).all()
    
    def delete(self, category_id: int) -> bool:
        """Elimina (hard‑delete) la categoría indicada."""
        category = self.get_by_id(category_id)
        if not category:
            return False
        db.session.delete(category)
        db.session.commit()
        return True
