#! /usr/bin/env python3
# -*- coding: utf-8 -*-


class ThresholdError(Exception):
    """Raised when the search threshold is not a float >=0.0 or <=1.0"""


class ModeError(Exception):
    """Raised when the opened file is not in mode w+"""


class SectionNameNotAllowed(Exception):
    """Raised when a section of default variant is attempted to be created."""


try:
    FileNotFoundError = FileNotFoundError
except NameError:
    FileNotFoundError = OSError
