"""Config singleton class. Can be accessed anywhere in code to get global config
options read from .default_config.ini and .device_config.ini
"""

import configparser
from libs.patterns.singleton import Singleton

@Singleton
class DeviceConfig:
    def __init__(self):
        self.load_config_from_file()

    def load_config_from_file(self):
        self.options = configparser.ConfigParser()
        files = ['.default_config.ini', '.device_config.ini']
        read = self.options.read(files)
        if '.device_config.ini' not in read:
            print("WARNING: No device specific config. Default values will be used.")
