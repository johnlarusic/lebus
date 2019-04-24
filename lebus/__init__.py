# Hooks for logging
import sys
import os
import json
import logging
import logging.config
import threading
import time
import datetime


def setup_logging(
    default_path='log_config.json',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    path = "{}/{}".format(sys.path[0], default_path)
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


setup_logging()
logging.getLogger(__name__).addHandler(logging.NullHandler())
LOG_HELPER = logging.getLogger()


# Package objects to import
from schedule import *
from timer import *
from print_schedule import *
from graphic_schedule import *
from util import *
