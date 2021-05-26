'''
Created on 2014-02-08

@author: y136wang
'''
from robot.api import logger

class Logger(object):

    def __init__(self):
        self.console_also = False

    def set_console_also(self, value):
        self.console_also = value

    def trace(self, msg, html=False):
        logger.trace(msg, html)
        if self.console_also:
            logger.console(msg)


    def debug(self, msg, html=False):
        logger.debug(msg, html)
        if self.console_also:
            logger.console(msg)


    def info(self, msg, html=False):
        logger.info(msg, html, self.console_also)


    def warn(self, msg, html=False):
        logger.warn(msg, html)
        if self.console_also:
            logger.console(msg)

LOGGER = Logger()

