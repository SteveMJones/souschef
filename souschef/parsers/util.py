import re

from database.model import Ingredient, RecipeIngredient


class IngredientParser(object):

    def __init__(self):
        self.replace_list = {u'\u215B': '1/8',
                             u'\u2153': '1/3',
                             u'\u2154': '2/3',
                             u'\u00BC': '1/4',
                             u'\u00BE': '3/4',
                             u'\u00BD': '1/2',
                             'ounce': 'oz',
                             'ounces': 'oz',
                             'teaspoon': 'tsp',
                             'tablespoon': 'tbsp',
                             'tablespoons': 'tbsp',
                             'cups': 'cup',
                             'inches': 'inch',
                             'bunches': 'bunch'}
        self.remove_list = ['*', '-', ',', 'of', 'divided', 'fresh']

        self.reject_list = ['not included']

        self.units = ['tsp', 'tbsp', 'cup', 'oz',
                      'pack', 'can', 'package', 'sprigs',
                      'knob', 'inch', 'bunch', 'pieces',
                      'piece']

    def replace_text(self, text):
        for i in self.replace_list.keys():
            text = re.sub(i, self.replace_list[i], text)
        
        for i in self.remove_list:
            text = text.replace(i, '')
            
        return text

    def test_rejections(self, text):
        if text.lower() in self.reject_list:
            return True
        if len(text) > 40:
            return True
        return False
    
    def clense_ingredients(self, ingredients):
        ingredients = self.replace_text(ingredients)

        if self.test_rejections(ingredients):
            return False
        return ingredients

    def parse_ingredients_with_amounts(self, ingredients):
        
        ingredients = self.clense_ingredients(ingredients)
        if not ingredients:
            return ingredients

        ingredients_parsed = []
        if ingredients.find('+') is not -1:
            ingredients_split = ingredients.split('+')
            ingredients_parsed.append(
                self.parse_ingredient(ingredients_split[1]))
            ingredients_parsed.append(self.parse_ingredient(
                ingredients_split[0] + ' ' + ingredients_parsed[0].ingredient.name))
        else:
            ingredients_parsed.append(self.parse_ingredient(ingredients))

        return ingredients_parsed

    def parse_ingredient(self, ingredient):
        amount = False
        unit = False

        ingredient = ingredient.strip()
        ingredient = ingredient.split(' ')

        # Detect amount
        if list(ingredient[0])[0].isdigit():
            amount = True

        # Detect unit
        if len(ingredient) > 1:
            if ingredient[1].lower() in self.units:
                unit = True

        start = 0
        ingredient_dto = Ingredient()
        recipe_ingredient_dto = RecipeIngredient()
        if amount and unit:
            amount = ingredient[0]
            if amount.find('/') == 2:
                ingredient[0] = list(amount)[0] + ' and ' + \
                    ''.join(list(amount)[1:])
            recipe_ingredient_dto.amount = ingredient[0].lower()
            recipe_ingredient_dto.unit = ingredient[1].lower()
            start = 2
        elif amount:
            recipe_ingredient_dto.amount = ingredient[0].lower()
            start = 1

        ingredient_dto.name = ' '.join(ingredient[start:]).lower().strip()
        ingredient_dto.code = ingredient_dto.name.replace(' ', '-')
        recipe_ingredient_dto.ingredient = ingredient_dto

        return recipe_ingredient_dto
