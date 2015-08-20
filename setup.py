#!/usr/bin/env python

import os
from setuptools import setup
from subprocess import call
from sys import platform, argv


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

SCRIPTS = ["src/bg_daemon/background_daemon.py"]

# only compile quack when none of these options are chosen
if (all([e not in argv for e in ['egg_info', 'sdist', 'register']]) and
    platform == 'darwin'):
    try:
        call(['make', '-C', 'src/bg_daemon/'])
        SCRIPTS.append("src/bg_daemon/quack")
    except OSError as e:
        print "Can't compile quack, reason {}".format(str(e))


setup(
    name="bg_daemon",
    version="0.0.1",
    author="Santiago Torres",
    author_email="torresariass@gmail.com",
    description=("An extensible set of classes that can programmatically "
                 "update the desktop wallpaper"),
    license="GPLv2",
    keywords="imgur desktop wallpaper background",
    url="https://github.com/santiagotorres/bg_daemon",
    packages=["bg_daemon", "bg_daemon.fetchers"],
    package_dir={"bg_daemon": "src/bg_daemon",
                 "bg_daemon.fetchers": "src/bg_daemon/fetchers"},
    scripts=SCRIPTS,
    include_package_data=True,
    data_files=[('bg_daemon', ['src/bg_daemon/settings.json',
                               'src/bg_daemon/mac-update.sh'])],
    long_description=read("README.md"),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: ",
        "Environment :: No Input/Output (Daemon)",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: Unix",
        "Topic :: Multimedia",
        ],
    install_requires=[
        "imgurpython",
        "requests",
        "python-crontab",
        "mock",
        ],
)
