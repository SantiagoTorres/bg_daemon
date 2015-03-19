#!/usr/bin/env python
"""
    bg_daemon.util

    This module's purpose is to serve as a centralized location for
    different constant and methods that don't fit anywhere else
"""
import os
import shutil
from hashlib import sha256
from pkg_resources import Requirement, resource_filename, resource_string

# for package-specific locations, change this value (your home folder might be
# ideal for this)
HOME = os.path.join(os.path.expanduser("~"), ".bg_daemon")
PKG_LOCATION = resource_filename("bg_daemon", "")
DIGEST_LENGTH = 10


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


def get_digest_for_file(filename):
    """
        get_digest_for_file

            calculates a sha256 digest for a given file, used when backing up a
            file. 
            
            In order to support legacy systems, the digest will be truncated
            to a certain length

        arguments:
            filename: the filename of the file to obtain the digest from 

        returns:
            the a hex-encoded string containing the hash-prefix of the file
    """
    with open(filename) as fp:

        data = fp.read()

    digest = sha256(data).digest()

    return hexify(digest)[:DIGEST_LENGTH]


def hexify(byte_array):
    """
        hexify:

        on input a byte stream, output its hex representation

        arguments:
            byte_array: a byte array to convert to hexadecimal

        output:
            the hex representation of the byte array in a string
    """
    return "".join("{:02x}".format(ord(c)) for c in byte_array)



