#!/usr/bin/env python
"""
    bg_daemon.util

    This module's purpose is to serve as a centralized location for
    different constant and methods that don't fit anywhere else
"""
# for package-specific locations, change this value (your home folder might be
# ideal for this)
from pkg_resources import Requirement, resource_filename, resource_string
HOME = resource_filename("bg_daemon", "")
