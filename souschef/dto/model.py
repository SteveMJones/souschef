class RecipeDTO(object):
    def __init__(self):
        self.name = None
        self.uid = None
        self.slug = None
        self.image_url = None
        self.thumnail_image_url = None
        self.url = None
        self.country = None
        self.ingredients = []


class IngredientDTO(object):
    def __init__(self):
        self.name = None
        self.description = None
        self.code = None
        self.amount = None
        self.unit = None