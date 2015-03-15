#!/usr/bin/env python
"""
    bg_daemon.util

    This module's purpose is to serve as a centralized location for
    different constant and methods that don't fit anywhere else
"""
import os
import shutil
from pkg_resources import Requirement, resource_filename, resource_string

# for package-specific locations, change this value (your home folder might be
# ideal for this)
HOME = os.path.join(os.path.expanduser("~"), ".bg_daemon")
PKG_LOCATION = resource_filename("bg_daemon", "")


def initialize_default_settings(filename):
    """
        initialize_default_settings

        If copies the default settings file from the package location into
        the home folder
    """
    settings_location = os.path.join(PKG_LOCATION, "settings.json")

    shutil.copy(settings_location, filename)

    return


def initialize_home_directory():
    """
        initialize_home_directory

        If the home folder is not found, initialize it.
    """

    if os.path.exists(HOME):
        return

    os.mkdir(HOME, 0770)

    settings_file = os.path.join(HOME, "settings.json")
    initialize_default_settings(settings_file)

    return
