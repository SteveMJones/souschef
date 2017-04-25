import requests
import json

from sqlalchemy import exists

from bs4 import BeautifulSoup

from database.session import Session
from database.model import Recipe
from database.util import get_or_create

HELLOFRESH_RECIPE_API = 'https://www.hellofresh.com/archive/recipes/'
HELLOFRESH_RECIPE_BATCH_COUNT = 10000


class HelloFresh(object):

    def saveRecipeData(self, recipeData):

        session = Session()
        recipe = get_or_create(session, Recipe, uid=recipeData['id'])

        recipe.uid = recipeData['id']
        recipe.name = recipeData['name']
        recipe.headline = recipeData['headline']
        recipe.difficulty = str(recipeData['difficulty'])
        recipe.slug = recipeData['slug']
        recipe.country = recipeData['country']
        recipe.time = recipeData['time'][1:]
        recipe.rating = str(recipeData['rating'])
        recipe.favorites = str(recipeData['favorites'])

        session.add(recipe)
        session.commit()

    def parse(self):
        print('Updating Hello Fresh Recipe Data...')
        recipeJson = requests.get(HELLOFRESH_RECIPE_API, params={
                                  'count': HELLOFRESH_RECIPE_BATCH_COUNT})
        recipeData = json.loads(recipeJson.text)
        for recipe in recipeData:
            self.saveRecipeData(recipe)
