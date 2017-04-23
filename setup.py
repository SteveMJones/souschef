#!/usr/bin/env python
import re
from os import path

from setuptools import find_packages, setup

ROOT = path.dirname(__file__)
NAME = 'hello_fresh_recipes'
DESCRIPTION = 'Automatically download and parse Hello Fresh Recipes.'


def get_version():
    init_file = path.join(ROOT, NAME, '__init__.py')
    pattern = re.compile("__version__ = '(?P<ver>.*?)'")
    with open(init_file, 'rb') as fo:
        for line in fo:
            line = line.decode('utf-8')
            match = pattern.match(line)
            if match:
                return match.group('ver')
    return None


def get_packages():
    pkgs = [
        NAME + '.' + pkg
        for pkg in find_packages(NAME, exclude=['*.tests'])
    ]
    return [NAME] + pkgs


setup(
    name=NAME,
    version=get_version(),
    description=DESCRIPTION,
    install_requires=[
        'requests==2.13.0',
        'beautifulsoup4==4.5.3',
        'future==0.16.0',
        'configparser==3.5.0',
        'sqlalchemy'
    ],
    packages=get_packages(),
    entry_points={
        'console_scripts': [
            'hello_fresh_recipes=hello_fresh_recipes.recipes:main'
        ]
    }
)