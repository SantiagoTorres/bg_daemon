#!/usr/bin/env python
"""
    bg_daemon.util

    This module's purpose is to serve as a centralized location for
    different constant and methods that don't fit anywhere else
"""
import sys
import os
import shutil
import json
import crontab
from hashlib import sha256
from pkg_resources import Requirement, resource_filename, resource_string

# for package-specific locations, change this value (your home folder might be
# ideal for this)
HOME = os.path.join(os.path.expanduser("~"), ".bg_daemon")
DEFAULT_IMAGE = "bg.jpg"
PKG_LOCATION = resource_filename("bg_daemon", "")
SETTINGS_LOCATION = resource_filename(Requirement.parse("bg_daemon"), 
                                      "settings.json")
MAC_OS_SCRIPT_LOCATION = resource_filename(Requirement.parse("bg_daemon"),
                                           "mac-update.sh")
DIGEST_LENGTH = 10
STDOUT_RELOCATION = os.path.join(HOME, "output.log")
DEFAULT_COMMAND = ("/usr/local/bin/background_daemon.py "
                   ">> {}".format(STDOUT_RELOCATION))


def initialize_default_settings(filename):
    """
        initialize_default_settings

        If copies the default settings file from the package location into
        the home folder, and updates values if needed
    """
    settings_location = os.path.join(PKG_LOCATION, "settings.json")

    shutil.copy(settings_location, filename)

    with open(filename) as fp:
        settings_template = json.load(fp)

    new_settings = set_default_settings(settings_template)

    with open(filename, 'wt') as fp:
        json.dump(new_settings, fp)

    return


def initialize_home_directory():
    """
        initialize_home_directory

        If the home folder is not found, initialize it.
    """

    if os.path.exists(HOME):
        return

    os.mkdir(HOME, 0770)

    # some sudo calls change the euid, uid and ruid to 0, which might not be
    # accessible later when running as a user process. This, for some reason
    # happens on certain MacOS systems
    if "SUDO_UID" in os.environ:
        uid = int(os.environ["SUDO_UID"])
        gid = int(os.environ["SUDO_GID"])
        os.lchown(HOME, uid, gid)

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


def set_default_settings(settings):
    """ 
        set_default_setings:

        loads the template file and updates the values with a sane default.
        adds platform specific hooks and whatnot.

        arguments:

            settings: a json dictionary containing the settings template

        output:
            
            the new settings dictionary, ready to be saved.
    """
    assert('daemon' in settings)

    daemon = settings['daemon']

    daemon['target'] = os.path.join(HOME, DEFAULT_IMAGE)
    # check if we need to make any mac specific checks
    if sys.platform == 'darwin':


        update_script = MAC_OS_SCRIPT_LOCATION 
        update_script_target = os.path.join(HOME, 'mac-update.sh')
        shutil.copy(update_script, update_script_target)
        daemon['update_hook'] = "bash {} {}".format(update_script_target,
                                                    daemon['target'])

    settings['daemon'] = daemon
    return settings['daemon']

def add_crontab_entry(days = None, hours = None, minutes = 5):
    """
        add_crontab_entry:

        adds a crontab entry to call the daemon every day, hour, and minute
        that's specified as an argument

        input:
            days: each [days] days this job will be executed

            hours: each [hours] hours this job will be executed

            minutes: each [minutes] minutes this job will be executes

        output:

            the resulting crontab

        side-effects:
            
            the user's crontab entry will be modified with the corresponding 
            cronjob

    """
    tab = crontab.CronTab(user=True)

    # verify that we haven't populated the crontab yet
    if _is_crontab_populated(tab):
        return tab

    new_job = tab.new(command=DEFAULT_COMMAND)
    
    if days:
        new_job.day.every(days)

    if hours:
        new_job.hour.every(hours)

    if minutes:
        new_job.minutes.every(minutes)

    new_job.set_comment("Background daemon")

    if not new_job.is_valid():
        raise Exception("couldn't create job!")

    tab.write_to_user(user=True)

    return tab


def remove_crontab_entry():
    """
        remove_crontab_entry:

        removes the background_daemon entry in the crontab

        input:
            Nothing

        output:
            
            the resulting crontab

        side-effects
            
            the bg_daemon entry in the crontab will be removed
    """
    tab = crontab.CronTab(user = True)

    jobs = [x for x in tab.find_command("background_daemon.py")]

    if len(jobs) == 0:
        return tab

    for job in jobs:
        if job.command == (DEFAULT_COMMAND):
            tab.remove(job)

    tab.write_to_user(user=True)
    return tab


def _is_crontab_populated(cron):
    """
        _is_crontab_populated:

        checks in the crontab already contains the background_daemon entry

        returns:
            True if the entry is already there
            False if the entry is not there

    """
    jobs = [x for x in cron.find_command("background_daemon.py")]

    if len(jobs) == 0:
        return False

    for job in jobs:
        if job.command.startswith("/usr/local/bin/background_daemon.py"):
            return True

    return False
