from flask import Flask, render_template, redirect, session, flash, request, url_for
# from flask_debugtoolbar import DebugToolbarExtension
from forms import LoginForm, RegisterForm, RecipeForm, SearchForm
from models import db, connect_db, User, Recipe, Ingredient, RecipeIngredient
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] =  
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] =  True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# toolbar = DebugToolbarExtension(app)

connect_db(app)
with app.app_context():
    db.create_all()

@app.context_processor
def base():
    form = SearchForm()
    return dict(form = form)

@app.route('/')
def homepage():
    drinks = Recipe.random_drinks()
    if 'username' not in session:
        return render_template('home.html', drinks = drinks)
    else:
        username = session['username']
        user = User.query.filter_by(username = username).first_or_404()
        return render_template('home.html', drinks = drinks, user = user)

@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data 
        password = form.password.data 
        email = form.email.data
        first_name = form.first_name.data 
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)
        session['username'] = new_user.username
        db.session.add(new_user)
        db.session.commit()
        return redirect(f'/users/{username}')

    return render_template('register.html', form = form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password =form.password.data
        
        user = User.authenticate(username, password)
        if user:
            flash(f'Greetings {user.username}!')
            session['username'] = user.username
            return redirect(f'/users/{username}')
        else:
            form.username.errors = ['Invalid Username/Password.']

    
    return render_template('login.html', form = form)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/users/<username>')
def show_user(username):
    user = User.query.filter_by(username = username).first_or_404()
    recipes = Recipe.query.filter_by(author = username).all()
    if 'username' not in session:
        flash('You must be logged in to access!')
        return redirect('/login') 
    else:
        return render_template('profile.html', user = user, recipes = recipes)

@app.route('/users/<username>/delete', methods = ['POST'])
def delete_user(username):
    if 'username' not in session:
        flash('You must be logged in to access!')
        return redirect('/login')
    user = User.query.get(username)
    recipes = Recipe.query.filter_by(author = username).all()
    if user.username == session['username']:
        for recipe in recipes:
            db.session.delete(recipe)
            db.session.commit()
        db.session.delete(user)
        db.session.commit()
        session.clear()
        return redirect('/')
    
@app.route('/users/<username>/recipe/add', methods = ['GET', 'POST'])
def create_recipe(username):
    if 'username' not in session:
        flash('You must be logged in to access!')
        return redirect('/login')
    user = User.query.get(username)
    form = RecipeForm()
    if form.validate_on_submit():
        new_recipe = Recipe(title = form.title.data,
                            instructions = form.instructions.data,
                            author = session['username'],
                            image = form.image.data or None)
        db.session.add(new_recipe)
        db.session.commit()
        ingredients = []
        measurements = []
        for field in form.ingredients:
            ingredients.append(field.ingredient_name.data)
            measurements.append(field.measurement.data)
            
        zipped_ingredients = list(zip(ingredients, measurements))
        for ingredient, measurement in zipped_ingredients:
            new_ingredient = Ingredient(ingredient_name = ingredient, measurement = measurement)
            db.session.add(new_ingredient)
            db.session.commit()
            new_recipe_ingredient = RecipeIngredient(recipe_id = new_recipe.id, ingredient_id = new_ingredient.id)
            db.session.add(new_recipe_ingredient)
            db.session.commit()

        return redirect(f'/users/{username}')
    
    return render_template('add_recipe.html', user = user, form = form)

@app.route('/recipes/<recipe_id>/update')
def show_edit_form(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    username = session['username']
    user = User.query.filter_by(username = username).first_or_404()
    if recipe.author != session['username']:
        flash('Must be logged in as author to edit!')
        return redirect(f'/users/{username}')
    else:
        return render_template('edit_recipe.html', recipe = recipe, user = user)

@app.route('/recipes/<recipe_id>/update', methods = ['POST'])
def edit_recipe(recipe_id):
    username = session['username']
    recipe = Recipe.query.get_or_404(recipe_id)
    recipe.title = request.form['title']
    recipe.instructions = request.form['instructions']
    db.session.add(recipe)
    db.session.commit()
    ingredient_list = []
    measurement_list = []
    for arg in request.form:
        if arg == 'ingredient_name':
            ingredient_list = request.form.getlist(arg)
        if arg == 'measurement':
            measurement_list = request.form.getlist(arg)

    zipped_ingredients = list(zip(ingredient_list, measurement_list))
    i = 0
    while i < len(recipe.ingredients):
        for ingredient in recipe.ingredients:
            ingredient.ingredient_name = zipped_ingredients[i][0]
            ingredient.measurement = zipped_ingredients[i][1]
            print(ingredient)
            db.session.add(ingredient)
            db.session.commit()
            i += 1

    return redirect(f'/users/{username}')

@app.route('/recipes/<recipe_id>/delete', methods = ['POST'])
def delete_recipe(recipe_id):
    username = session['username']
    recipe = Recipe.query.get_or_404(recipe_id)
    db.session.delete(recipe)
    db.session.commit()

    return redirect(f'/users/{username}')

@app.route('/search', methods = ['GET', 'POST'])
def search():
    form = SearchForm()
    if form.searched.data == '':
        return redirect('/')
    searched = form.searched.data or request.args.get('searched')
    page = request.args.get('page', 1, type=int)
    recipes = Recipe.query.filter(Recipe.title.like('%' + searched + '%'))
    recipes = recipes.order_by(Recipe.title).paginate(page = page, per_page = 4, error_out = False)
    if 'username' not in session:
        return render_template('search.html', form = form, searched = searched, recipes = recipes)
    else:
        username = session['username']
        user = User.query.filter_by(username = username).first()
        return render_template('search.html', form = form, searched = searched, user = user, recipes = recipes)
        

@app.route('/recipes/<drink_title>')
def get_drink(drink_title):
    recipes = Recipe.query.filter_by(title = drink_title).all()
    if 'username' not in session:
        return render_template('drink.html', recipes = recipes)
    else:
        username = session['username']
        user = User.query.filter_by(username = username).first()
        return render_template('drink.html', recipes = recipes, user = user)
