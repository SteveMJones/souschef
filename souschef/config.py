#!/usr/bin/env python
import os
import yaml
import configparser

CONFIG_FILE_PATH = 'souschef.conf'


class Config(object):
    def __init__(self):
        with open(CONFIG_FILE_PATH, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)

        self.data_dir = cfg['main']['data']
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
