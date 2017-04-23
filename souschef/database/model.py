from sqlalchemy import create_engine, Column, ForeignKey, Integer, String
from sqlalchemy import String, DateTime, Binary, Enum, func
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Asset(Base):
    __tablename__ = 'asset'
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipe.id'))
    ingredient_id = Column(Integer, ForeignKey('ingredient.id'))
    instruction_id = Column(Integer, ForeignKey('instruction.id'))
    type = Column(Enum('image', 'thumbnail', 'pdf'))
    url = Column(String)
    size = Column(String)
    size_unit = Column(String)
    path = Column(String)
    filename = Column(String)
    downloaded = Column(Binary)
    download_date = Column(DateTime)
    recipe = relationship("Recipe", back_populates='assets')
    ingredient = relationship("Ingredient", back_populates='image')
    instruction = relationship("Instruction", back_populates='image')


class Recipe(Base):
    __tablename__ = 'recipe'
    id = Column(Integer, primary_key=True)
    uid = Column(String, nullable=False, unique=True)
    country = Column(String)
    name = Column(String)
    headline = Column(String)
    time = Column(String)
    difficulty = Column(Integer)
    favorites = Column(Integer)
    rating = Column(String)
    slug = Column(String)
    description = Column(String)
    url = Column(String)
    published_date = Column(DateTime)
    created_date = Column(DateTime, default=func.now())
    assets = relationship("Asset")
    ingredients = relationship(
        "RecipeIngredient", back_populates='recipe')
    instructions = relationship("Instruction", back_populates='recipe')


class Ingredient(Base):
    __tablename__ = 'ingredient'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    contains = Column(String)
    image = relationship("Asset", uselist=False, back_populates='ingredient')


class RecipeIngredient(Base):
    __tablename__ = 'recipe_ingredient'
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipe.id'))
    ingredient_id = Column(Integer, ForeignKey('ingredient.id'))
    amount = Column(String)
    unit = Column(String)
    recipe = relationship("Recipe", back_populates='ingredients')
    ingredient = relationship("Ingredient")


class Instruction(Base):
    __tablename__ = 'instruction'
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer)
    step = Column(Integer)
    description = Column(String)
    image = relationship("Asset", uselist=False, back_populates='instruction')
    recipe = relationship("Recipe", back_populates='instructions')

