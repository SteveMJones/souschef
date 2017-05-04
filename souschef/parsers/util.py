import re

from database.model import Ingredient, RecipeIngredient


class IngredientParser(object):

    def __init__(self):
        self.char_replacement = {u'\x215b': '1/8',
                                 u'\x2153': '1/3',
                                 u'\x2154': '2/3',
                                 u'\xbc': '1/4',
                                 u'\xbe': '3/4',
                                 u'\xbd': '1/2',
                                 '\*': ''}
        self.units = ['tsp', 'tbsp', 'cup', 'oz', 'pack', 'can', 'package']
        self.rejects = ['not included']

    def strip_bad_characters(self, text):
        for i in self.char_replacement.keys():
            text = re.sub(i, self.char_replacement[i], text)
        return text

    def test_rejections(self, text):
        if text.lower() in self.rejects:
            return True
        elif len(text.split(' ')) > 5:
            return True
        return False

    def parse_ingredients(self, ingredients):
        ingredients = self.strip_bad_characters(ingredients)
        if self.test_rejections(ingredients):
            return False

        ingredients_parsed = []
        if ingredients.find('+') is not -1:
            ingredients_split = ingredients.split('+')
            ingredients_parsed.append(
                self.parse_ingredient(ingredients_split[1]))
            ingredients_parsed.append(self.parse_ingredient(
                ingredients_split[0] + ' ' + ingredients_parsed[0].name))
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
        
        ingredient_dto.name = ' '.join(ingredient[start:]).lower()
        ingredient_dto.code = '-'.join(ingredient[start:]).lower()
        recipe_ingredient_dto.ingredient = ingredient_dto

        return recipe_ingredient_dto
