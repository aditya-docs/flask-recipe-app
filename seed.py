from models import User, Recipe, Ingredient, RecipeIngredient, db
from app import app
import requests
app.app_context().push()

db.drop_all()
db.create_all()
chars = 'abcdefghijklmnopqrstvwyz'
API_Reqs = []
for char in chars:
    API_Reqs.append(f'https://www.thecocktaildb.com/api/json/v1/1/search.php?f={char}')

def seedData(url):
    data = requests.get(url)
    json = data.json()['drinks']
    for drink in json:
        title = drink['strDrink']
        instructions = drink['strInstructions']
        if drink['strDrinkThumb']:
            image = drink['strDrinkThumb']
        new_recipe = Recipe(title = title, instructions = instructions, image = image)
        db.session.add(new_recipe)
        db.session.commit()
        nums = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        ingredients = []
        measurements = []

        for num in nums:
            if drink[f'strIngredient{num}']:
                ingredients.append(drink[f'strIngredient{num}'])
            if drink[f'strMeasure{num}']:
                measurements.append(drink[f'strMeasure{num}'])

        zipped_ingredients = list(zip(ingredients, measurements))

        for ingredient, measurement in zipped_ingredients:
            new_ingredient = Ingredient(ingredient_name = ingredient, measurement = measurement)
            db.session.add(new_ingredient)
            db.session.commit()
            new_recipe_ingredient = RecipeIngredient(recipe_id = new_recipe.id, ingredient_id = new_ingredient.id)
            db.session.add(new_recipe_ingredient)
            db.session.commit()

# Create a Default user for all imported cocktails
# API_User = User(username = 'Admin', password = '1234qwer', email = 'none@gmail.com', first_name = 'Site', last_name = 'Admin')
# db.session.add(API_User)
# db.session.commit()

for url in API_Reqs:
    seedData(url)

# seedData('https://www.thecocktaildb.com/api/json/v1/1/search.php?f=a')

# Optimization: Implement only 1 of each ingredient by separating it from measurement insted of storing multiple of the same
# uniq_ingredients = set()
# for ingredient in uniq_ingredients:
#     new_ingredient = Ingredient(name = ingredient)
#     db.session.add(new_ingredient)
#     db.session.commit()

 