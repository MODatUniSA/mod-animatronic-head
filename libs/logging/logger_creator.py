"""Initialises our logger as a rotating log that writes to 2 log files and outputs to console
Provides simple methods for fetching logger with name set correctly (so all loggers will use the same config)

Driver should call LoggerCreator().create_logger() before any calls to logger_for are made. create_logger() should only be called once per program execution.
"""

import sys
import os
import logging
from logging.handlers import RotatingFileHandler

# Sentry Integration
from raven import Client, fetch_git_sha
from raven.handlers.logging import SentryHandler
from raven.conf import setup_logging

from libs.config.device_config import DeviceConfig

class LoggerCreator:
    def create_logger(self, path=None):
        """
        Creates a logger that logs to 2 different log files at different levels
        Pass path without an extension, so we can append to the file name for the different logs
        """

        logger_name = 'application'

        if path is None:
            path = 'logs/{}'.format(logger_name)

        # Get a base level logger, so other classes don't need to know logger base
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # Allow total of 1GB of each type of log file
        # Each log file can grow to 100mb. The most recent 5 are kept
        handler = RotatingFileHandler("{}_error.log".format(path), maxBytes=100000000,
        backupCount=5)
        handler.setLevel(logging.WARNING)
        handler.setFormatter(formatter)

        verbose_handler = RotatingFileHandler("{}_output.log".format(path), maxBytes=100000000,
        backupCount=5)
        verbose_handler.setLevel(logging.DEBUG)
        verbose_handler.setFormatter(formatter)

        # Handler for console output
        logger.debug("Stream handler created with level %s", type(self)._console_level())
        console_handler = logging.StreamHandler()
        console_handler.setLevel(type(self)._console_level())
        console_handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.addHandler(verbose_handler)
        logger.addHandler(console_handler)

        sentry_config = DeviceConfig.Instance().options['SENTRY']
        if sentry_config.getboolean('ENABLED'):
            dsn = sentry_config["DSN"]
            environment = sentry_config["ENVIRONMENT"]
            type(self)._setup_sentry_integration(dsn, environment, formatter)

        return logger

    @classmethod
    def _setup_sentry_integration(cls, dsn, environment, formatter):
        # IDEA: May want to create client in singleton proxy, so other parts of the code can access
        #       Do this if we want to send messages in any other way
        client = Client(
            dsn=dsn,
            environment=environment,
            include_paths=['app', 'libs'],
            # FIXME: want to automatically set release by git sha
            # release=fetch_git_sha(os.path.dirname(__file__)),
            repos={'raven' : {'name': 'wearesandpit/almost-human'}},
        )

        handler = SentryHandler(client)
        handler.setLevel(logging.WARNING)
        handler.setFormatter(formatter)
        setup_logging(handler)

    @staticmethod
    def logger_for(name):
        """Syntactic sugar to get a logger by the provided name."""
        return logging.getLogger(name)

    @staticmethod
    def _console_level():
        if '-vv' in sys.argv:
            return logging.DEBUG
        elif '-v' in sys.argv:
            return logging.INFO
        else:
            return logging.WARNING
