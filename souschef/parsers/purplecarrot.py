import urlparse
import json
import requests
import logging

from tqdm import tqdm
from bs4 import BeautifulSoup

from util import IngredientParser
from database.session import Session
from database.model import Recipe, Asset, Ingredient, RecipeIngredient
from database.model import Nutrition, RecipeNutrition, Instruction
from database.util import get_or_create

SERVICE_NAME = 'Purple Carrot'
SERVICE_CODE = 'purplecarrot'
RECIPE_API = 'https://www.purplecarrot.com/plant-based-recipes'

RECIPE_API_PAGE_SCAN_START = 20
RECIPES_PER_PAGE = 20
RECIPE_BATCH_COUNT = 50


class PurpleCarrot(object):
    max_api_page = None
    num_of_recipes = None

    """Purple Carrot parser and downloader"""
    @classmethod
    def __init__(cls):
        cls.logger = logging.getLogger(__name__)
        cls.hostname = urlparse.urlparse(RECIPE_API).hostname or ''

    @classmethod
    def download_all(cls):
        """Downloads full recipe data"""
        # Get max page
        cls.get_max_recipe_page()

        # Download meta data
        cls.download_recipe_meta_data()

        # Download full recipe data
        cls.download_recipe_data()

    @classmethod
    def get_max_recipe_page(cls):
        """Parses recipe pages to find max page number"""
        cls.logger.info('Finding recipes to download')
        page = RECIPE_API_PAGE_SCAN_START
        last_page_recipe_num = 20
        while True:
            req = requests.get(RECIPE_API, params={'page': page})
            soup = BeautifulSoup(req.text, 'html.parser')
            recipes = soup.find('ul', {'class': 'row'}).findAll('li')
            if not recipes:
                cls.max_api_page = page
                cls.num_of_recipes = RECIPES_PER_PAGE * \
                    (page - 2) + last_page_recipe_num
                break
            last_page_recipe_num = len(recipes)
            page += 1

    @classmethod
    def get_recipe_batch_count(cls):
        if RECIPE_BATCH_COUNT < cls.num_of_recipes:
            return RECIPE_BATCH_COUNT
        else:
            return cls.num_of_recipes

    @classmethod
    def download_recipe_meta_data(cls):
        """Downloads recipe metadata"""
        session = Session()

        # loading bar based on recipe count
        recipe_count = 1
        recipe_batch_count = cls.get_recipe_batch_count()
        cls.logger.info('Parsing and saving recipe meta data')
        with tqdm(total=recipe_batch_count, unit=' recipes') as pbar:
            for page in range(1, cls.max_api_page):
                req = requests.get(RECIPE_API, params={'page': page})
                soup = BeautifulSoup(req.text, 'html.parser')
                section = soup.find('section', {'id': 'archive-recipes'})
                recipes = section.findAll('li')
                for recipe_html in recipes:
                    if recipe_count > RECIPE_BATCH_COUNT:
                        return

                    slug = recipe_html.a['href'].replace(
                        '/plant-based-recipes/', '')
                    recipe = get_or_create(session, Recipe, slug=slug)

                    recipe.name = recipe_html.img['title']
                    cls.logger.info('Parsing recipe: ' + recipe.name)
                    recipe.slug = slug
                    recipe.url = 'https://' + cls.hostname + \
                        str(recipe_html.a['href'])
                    recipe.origin = SERVICE_CODE
                    recipe.country = 'US'

                    assets = []
                    thumbnail_url = recipe_html.img['src']
                    thumbnail = get_or_create(
                        session, Asset, url=thumbnail_url)
                    thumbnail.type = 'thumbnail'
                    thumbnail.url = thumbnail_url
                    assets.append(thumbnail)

                    recipe.assets = assets

                    session.add(recipe)
                    session.commit()

                    pbar.update(1)
                    recipe_count += 1
                page += 1

    @classmethod
    def download_recipe_data(cls):
        session = Session()

        recipes_dto = session.query(Recipe).filter(
            Recipe.origin == SERVICE_CODE).all()

        cls.logger.info('Parsing and saving recipe data')
        for recipe_dto in tqdm(recipes_dto, unit=' recipes'):
            cls.logger.info('Downloading recipe: ' + recipe_dto.name)
            recipe_html = requests.get(recipe_dto.url)
            soup = BeautifulSoup(recipe_html.text, 'html.parser')

            # Main Image
            tag = soup.find('source', {'media': '(max-width: 1199px)'})
            image_url = tag['srcset']
            image = get_or_create(session, Asset, url=image_url)
            image.type = 'image'
            image.url = image_url
            recipe_dto.assets.append(image)

            # Description
            description = soup.find(
                'section', {'class': 'recipe-description'}).find('p')
            recipe_dto.description = description.text

            # Summary
            uls = soup.find('div', {'class': 'recipe-side-note'}).findAll('ul')
            li = uls[0].findAll('li')
            prep = li[0].text.split(':')
            time = prep[1].replace('minutes', 'M').replace(' ', '')
            recipe_dto.time = time[:time.find('M')+1]
            servings = li[1].text.split(':')
            recipe_dto.servings = servings[1]

            # Nutrition
            for li in uls[1].findAll('li'):
                nutrition = li.text.split(':')
                nutrition_name = nutrition[0].strip()
                nutrition_code = nutrition_name.lower().replace(' ', '-')

                nutrition_dto = get_or_create(
                    session, Nutrition, code=nutrition_code)
                nutrition_dto.name = nutrition_name

                nutrition_amount = nutrition[1].strip()
                nutrition_unit = None

                if nutrition_code == 'calories':
                    nutrition_unit = 'cal'
                else:
                    nutrition_unit = 'g'

                recipe_nutrition_dto = get_or_create(
                    session, RecipeNutrition, recipe=recipe_dto, nutrition=nutrition_dto)
                recipe_nutrition_dto.amount = nutrition_amount
                recipe_nutrition_dto.unit = nutrition_unit

            # Ingredients
            main_recipe = soup.find('section', {'class': 'main-recipe'})
            ingredients = main_recipe.find('ol').findAll('li')
            ingredient_parser = IngredientParser()
            for ingredient in ingredients:
                recipe_ingredient_dtos = ingredient_parser.clense_ingredients(
                    ingredient.string)
                if recipe_ingredient_dtos:
                    for recipe_ingredient_dto in recipe_ingredient_dtos:
                        ingredient_dto = get_or_create(
                            session, Ingredient, code=recipe_ingredient_dto.ingredient.code)
                        ingredient_dto.name = recipe_ingredient_dto.ingredient.name

                        recipe_ingredient = get_or_create(
                            session, RecipeIngredient, recipe=recipe_dto, ingredient=ingredient_dto)
                        recipe_ingredient.ingredient = ingredient_dto

                        if recipe_ingredient_dto.amount is not None:
                            recipe_ingredient.amount = recipe_ingredient_dto.amount

                        if recipe_ingredient_dto.unit is not None:
                            recipe_ingredient.unit = recipe_ingredient_dto.unit

            # Instructions
            steps = soup.find(
                'section', {'class': 'recipe-instruct'}).findAll('div', {'class': 'row'})
            stepNbr = 1
            for step in steps[1:]:
                instruction_dto = get_or_create(
                    session, Instruction, recipe=recipe_dto, step=stepNbr)
                instruction_dto.description = step.find(
                    'p', {'class': 'instruction-description'}).text

                instruction_image_dto = get_or_create(
                    session, Asset, instruction=instruction_dto, type='image')
                instruction_image_dto.url = step.find('img')['src']
                stepNbr += 1

            session.commit()
