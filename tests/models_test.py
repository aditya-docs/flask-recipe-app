from unittest import TestCase
from app import app
from models import db, User

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///cocktails_test"
app.config['SQLALCHEMY_ECHO'] =  False
app.config['TESTING'] = True

# with app.app_context():
#     db.drop_all()
#     db.create_all()

class UserModelTestCase(TestCase):

    def setUp(self):
        with app.app_context():
            User.query.delete()

    def tearDown(self):
        with app.app_context():
            db.session.rollback()

    def test_get_by_username(self):
        user = User(username='TestUser', password='1234', first_name='Test', last_name='User', email='test@gmail.com')
        with app.app_context():
            db.session.add(user)
            db.session.commit()
            users = User.query.filter_by(username = user.username).all()

        self.assertEqual(users, [user])