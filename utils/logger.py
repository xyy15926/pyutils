#!/usr/bin/env python3
#----------------------------------------------------------
#   Name: log.py
#   Author: xyy15926
#   Created at: 2020-09-07 18:58:23
#   Updated at: 2020-09-07 18:58:26
#   Description:
#----------------------------------------------------------
#%%
import os
import logging
import logging.config
import yaml

####################################################################
#
# Logging module manages all the logger registered, with `getLogger`
#   or `config`. And logger returned by `getLogger` will trigger
#   the registered parent logger `root` and loggers indicated by
#   the name seperated by `.`
#
# So logger registerer could be put in the parent module, and the
#   children module could get logger inheriting the default setting.
#
####################################################################


#%%

def get_logger(name=None, path=None, *, level=logging.DEBUG):
    """
    Description:
    get a logger attached with a file handler

    Params:
    name: logger name, `__name__` will be used as default name
    path: file logger path
    level: logging level

    Return:
    logger
    """

    name = name or __name__
    logger = logging.getLogger(name)
    logger.setLevel(level=logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # set and add a file handler
    file_handler = logging.FileHandler("log/{!s}.log".format(name))
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level=level)
    logger.addHandler(file_handler)

    # set and add a http handler
    # http_handler = logging.handlers.HTTPHandler(
    #     host="localhost:8001",
    #     url="log",
    #     method="POST",
    # )
    # logger.addHandler(http_handler)

    return logger


#%%

def setup_logging(path="logging.yml", level=logging.INFO):
    """
    Description:
    register loggers according the yaml config loaded

    Params:
    path: yaml config file
    level: logging level if no config file exists

    Returns:
    """

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            config = yaml.load(f)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

