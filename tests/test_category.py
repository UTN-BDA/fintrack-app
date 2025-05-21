import unittest, os
from app import create_app, db
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user import User
from datetime import date

class CategoryModelTestCase(unittest.TestCase):
    def setUp(self):
        # Configuración del entorno de testing
        os.environ['FLASK_CONTEXT'] = 'testing'
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Crear usuario de prueba para relaciones
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('TestPassword123')
        db.session.add(self.user)
        db.session.commit()
        
        # Datos de prueba
        self.category_data = {
            'name': 'Groceries',
            'is_favorite': True,
            'is_recurring': False
        }

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_category_creation(self):
        """Test creación de categoría"""
        category = Category(**self.category_data)
        db.session.add(category)
        db.session.commit()
        
        fetched_category = Category.query.get(category.id)
        self.assertEqual(fetched_category.name, self.category_data['name'])
        self.assertEqual(fetched_category.is_favorite, self.category_data['is_favorite'])
        self.assertEqual(fetched_category.is_recurring, self.category_data['is_recurring'])

    def test_category_update(self):
        """Test actualización de categoría"""
        category = Category(**self.category_data)
        db.session.add(category)
        db.session.commit()
        
        # Actualizar datos
        new_name = 'Utilities'
        new_favorite = False
        category.name = new_name
        category.is_favorite = new_favorite
        db.session.commit()
        
        updated_category = Category.query.get(category.id)
        self.assertEqual(updated_category.name, new_name)
        self.assertEqual(updated_category.is_favorite, new_favorite)

    def test_category_deletion(self):
        """Test eliminación de categoría"""
        category = Category(**self.category_data)
        db.session.add(category)
        db.session.commit()
        
        category_id = category.id
        db.session.delete(category)
        db.session.commit()
        
        deleted_category = Category.query.get(category_id)
        self.assertIsNone(deleted_category)

    def test_category_transaction_relationship(self):
        """Test relación con transacciones"""
        category = Category(**self.category_data)
        db.session.add(category)
        db.session.commit()
        
        # Crear transacción asociada
        transaction = Transaction(
            amount=100.50,
            date=date.today(),
            description='Supermarket',
            method='Credit Card',
            is_income=False,
            user_id=self.user.id,
            category_id=category.id
        )
        db.session.add(transaction)
        db.session.commit()
        
        # Verificar relación
        self.assertEqual(category.transactions.count(), 1)
        self.assertEqual(category.transactions.first().id, transaction.id)
        
        # Eliminar categoría debería establecer category_id a NULL en transacción (dependiendo de ondelete)
        db.session.delete(category)
        db.session.commit()
        
        updated_transaction = Transaction.query.get(transaction.id)
        self.assertIsNone(updated_transaction.category_id)

if __name__ == '__main__':
    unittest.main()
    