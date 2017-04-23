#!/usr/bin/env python
import requests
import argparse

from bs4 import BeautifulSoup

from database.session import Session
from database.model import Recipe, Asset, RecipeIngredient, Ingredient
from database.util import init as database_init
from database.util import reset as database_reset


class Downloader(object):
    def download(self):
        print('Updating recipe cache...')
        req = requests.get('https://www.hellofresh.com/archive/recipes/',
                           params={'count': '100000'})
        print(req.content)


# Main
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-rd', '--resetdb', action='store_true')
    args = parser.parse_args()

    if args.resetdb:
        database_reset()
    else:
        database_init()

    downloader = Downloader()
    # downloader.download()
    session = Session()

    ingredient = Ingredient()
    ingredient.name = 'Flour'
    ingredient.contains = 'nuts'
    ingredient.description = 'Flour used mostly in baking and comes from wheat'
    session.add(ingredient)

    ingredient = Ingredient()
    ingredient.name = 'Salt'
    ingredient.description = 'Comes from the ocean'
    session.add(ingredient)

    recipe = Recipe()
    recipe.uid = 'test'
    recipe.country = 'US'
    recipe.description = 'test description'
    recipe.name = 'test name'

    pdf = Asset()
    pdf.path = './downloads/pdfs'
    pdf.filename = 'recipe.pdf'
    pdf.size = 12345
    pdf.size_unit = 'kb'

    recipe.assets.append(pdf)

    recipe_ingredient = RecipeIngredient()
    recipe_ingredient.amount = 2
    recipe_ingredient.unit = 'tsp'
    recipe_ingredient.ingredient = session.query(
        Ingredient).filter(Ingredient.name == 'Salt').one()
    recipe_ingredient.recipe = recipe
    session.add(recipe_ingredient)

    recipe_ingredient = RecipeIngredient()
    recipe_ingredient.amount = 4
    recipe_ingredient.unit = 'Cups'
    recipe_ingredient.ingredient = session.query(
        Ingredient).filter(Ingredient.name == 'Flour').one()
    recipe_ingredient.recipe = recipe
    session.add(recipe_ingredient)

    session.add(recipe)
    session.commit()

    recipe = session.query(Recipe).filter(Recipe.name == 'test name').one()
    for recipe_ingredient in recipe.ingredients:
        ingredient = recipe_ingredient.ingredient
        print(recipe_ingredient.amount + ' ' +
              recipe_ingredient.unit + ' ' + ingredient.name)


if __name__ == '__main__':
    main()
