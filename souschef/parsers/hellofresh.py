import requests
import json
import re
import demjson
import logging

from tqdm import tqdm
from sqlalchemy import exists
from bs4 import BeautifulSoup

from util import IngredientParser
from database.session import Session
from database.model import Recipe, Asset, RecipeTag, Tag, Ingredient, RecipeIngredient
from database.util import get_or_create

SERVICE_NAME = 'Hello Fresh'
SERVICE_CODE = 'hellofresh'
RECIPE_API = 'https://www.hellofresh.com/archive/recipes/'
RECIPE_BATCH_COUNT = 1
RECIPE_HTML_URL = 'https://www.hellofresh.com/recipes/'
RECIPE_PDF_URL = 'https://ddw4dkk7s1lkt.cloudfront.net/card/'


class HelloFresh(object):
    """Hello Fresh parser and downloader"""

    @classmethod
    def __init__(cls):
        cls.logger = logging.getLogger(__name__)

    @classmethod
    def download_all(cls):
        """Downloads full recipe data"""

        # Download meta data
        cls.download_recipe_meta_data(cls.get_recipe_meta_data())

        # Download recipe data
        cls.download_recipe_data()

    @classmethod
    def get_recipe_meta_data(cls):
        """Downloads recipe metadata"""

        cls.logger.info('Downloading Recipe Meta Data...')
        recipe_json = requests.get(
            RECIPE_API, params={'count': RECIPE_BATCH_COUNT})
        return json.loads(recipe_json.text)

    @classmethod
    def download_recipe_meta_data(cls, recipe_obj):
        """Persists recipe meta data from parsed json object"""

        cls.logger.info('Parsing and Saving Recipe Meta Data...')
        for recipe_data in tqdm(recipe_obj, unit='recipes'):
            session = Session()
            recipe = get_or_create(session, Recipe, uid=recipe_data['id'])

            recipe.uid = recipe_data['id']
            recipe.name = recipe_data['name']
            recipe.origin = SERVICE_CODE
            recipe.headline = recipe_data['headline']
            recipe.difficulty = str(recipe_data['difficulty'])
            recipe.slug = recipe_data['slug']
            recipe.country = recipe_data['country']
            recipe.time = recipe_data['time'][2:]
            recipe.rating = str(recipe_data['rating'])
            recipe.favorites = str(recipe_data['favorites'])
            recipe.url = RECIPE_HTML_URL + recipe.slug + '-' + recipe.uid

            assets = []
            image = Asset()
            image.type = 'image'
            image.url = recipe_data['image']
            assets.append(image)

            thumbnail = Asset()
            thumbnail.type = 'thumbnail'
            thumbnail.url = recipe_data['thumb']
            assets.append(thumbnail)
            recipe.assets = assets

            recipe_tags = []
            for tag_name in recipe_data['tags']:
                recipe_tag = RecipeTag()

                tag = get_or_create(session, Tag, name=tag_name)
                tag.name = tag_name

                recipe_tag.tag = tag
                recipe_tag.recipe = recipe
                recipe_tags.append(recipe_tag)

            recipe.tags = recipe_tags

            session.add(recipe)
            session.commit()

    @classmethod
    def download_recipe_data(cls):
        # Download full recipe data
        session = Session()
        recipes_dto = session.query(Recipe).filter(
            Recipe.origin == SERVICE_CODE).all()

        cls.logger.info('Parsing and saving recipe data')
        for recipe_dto in tqdm(recipes_dto, unit=' recipes'):
            cls.logger.info('Downloading recipe: ' + recipe_dto.name)

            recipe_html = requests.get(recipe_dto.url)
            # print(recipe.url)
            # print(recipe.uid)
            soup = BeautifulSoup(recipe_html.text, 'html.parser')
            scripts = soup.findAll('script', {'defer': ''})

            begin_search = '"' + recipe_dto.uid + '":{'
            end_search = '}},particle:'

            recipe_json = re.search(begin_search + '(.+?)' + end_search,
                                    scripts[6].text).group(1).replace(':!', ':')
            recipe_json = '{' + recipe_json + '}'
            recipe_obj = demjson.decode(recipe_json)

            yields = recipe_obj['yields']
            ingredient_yields = yields[0]['ingredients']

            # Ingredients
            ingredient_parser = IngredientParser()
            for ingredient in recipe_obj['ingredients']:
                recipe_ingredient_dtos = ingredient_parser.parse_ingredients_with_amounts(
                    ingredient['name'])
                if recipe_ingredient_dtos:
                    for recipe_ingredient_dto in recipe_ingredient_dtos:
                        for yld in ingredient_yields:
                            if yld['id'] == ingredient['id']:
                                ingredient_code = recipe_ingredient_dto.ingredient.code
                                ingredient_dto = get_or_create(
                                    session, Ingredient, code=ingredient_code)
                                ingredient_dto.name = recipe_ingredient_dto.ingredient.name
                                recipe_ingredient_dto = get_or_create(
                                    session, RecipeIngredient, recipe=recipe_dto, ingredient=ingredient_dto)
                                recipe_ingredient_dto.amount = str(yld['amount'])
                                recipe_ingredient_dto.unit = yld['unit']
                                break
