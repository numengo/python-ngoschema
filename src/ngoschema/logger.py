import logging

from . import utils

class HasLogger:
    logger = None

    @classmethod
    def init_class_logger(cls):
        cls.logger = logging.getLogger(utils.fullname(cls))

    @classmethod
    def set_logLevel(cls, logLevel):
        level = logging.getLevelName(logLevel)
        cls.logger.setLevel(level)
