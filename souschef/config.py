#!/usr/bin/env python
import os

import configparser

CONFIG_FILE_PATH = 'configFile.cfg'


class Config(object):
    def __init__(self):
        self.configuration = configparser.ConfigParser()

        if not self.configuration.read(CONFIG_FILE_PATH):
            raise configparser.Error('{} file not found'
                                     .format(CONFIG_FILE_PATH))
        self.data_dir = self.configuration.get("DIRECTORIES", 'data_dir')

        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
