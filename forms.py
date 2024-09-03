from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, FieldList, Form, FormField, URLField, SubmitField
from wtforms.validators import InputRequired, Length

class RegisterForm(FlaskForm):
    username = StringField('Username:', validators=[InputRequired(), Length(max=30)])
    password = PasswordField('Password:', validators=[InputRequired()])
    email = EmailField('Email:', validators=[InputRequired(), Length(max=50)])
    first_name= StringField('First Name:', validators=[InputRequired(), Length(max=20)])
    last_name= StringField('Last Name:', validators=[InputRequired(), Length(max=20)])

class LoginForm(FlaskForm):
    username = StringField('Username:', validators=[InputRequired(), Length(max=30)])
    password = PasswordField('Password:', validators=[InputRequired()])

class IngredientForm(Form):
    ingredient_name = StringField('Ingredient:', validators=[InputRequired()])
    measurement = StringField('Measurement:', validators=[InputRequired()])
    
class RecipeForm(FlaskForm):
    title = StringField('Title:', validators=[InputRequired()])
    image = URLField('Image URL:')
    instructions = StringField('Instructions:', validators=[InputRequired()])
    ingredients = FieldList(FormField(IngredientForm), min_entries=1, max_entries=5)

class SearchForm(FlaskForm):
    searched = StringField('Search Term', validators=[InputRequired()])
    submit = SubmitField('Submit')