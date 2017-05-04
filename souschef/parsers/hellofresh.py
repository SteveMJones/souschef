import requests
import json
import re
import demjson

from tqdm import tqdm
from sqlalchemy import exists
from bs4 import BeautifulSoup

from database.session import Session
from database.model import Recipe, Asset, RecipeTag, Tag
from database.util import get_or_create
from utils.logger import Logger

SERVICE_NAME = 'Hello Fresh'
SERVICE_CODE = 'hellofresh'
RECIPE_API = 'https://www.hellofresh.com/archive/recipes/'
RECIPE_BATCH_COUNT = 1
RECIPE_HTML_URL = 'https://www.hellofresh.com/recipes/'
RECIPE_PDF_URL = 'https://ddw4dkk7s1lkt.cloudfront.net/card/'

LOG = Logger(SERVICE_NAME)


class HelloFresh(object):
    """Hello Fresh parser and downloader"""

    @classmethod
    def download_all(cls):
        """Downloads full recipe data"""

        # Download meta data
        cls.download_recipe_meta_data(cls.get_recipe_meta_data())

        # Download full recipe data
        session = Session()
        recipes = session.query(Recipe).filter(
            Recipe.origin == SERVICE_CODE).all()

        for recipe in recipes:
            cls.download_recipe_data(recipe)

    @classmethod
    def get_recipe_meta_data(cls):
        """Downloads recipe metadata"""

        LOG.printLog('Downloading Recipe Meta Data...')
        recipe_json = requests.get(
            RECIPE_API, params={'count': RECIPE_BATCH_COUNT})
        return json.loads(recipe_json.text)

    @classmethod
    def download_recipe_meta_data(cls, recipe_obj):
        """Persists recipe meta data from parsed json object"""

        LOG.printLog('Parsing and Saving Recipe Meta Data...')
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
    def download_recipe_data(cls, recipe):
        recipe_html = requests.get(recipe.url)
        soup = BeautifulSoup(recipe_html.text, 'html.parser')
        scripts = soup.findAll('script', {'defer': ''})
        begin_search = '"' + recipe.uid + '":{'
        end_search = '}},notifications:'

        recipe_json = re.search(begin_search + '(.+?)' + end_search,
                                scripts[5].text).group(1).replace(':!', ':')
        recipe_json = '{' + recipe_json + '}'
        recipe_obj = demjson.decode(recipe_json)
        # print(recipe_obj)
        for ingredient in recipe_obj['ingredients']:
            print(ingredient)
