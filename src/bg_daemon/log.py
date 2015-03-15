#!/usr/bin/env python
"""
    logger.py

    Intended to be used as a centralized module for all logging calls in the
    bg_daemon classes.

    The first time the module is imported, a logger instance is created, if
    it is allocated by other modules, the same logger instance will be queried.

    <usage>
        main program:
            import .log
            log.log("Message")

        fetchers:
            import logging
            log = logging.getLogger("bg_daemon")
            log.log("message")

"""
import logging
import os
from pkg_resources import Requirement, resource_filename, resource_string

# We set some sane defaults here, we filted differently if the logging
# calls are meant to be to the console or somewhere else
_BASE_PATH = resource_filename("bg_daemon", "")
_DEFAULT_LOG_FILENAME = os.path.join(_BASE_PATH, "bg_daemon.log")
_DEFAULT_LOG_LEVEL = logging.DEBUG
_DEFAULT_CONSOLE_LOG_LEEL = logging.INFO
_DEFAULT_FILE_LOG_LEVEL = logging.DEBUG

# define the hardcoded format string
_FORMAT_STRING = ("[%(asctime)s] [%(name)s] [%(levelname)s]"
                  "[%(funcName)s:%(lineno)s@%(filename)s]\n\t%(message)s")
formatter = logging.Formatter(_FORMAT_STRING)

# define the handler, we are going to write our log to a file
file_handler = logging.FileHandler(_DEFAULT_LOG_FILENAME)
file_handler.setLevel(_DEFAULT_FILE_LOG_LEVEL)
file_handler.setFormatter(formatter)

# define the logger itself
logger = logging.getLogger('bg_daemon')
logger.setLevel(_DEFAULT_LOG_LEVEL)
logger.addHandler(file_handler)
