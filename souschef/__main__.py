#!/usr/bin/env python
from __future__ import print_function

import argparse

from database.session import Session
from database.model import Recipe, Asset, RecipeIngredient, Ingredient
from database.util import init as database_init
from database.util import reset as database_reset

from parsers.hellofresh import HelloFresh
from parsers.purplecarrot import PurpleCarrot


# Main
def main():
    """Main execution point"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-rd', '--resetdb', action='store_true')
    args = parser.parse_args()

    if args.resetdb:
        database_reset()
    else:
        database_init()

    '''
    hello_fresh = HelloFresh()
    hello_fresh.download_all()
    '''
    purple_carrot = PurpleCarrot()
    purple_carrot.download_all()

if __name__ == '__main__':
    main()
