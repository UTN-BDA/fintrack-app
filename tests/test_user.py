import unittest, os
from datetime import date
from app import create_app, db
from app.models.user import User
from werkzeug.security import check_password_hash

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        # Configuración del entorno de testing
        os.environ['FLASK_CONTEXT'] = 'testing'
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Datos de prueba
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123'
        }

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_creation(self):
        """Test creación de usuario"""
        user = User(username=self.user_data['username'], email=self.user_data['email'])
        user.set_password(self.user_data['password'])
        db.session.add(user)
        db.session.commit()
        
        fetched_user = User.query.get(user.id)
        self.assertEqual(fetched_user.username, self.user_data['username'])
        self.assertEqual(fetched_user.email, self.user_data['email'])
        self.assertTrue(check_password_hash(fetched_user.password_hash, self.user_data['password']))

    def test_user_update(self):
        """Test actualización de usuario"""
        user = User(username=self.user_data['username'], email=self.user_data['email'])
        user.set_password(self.user_data['password'])
        db.session.add(user)
        db.session.commit()
        
        # Actualizar datos
        new_email = 'new@example.com'
        user.email = new_email
        db.session.commit()
        
        updated_user = User.query.get(user.id)
        self.assertEqual(updated_user.email, new_email)

    def test_user_deletion(self):
        """Test eliminación de usuario"""
        user = User(username=self.user_data['username'], email=self.user_data['email'])
        user.set_password(self.user_data['password'])
        db.session.add(user)
        db.session.commit()
        
        user_id = user.id
        db.session.delete(user)
        db.session.commit()
        
        deleted_user = User.query.get(user_id)
        self.assertIsNone(deleted_user)

    def test_password_hashing(self):
        """Test que verifica el hashing de contraseña"""
        user = User(username=self.user_data['username'], email=self.user_data['email'])
        user.set_password(self.user_data['password'])
        
        self.assertNotEqual(user.password_hash, self.user_data['password'])
        self.assertTrue(user.password_hash.startswith('scrypt:'))
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertFalse(user.check_password('WrongPassword'))

    def test_unique_constraints(self):
        """Test que verifica las restricciones de unicidad"""
        user1 = User(username=self.user_data['username'], email=self.user_data['email'])
        user1.set_password(self.user_data['password'])
        db.session.add(user1)
        db.session.commit()
        
        # Intentar crear usuario con mismo username
        user2 = User(username=self.user_data['username'], email='other@example.com')
        user2.set_password('OtherPassword123')
        db.session.add(user2)
        with self.assertRaises(Exception):
            db.session.commit()
        
        db.session.rollback()
        
        # Intentar crear usuario con mismo email
        user3 = User(username='otheruser', email=self.user_data['email'])
        user3.set_password('OtherPassword123')
        db.session.add(user3)
        with self.assertRaises(Exception):
            db.session.commit()

if __name__ == '__main__':
    unittest.main()
    