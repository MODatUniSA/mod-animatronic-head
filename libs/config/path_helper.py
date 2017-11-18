""" Helpers for fetching and validating files paths
"""

import os

from libs.config.device_config import DeviceConfig

class PathHelper:
    config = DeviceConfig.Instance()
    path_options = config.options['PATHS']
    base_audio_path = path_options['BASE_AUDIO_PATH']
    base_instruction_path = path_options['BASE_INSTRUCTION_PATH']

    @classmethod
    def is_valid_path(cls, path):
        return os.path.isfile(path)

    @classmethod
    def audio_path(cls, file_name):
        return os.path.join(cls.base_audio_path, file_name)

    @classmethod
    def is_valid_audio_file(cls, filename):
        if filename is None:
            return False

        return cls.is_valid_path(cls.audio_path(filename))

    @classmethod
    def instruction_path(cls, file_name):
        return os.path.join(cls.base_instruction_path, file_name)

    @classmethod
    def is_valid_instruction_file(cls, filename):
        if filename is None:
            return False

        return cls.is_valid_path(cls.instruction_path(filename))
