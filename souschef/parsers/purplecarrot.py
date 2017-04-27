import requests
import json
import urlparse
import uuid

from tqdm import tqdm
from tqdm import trange
from sqlalchemy import exists
from bs4 import BeautifulSoup

from database.session import Session
from database.model import Recipe, Asset, RecipeTag, Tag
from database.util import get_or_create
from utils.logger import Logger

SERVICE_NAME = 'Purple Carrot'
SERVICE_CODE = 'purplecarrot'
RECIPE_API = 'https://www.purplecarrot.com/plant-based-recipes'
RECIPE_API_PAGES_COUNT = 20
RECIPE_BATCH_COUNT = 1000

LOG = Logger(SERVICE_NAME)


class PurpleCarrot(object):
    maxApiPage = None

    """Purple Carrot parser and downloader"""
    @classmethod
    def __init__(cls):
        cls.hostname = urlparse.urlparse(RECIPE_API).hostname or ''
        LOG.printLog('Finding recipes to download...')
        page = RECIPE_API_PAGES_COUNT
        while True:
            req = requests.get(RECIPE_API, params={'page': page})
            soup = BeautifulSoup(req.text, 'html.parser')
            recipes = soup.find('ul', {'class': 'row'}).findAll('li')
            if not recipes:
                cls.maxApiPage = page
                break
            page += 1

    @classmethod
    def download_all(cls):
        """Downloads full recipe data"""
        cls.get_recipe_meta_data()
        return
        # Download meta data
        cls.download_recipe_meta_data()

        # Download full recipe data
        session = Session()
        recipes = session.query(Recipe).filter(
            Recipe.origin == SERVICE_CODE).all()

        for recipe in recipes:
            cls.download_recipe_data(recipe)

    @classmethod
    def get_recipe_meta_data(cls):
        """Downloads recipe metadata"""
        LOG.printLog('Parsing and saving recipe meta data...')
        recipeCount = 1
        for page in trange(1, cls.maxApiPage, unit='recipe pages'):
            req = requests.get(RECIPE_API, params={'page': page})
            soup = BeautifulSoup(req.text, 'html.parser')
            section = soup.find('section', {'id': 'archive-recipes'})
            recipes = section.findAll('li')
            for recipe_html in recipes:
                if recipeCount > RECIPE_BATCH_COUNT:
                    return
                cls.download_recipe_meta_data(recipe_html)
                recipeCount += 1
            page += 1

    @classmethod
    def parse_recipe_html(cls, recipe_html):
        recipe_dto = RecipeDTO()
        recipe_dto.name = recipe_html.img['title']
        recipe_dto.slug = recipe_html.a['href'].replace('/plant-based-recipes/','')
        recipe_dto.url = 'https://' + cls.hostname + str(recipe_html.a['href'])
        recipe_dto.image_url = recipe_html.img['src']
        recipe_dto.origin = SERVICE_CODE
        recipe_dto.country = 'US'
        return recipe_dto

    @classmethod
    def download_recipe_meta_data(cls, recipe_html):
        """Persists recipe meta data from html object"""

        recipe_dto = cls.parse_recipe_html(recipe_html)

        session = Session()
        recipe = get_or_create(session, Recipe, slug=recipe_dto.slug)

        recipe.name = recipe_dto.name
        recipe.origin = recipe_dto.origin
        recipe.slug = recipe_dto.slug
        recipe.country = recipe_dto.country
        recipe.url = recipe_dto.url

        assets = []
        image = Asset()
        image.type = 'thumbnail'
        image.url = recipe_dto.image_url
        assets.append(image)

        recipe.assets = assets

        session.add(recipe)
        session.commit()

    @classmethod
    def download_recipe_data(cls, recipe):
        recipe_html = requests.get(recipe.url)
        soup = BeautifulSoup(recipe_html.text, 'html.parser')
        script_jsons = soup.findAll("script")
        for i in script_jsons:
            if i.text is not None:
                print(i.text)


class RecipeDTO(object):
    def __init__(self):
        self.name = None
        self.uid = None
        self.slug = None
        self.image_url = None
        self.url = None
        self.country = None
