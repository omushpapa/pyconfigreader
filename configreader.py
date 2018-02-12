#! /usr/bin/env python3

import os
import ast
import json
from difflib import SequenceMatcher
from configparser import (ConfigParser, NoSectionError,
                          NoOptionError, DuplicateSectionError)


def get_defaults(filename):
    """Returns a dictionary of the configuration properties"""
    configs = {}
    parser = ConfigParser()
    parser.read(filename)

    for section in parser.sections():
        configs[section] = {}
        options = parser.options(section)

        for option in options:
            value = parser.get(section, option)
            configs[section][option] = value
    return configs


class ConfigReader(object):
    """A simple configuration reader class for performing
    basic config file operations including reading, setting
    and searching for values"""

    __defaults = {
        'reader': 'configreader'
    }
    __default_section = 'main'

    def __init__(self, filename='settings.ini'):
        self.__parser = ConfigParser()
        self.__filename = self._set_filename(filename)
        self.__parser.read(filename)
        self._create_config()

    @property
    def sections(self):
        return self.__parser.sections()

    @sections.setter
    def sections(self, value):
        raise AttributeError("'Can't set attribute")

    @property
    def filename(self):
        return self.__filename

    @filename.setter
    def filename(self, value):
        old_name = self.__filename
        self.__filename = self._set_filename(value)
        os.rename(old_name, self.__filename)

    @staticmethod
    def _set_filename(value):
        if os.path.isabs(value):
            full_path = value
        else:
            full_path = os.path.join(os.path.abspath(
                os.path.dirname(__file__)), os.path.basename(value))
        return full_path

    def _add_section(self, section):
        try:
            self.__parser.add_section(section)
        except DuplicateSectionError:
            pass

    def _create_config(self):
        defaults = get_defaults(self.filename)
        self.__defaults.update(defaults)
        with open(self.filename, 'w') as config:
            for key in self.__defaults.keys():
                value = self.__defaults[key]
                if isinstance(value, dict):
                    self._add_section(key)

                    for item in value.keys():
                        self.set(key=item,
                                       value=value[item],
                                       section=key)
                else:
                    section = self.__default_section
                    self._add_section(section)
                    self.set(key, value, section)

            self.__parser.write(config)

    def get(self, key, section=None, evaluate=True, default=None):
        """Return the value of the provided key

        Returns None if the key does not exist.
        The section defaults to 'main' if not provided.
        If the value of the key does not exist and default is not None,
        the variable default is returned. In this case, providing
        section may be a good idea.

        If evaluate is True, the returned values are evaluated to
        Python data types int, float and boolean."""
        section = section or self.__default_section
        value = None
        try:
            value = self.__parser.get(section, option=key)
        except (NoSectionError, NoOptionError):
            if default is not None:
                value = default
                self.set(key, default, section)
        else:
            if evaluate:
                try:
                    value = ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    # ValueError when normal string
                    # SyntaxError when empty
                    pass
        return value

    def set(self, key, value, section=None):
        """Sets the value of key to the provided value

        Section defaults to 'main' is not provided.
        The section is created if it does not exist."""
        with open(self.filename, 'w') as config:
            section = section or self.__default_section
            self._add_section(section)
            self.__parser.set(section, option=key, value=str(value))
            self.__parser.write(config)

    def remove_section(self, section):
        """Remove a section from the configuration file
        whilst leaving the others intact"""
        parser = self.__parser
        with open(self.filename, 'r+') as f:
            parser.read_file(f)
            parser.remove_section(section)
            f.seek(0)
            parser.write(f)
            f.truncate()

    def remove_option(self, key, section=None):
        section = section or self.__default_section
        parser = self.__parser
        with open(self.filename, 'r+') as f:
            parser.read_file(f)
            parser.remove_option(section=section, option=key)
            f.seek(0)
            parser.write(f)
            f.truncate()

    def print(self, output=True):
        """Prints out all the sections and
        returns a dictionary of the same"""
        configs = {}
        string = '{:-^50}'.format(
            os.path.basename(self.filename))

        for section in self.sections:
            configs[section] = {}
            options = self.__parser.options(section)
            string += '\n{:^50}'.format(section)

            for option in options:
                value = self.get(option, section)
                configs[section][option] = value
                string += '\n{:>23}: {}'.format(option, value)

            string += '\n'

        string += '\n\n{:-^50}\n'.format('end')
        if output:
            print('\n\n{}'.format(string))
        return configs

    def search(self, value, case_sensitive=True,
               exact_match=False, threshold=0.36):
        """Returns a tuple containing the key, value and
        section if the value matches, else empty tuple

        If exact_match is True, checks if there exists a value
        that matches above the threshold value. In this case,
        case_sensitive is ignored.

        The threshold value should be 0, 1 or any value
        between 0 and 1. The higher the value the more the accuracy"""
        if not 0 <= threshold <= 1:
            raise AttributeError(
                'threshold must be 0, 1 or any value between 0 and 1')
        lowered_value = value.lower()
        result = ()
        for section in self.sections:
            options = self.__parser.options(section)

            for option in options:
                found = self.get(option, section)
                if exact_match:
                    if case_sensitive:
                        if value == found:
                            result = (option, found, section)
                            return result
                    else:
                        if lowered_value == found.lower():
                            result = (option, found, section)
                            return result
                else:
                    ratio = SequenceMatcher(None, found, value).ratio()
                    if ratio >= threshold:
                        result = (option, found, section)
                        return result

        return result

    def to_json(self, filename=None):
        """Export config to JSON

        If filename is given, it is exported to the file
        else returned as called"""
        config = self.print(output=False)
        if filename is None:
            return json.dumps(config)
        else:
            with open(filename, 'w') as f:
                json.dump(config, f)
