from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import random
db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):
    """Model for creating a user"""
    __tablename__ = 'users'
    username = db.Column(db.String(30), primary_key = True, unique = True)
    password = db.Column(db.Text, nullable = False)
    email = db.Column(db.String(50), nullable = False, unique = True, )
    first_name = db.Column(db.String(20), nullable = False)
    last_name = db.Column(db.String(20), nullable = False)
    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        """Registers a user with a hashed password"""

        hashed  = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode('utf8')
        return cls(username = username, 
                    password = hashed_utf8,
                    email = email,
                    first_name = first_name,
                    last_name = last_name)
    
    @classmethod
    def authenticate(cls, username, password):
        """Validates login credentials"""

        user = User.query.filter_by(username = username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False
# make recipes visible to USERS AND SEE IF DELETING IT THROUGH THE WEB APP WORKS INSTEAD OF USING PSQL
class Recipe(db.Model):
    """Model for new and existing recipes"""
    __tablename__ = 'recipes'
    Default_Image = 'https://i.pinimg.com/736x/5c/3e/29/5c3e29112c52abd22a3d446e865d3320.jpg'      
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    title = db.Column(db.Text, nullable = False)
    author = db.Column(db.String(30), db.ForeignKey('users.username'), nullable = True)
    instructions = db.Column(db.Text, nullable = False)
    image = db.Column(db.Text, nullable = False, default = Default_Image )
    ingredients = db.relationship('Ingredient', secondary = 'recipe_ingredients', backref = 'recipes', cascade = 'all, delete')


    @classmethod
    def random_drinks(cls):
        """Query 8 random drinks from the db"""
        nums = []
        drinks = []
        for i in range(0, 8):
            num = random.randint(1, 426)
            nums.append(num)
        for num in nums:
             drinks.append(Recipe.query.get_or_404(num))
        return drinks
    
class Ingredient(db.Model):
    """Model for adding and storing ingredients"""
    __tablename__ = 'ingredients'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    ingredient_name = db.Column(db.Text, nullable = False)
    measurement = db.Column(db.Text, nullable = False)
    
    def __repr__(self):
        i = self
        return f'{i.id} name = {i.ingredient_name} measurement = {i.measurement}'


class RecipeIngredient(db.Model):
    """Model for the recipe-ingredient relationship"""
    __tablename__ = 'recipe_ingredients'
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id', ondelete='CASCADE'), primary_key = True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id', ondelete='CASCADE'), primary_key =True)
