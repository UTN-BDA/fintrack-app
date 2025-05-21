import unittest, os
from datetime import date, timedelta
from decimal import Decimal
from app import create_app, db
from app.models.transaction import Transaction
from app.models.user import User
from app.models.category import Category

class TransactionModelTestCase(unittest.TestCase):
    def setUp(self):
        # Configuración del entorno de testing
        os.environ['FLASK_CONTEXT'] = 'testing'
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Crear usuario y categoría de prueba para relaciones
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('TestPassword123')
        db.session.add(self.user)
        
        self.category = Category(name='Groceries', is_favorite=True)
        db.session.add(self.category)
        
        db.session.commit()
        
        # Datos de prueba
        self.transaction_data = {
            'amount': Decimal('100.50'),
            'date': date.today(),
            'description': 'Supermarket',
            'method': 'Credit Card',
            'is_income': False,
            'deleted': False,
            'user_id': self.user.id,
            'category_id': self.category.id
        }

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_transaction_creation(self):
        """Test creación de transacción"""
        transaction = Transaction(**self.transaction_data)
        db.session.add(transaction)
        db.session.commit()
        
        fetched_transaction = Transaction.query.get(transaction.id)
        self.assertEqual(fetched_transaction.amount, self.transaction_data['amount'])
        self.assertEqual(fetched_transaction.date, self.transaction_data['date'])
        self.assertEqual(fetched_transaction.description, self.transaction_data['description'])
        self.assertEqual(fetched_transaction.method, self.transaction_data['method'])
        self.assertEqual(fetched_transaction.is_income, self.transaction_data['is_income'])
        self.assertEqual(fetched_transaction.user_id, self.transaction_data['user_id'])
        self.assertEqual(fetched_transaction.category_id, self.transaction_data['category_id'])

    def test_transaction_update(self):
        """Test actualización de transacción"""
        transaction = Transaction(**self.transaction_data)
        db.session.add(transaction)
        db.session.commit()
        
        # Actualizar datos
        new_amount = Decimal('150.75')
        new_description = 'Whole Foods'
        new_is_income = True
        transaction.amount = new_amount
        transaction.description = new_description
        transaction.is_income = new_is_income
        db.session.commit()
        
        updated_transaction = Transaction.query.get(transaction.id)
        self.assertEqual(updated_transaction.amount, new_amount)
        self.assertEqual(updated_transaction.description, new_description)
        self.assertEqual(updated_transaction.is_income, new_is_income)

    def test_transaction_deletion(self):
        """Test eliminación de transacción"""
        transaction = Transaction(**self.transaction_data)
        db.session.add(transaction)
        db.session.commit()
        
        transaction_id = transaction.id
        db.session.delete(transaction)
        db.session.commit()
        
        deleted_transaction = Transaction.query.get(transaction_id)
        self.assertIsNone(deleted_transaction)

    def test_soft_delete(self):
        """Test eliminación lógica (campo deleted)"""
        transaction = Transaction(**self.transaction_data)
        db.session.add(transaction)
        db.session.commit()
        
        transaction.deleted = True
        db.session.commit()
        
        # Verificar que aún existe en la base de datos
        self.assertIsNotNone(Transaction.query.get(transaction.id))
        
        # Verificar que el campo deleted es True
        self.assertTrue(Transaction.query.get(transaction.id).deleted)

    def test_user_relationship(self):
        """Test relación con usuario"""
        transaction = Transaction(**self.transaction_data)
        db.session.add(transaction)
        db.session.commit()
        
        # Verificar relación
        self.assertEqual(transaction.user.id, self.user.id)
        self.assertEqual(self.user.transactions.count(), 1)
        self.assertEqual(self.user.transactions.first().id, transaction.id)

    def test_category_relationship(self):
        """Test relación con categoría"""
        transaction = Transaction(**self.transaction_data)
        db.session.add(transaction)
        db.session.commit()
        
        # Verificar relación
        self.assertEqual(transaction.category.id, self.category.id)
        self.assertEqual(self.category.transactions.count(), 1)
        self.assertEqual(self.category.transactions.first().id, transaction.id)
        
        # Transacción sin categoría
        transaction2 = Transaction(
            amount=Decimal('50.00'),
            date=date.today(),
            description='Misc',
            method='Cash',
            is_income=False,
            user_id=self.user.id,
            category_id=None
        )
        db.session.add(transaction2)
        db.session.commit()
        
        self.assertIsNone(transaction2.category_id)

    def test_date_constraints(self):
        """Test que verifica restricciones de fecha"""
        # Fecha en el futuro no debería ser permitida (dependiendo de tu lógica de negocio)
        future_date = date.today() + timedelta(days=365)
        transaction = Transaction(
            amount=Decimal('100.00'),
            date=future_date,
            description='Future Transaction',
            method='Credit Card',
            is_income=False,
            user_id=self.user.id,
            category_id=self.category.id
        )
        db.session.add(transaction)
        
        # Esto pasaría a menos que tengas validación explícita
        db.session.commit()
        
        # Podrías añadir validación en el modelo si necesitas restringir fechas futuras

if __name__ == '__main__':
    unittest.main()
    