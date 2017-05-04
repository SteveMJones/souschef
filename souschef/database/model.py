from sqlalchemy import create_engine, Column, ForeignKey, Integer, String
from sqlalchemy import String, DateTime, Binary, Enum, func
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Recipe(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True)
    uid = Column(String, unique=True)
    origin = Column(String)
    country = Column(String)
    name = Column(String)
    headline = Column(String)
    time = Column(String)
    difficulty = Column(Integer)
    servings = Column(Integer)
    favorites = Column(Integer)
    rating = Column(String)
    slug = Column(String)
    description = Column(String)
    url = Column(String)
    published_date = Column(DateTime)
    created_date = Column(DateTime, default=func.now())
    assets = relationship('Asset', backref='recipe')
    ingredients = relationship(
        'RecipeIngredient', backref='recipe')
    instructions = relationship('Instruction', back_populates='recipe')
    nutrition = relationship('RecipeNutrition', back_populates='recipe')
    tags = relationship('RecipeTag', back_populates='recipe')
    utensils = relationship('RecipeUtensil', back_populates='recipe')


class Asset(Base):
    __tablename__ = 'assets'
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'))
    instruction_id = Column(Integer, ForeignKey('instructions.id'))
    type = Column(Enum('image', 'thumbnail', 'pdf'))
    url = Column(String)
    size = Column(String)
    size_unit = Column(String)
    path = Column(String)
    filename = Column(String)
    downloaded = Column(Binary)
    download_date = Column(DateTime)
    error = Column(Binary)
    error_code = Column(String)
    error_msg = Column(String)


class Ingredient(Base):
    __tablename__ = 'ingredients'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    code = Column(String)
    contains = Column(String)
    image = relationship('Asset', uselist=False, backref='ingredient')
    recipe_ingredients = relationship('RecipeIngredient', backref='ingredient')


class RecipeIngredient(Base):
    __tablename__ = 'recipe_ingredient'
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'))
    amount = Column(String, default='1')
    unit = Column(String, default='unit')


class Instruction(Base):
    __tablename__ = 'instructions'
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    step = Column(Integer)
    description = Column(String)
    image = relationship("Asset", uselist=False, backref='instruction')
    recipe = relationship("Recipe", back_populates='instructions')


class RecipeNutrition(Base):
    __tablename__ = 'recipe_nutrition'
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    nutrition_id = Column(Integer, ForeignKey('nutrition.id'))
    amount = Column(String)
    unit = Column(String)
    nutrition = relationship('Nutrition')
    recipe = relationship('Recipe', back_populates='nutrition')


class Nutrition(Base):
    __tablename__ = 'nutrition'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String)
    description = Column(String)


class RecipeTag(Base):
    __tablename__ = 'recipe_tag'
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    tag_id = Column(Integer, ForeignKey('tags.id'))
    tag = relationship('Tag')
    recipe = relationship('Recipe', back_populates='tags')


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)


class RecipeUtensil(Base):
    __tablename__ = 'recipe_utensil'
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    utensil_id = Column(Integer, ForeignKey('utensils.id'))
    recipe = relationship('Recipe', back_populates='utensils')
    utensil = relationship('Utensil')


class Utensil(Base):
    __tablename__ = 'utensils'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
