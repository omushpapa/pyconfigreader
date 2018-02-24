#! /usr/bin/env python3


class ThresholdError(Exception):
    """Raised when the search threshold is not a float >=0.0 or <=1.0"""


class ModeError(Exception):
    """Raised when the opened file is not in mode w+"""
