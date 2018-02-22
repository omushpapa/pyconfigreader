#! /usr/bin/env python3

import os
import ast
import json
import shutil
from difflib import SequenceMatcher
from configparser import (ConfigParser, NoSectionError,
                          NoOptionError, DuplicateSectionError)
from io import StringIO


def get_defaults(filename):
    """Returns a dictionary of the configuration properties

    :param filename: the name of an existing ini file
    :type filename: str
    :returns: sections, keys and options read from the file
    :rtype: dict
    """
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
    and searching for values

    :param filename: The name of the final config file
    :param file_object: A file-like object
    :type filename: str
    :type file_object: io.TextIO or io.StringIO
    """

    __defaults = {
        'reader': 'configreader'
    }
    __default_section = 'main'

    def __init__(self, filename='settings.ini', file_object=StringIO()):
        self.__parser = ConfigParser()
        self.__filename = self._set_filename(filename)
        self.__file_object = file_object
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
        self.__filename = self._set_filename(value)
        if not isinstance(self.__file_object, StringIO):
            self.__file_object.close()
            self.__file_object = open(self.__filename, 'w')

    @staticmethod
    def _set_filename(value):
        """Set the file name provided to a full path

        :param value: The new file name or path
        :type value: str
        :returns: the full path of the file
        :rtype: str
        """
        if os.path.isabs(value):
            full_path = value
        else:
            full_path = os.path.join(os.path.abspath(
                os.path.dirname(__file__)), os.path.basename(value))
        return full_path

    def _add_section(self, section):
        """Add a section to the ini file if it doesn't exist

        :param section: The name of the section
        :type section: str
        :returns: Nothing
        :rtype: None
        """
        try:
            self.__parser.add_section(section)
        except DuplicateSectionError:
            pass

    def _write_config(self):
        """Write to the file-like object

        :returns: Nothing
        :rtype: None
        """
        self.__parser.write(self.__file_object)

    def _create_config(self):
        """Initialise an ini file from the defaults provided

        This does not write the file to disk. It only reads
        from disk if a file with the same name exists.

        :returns: Nothing
        :rtype: None
        """
        defaults = get_defaults(self.filename)
        self.__defaults.update(defaults)

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

        self._write_config()

    def get(self, key, section=None, evaluate=True, default=None):
        """Return the value of the provided key

        Returns None if the key does not exist.
        The section defaults to 'main' if not provided.
        If the value of the key does not exist and default is not None,
        the variable default is returned. In this case, providing
        section may be a good idea.

        If evaluate is True, the returned values are evaluated to
        Python data types int, float and boolean.

        :param key: The key name
        :param section: The name of the section, defaults to 'main'
        :param evaluate: Determines whether to evaluate the acquired values into Python literals
        :param default: The value to return if the key is not found
        :type key: str
        :type section: str
        :type evaluate: bool
        :type default: str
        :returns: The value that is mapped to the key
        :rtype: str, int, float, bool or None
        """
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
        The section is created if it does not exist.

        :param key: The key name
        :param value: The value to which the key is mapped
        :param section: The name of the section, defaults to 'main'
        :type key: str
        :type value: str
        :type section: str
        :returns: Nothing
        :rtype: None
        """
        section = section or self.__default_section
        self._add_section(section)
        self.__parser.set(section, option=key, value=str(value))
        self._write_config()

    def remove_section(self, section):
        """Remove a section from the configuration file
        whilst leaving the others intact

        :param section: The name of the section to remove
        :type section: str
        :returns: Nothing
        :rtype: None
        """
        self.__parser.read_file(self.__file_object)
        self.__parser.remove_section(section)
        self.__file_object.seek(0)
        self.__parser.write(self.__file_object)
        self.__file_object.truncate()

    def remove_option(self, key, section=None):
        """Remove an option from the configuration file

        :param key: The key name
        :param section: The section name, defaults to 'main'
        :type key: str
        :type section: str
        :returns: Nothing
        :rtype: None
        """
        section = section or self.__default_section
        self.__parser.read_file(self.__file_object)
        self.__parser.remove_option(section=section, option=key)
        self.__file_object.seek(0)
        self.__parser.write(self.__file_object)
        self.__file_object.truncate()

    def print(self, output=True):
        """Prints out all the sections and
        returns a dictionary of the same

        :param output: Print to std.out a string representation of the file contents, defaults to True
        :type output: bool
        :returns: A dictionary mapping of sections, options and values
        :rtype: dict
        """
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
        between 0 and 1. The higher the value the more the accuracy

        :param value: The value to search for in the config file
        :param case_sensitive: Match case during search or not
        :param exact_match: Match exact value
        :param threshold: The value of matching at which a match can be considered as satisfactory
        :type value: str
        :type case_sensitive: bool
        :type exact_match: bool
        :type threshold: float
        :returns: A tuple of the option, value and section
        :rtype: tuple
        """
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

    def to_json(self, file_object=None):
        """Export config to JSON

        If a file_object is given, it is exported to it
        else returned as called

        Example
        -------
        >>> reader = ConfigReader()
        >>> with open('abc.ini', 'w') as f:
        >>>    reader.to_json(f)

        or:

        >>> from io import StringIO
        >>> s_io = StringIO()
        >>> reader.to_json(s_io)

        :param file_object: A file-like object for the JSON content
        :type file_object: io.TextIO
        :returns: A string or the dumped JSON contents or nothing if file_object is provided
        :rtype: str or None
        """
        config = self.print(output=False)
        if file_object is None:
            return json.dumps(config)
        else:
            json.dump(config, file_object)

    def to_env(self, environment=os.environ):
        """Export contents to an environment

        Exports by default to os.environ.

        By default, the section and option would be capitalised
        and joined by an underscore to form the key - as an
        attempt at avoid collision with environment variables.

        Example
        -------
        >>> reader = ConfigReader()
        >>> reader.print(output=False)
          {'main': {'reader': 'configreader'}}
        >>> reader.to_env()
        >>> import os
        >>> os.environ['MAIN_READER']
          'configreader'

        :param environment: An environment to export to
        :type environment: os.environ
        :returns: Nothing
        :rtype: None
        """
        data = self.print(False)

        for section in data:
            items = data[section]

            for item in items:
                env_key = '{}_{}'.format(
                    section.upper(), item.upper())
                environment[env_key] = str(items[item])

    def to_file(self):
        """Write to file on disk

        Write the contents to a file on the disk.

        :returns: Nothing
        :rtype: None
        """
        if isinstance(self.__file_object, StringIO):
            with open(self.filename, 'w') as config_file:
                self.__file_object.seek(0)
                shutil.copyfileobj(self.__file_object, config_file)
        else:
            self.__file_object.flush()
            os.fsync(self.__file_object.fileno())
