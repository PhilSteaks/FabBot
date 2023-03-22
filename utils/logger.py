"""
Helper util for logging
"""
import os
import sys
import logging
import logging.handlers


FILENAME = "/opt/log/fab-bot.log"
should_roll_over = os.path.isfile(FILENAME)
handler = logging.handlers.RotatingFileHandler(FILENAME, backupCount=5)
if should_roll_over:  # log already exists, roll over!
    handler.doRollover()

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)

logging.basicConfig(
    filename=FILENAME,
    format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d]    %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.addHandler(stream_handler)

def debug(message):
    """ helper """
    logger.debug(message)

def info(message):
    """ helper """
    logger.info(message)

def warning(message):
    """ helper """
    logger.warning(message)

def error(message):
    """ helper """
    logger.error(message)

def critical(message):
    """ helper """
    logger.critical(message)
