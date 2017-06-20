#!/usr/bin/env python
from __future__ import print_function

import logging
import logging.config
import argparse
import yaml

import database.util as db_util

from parsers.hellofresh import HelloFresh
from parsers.purplecarrot import PurpleCarrot


# Main
def main():
    """Main execution point"""
    logging.config.dictConfig(yaml.load(open('logging.conf', 'r')))
    logger = logging.getLogger('main')

    logger.info('Running souschef')
    logger.debug('main() - start')

    parser = argparse.ArgumentParser()
    parser.add_argument('-rd', '--resetdb', action='store_true')
    args = parser.parse_args()

    if args.resetdb:
        db_util.reset()
    else:
        db_util.init()

    hello_fresh = HelloFresh()
    hello_fresh.download_all()
    '''
    purple_carrot = PurpleCarrot()
    purple_carrot.download_all()
    '''
    logger.debug('main() - end')

if __name__ == '__main__':
    main()
