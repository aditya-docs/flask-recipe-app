from unittest import TestCase

from app import app
from models import db, User, Recipe, Ingredient, RecipeIngredient

app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///cocktails_test"
app.config['WTF_CSRF_ENABLED'] = False

# with app.app_context():
#     db.drop_all()
#     db.create_all()

class GetRoutesTestCase(TestCase):

    def test_homepage(self):
        with app.test_client() as client:
            res = client.get('/')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h1>Welcome to the Homepage!!!</h1>', html)

    def test_register(self):
        with app.test_client() as client:
            res = client.get('/register')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h1>Create an Account</h1>', html)

    def test_login(self):
        with app.test_client() as client:
            res = client.get('/login')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h1>Login</h1>', html)
