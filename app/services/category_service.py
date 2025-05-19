from typing import List, Optional
from app.models.category import Category
from app.repository.category_repository import CategoryRepository

class CategoryService:
    def __init__(self, repo: CategoryRepository = None):
        self.repo = repo or CategoryRepository()

    def create_category(self, name: str, is_favorite: bool = False, is_recurring: bool = False) -> Category:
        """Crea y persiste una nueva categoría."""
        category = Category(
            name=name,
            is_favorite=is_favorite,
            is_recurring=is_recurring
        )
        return self.repo.save(category)

    def get_category(self, category_id: int) -> Optional[Category]:
        """Obtiene una categoría por su ID"""
        return self.repo.get_by_id(category_id)
    
    def get_category_name(self, category_name: int) -> Optional[Category]:
        """Obtiene una categoría por su nombre"""
        return self.repo.get_by_name(category_name)

    def list_categories(self, favorites_only: bool = False, recurring_only: bool = False) -> List[Category]:
        """Lista categorías, con opción de filtrar por favoritas o recurrentes"""
        if favorites_only:
            return self.repo.get_favorites()
        if recurring_only:
            return self.repo.get_recurring()
        return self.repo.get_all()

    def update_category(self, category_id: int, **updates) -> Optional[Category]:
        """
        Cambia el nombre, si es favorito o si es recurrente de una categoría.
        Ejemplo: update_category(1, name="Transporte", is_favorite=True)
        """
        # Solo permite actualizar estas tres cosas
        allowed = {"name", "is_favorite", "is_recurring"}
        # Se queda solo con los cambios válidos
        data = {key: value for key, value in updates.items() if key in allowed}
        # Si no hay nada que actualizar, devuelve None
        if not data:
            return None
        # Aplica los cambios y devuelve la categoría actualizada
        return self.repo.update(category_id, **data)

    def delete_category(self, category_id: int, soft: bool = True) -> bool:
        """
        Elimina la categoría. Por defecto soft‑delete:
        marca deleted=True si existe ese campo.
        Si soft=False, hace un borrado físico.
        """
        if soft and hasattr(Category, 'deleted'):
            # asume que el modelo tiene un campo deleted
            return self.repo.update(category_id, deleted=True) is not None
        return self.repo.delete(category_id)
