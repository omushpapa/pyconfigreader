#! /usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import json
import os
import sys
import unittest
from collections import OrderedDict
from io import StringIO

from faker import Faker
from faker.providers import BaseProvider
from testfixtures import TempDirectory, compare

from pyconfigreader import ConfigReader
from pyconfigreader.exceptions import (ThresholdError, SectionNameNotAllowed,
                                       ModeError, MissingOptionError)

fake = Faker()


class ConfigProvider(BaseProvider):

    def config_file(self, path=None):
        filename = fake.file_name(extension='ini')
        if path is None:
            return filename

        return os.path.join(path, filename)


fake.add_provider(ConfigProvider)


class TestConfigReaderTestCase(unittest.TestCase):

    def setUp(self):
        self.tempdir = TempDirectory()
        self.file_path = os.path.join(self.tempdir.path, fake.config_file())

    def tearDown(self):
        self.tempdir.cleanup()

    def _get_config(self):
        file_path = self._get_config_file()
        config = ConfigReader(file_path)
        return config

    def _get_config_file(self):
        return fake.config_file(self.tempdir.path)

    def test_returns_false_if_key_not_set(self):
        file_path = self.tempdir.write(fake.config_file(), b'')
        with ConfigReader(file_path) as config:
            config.set('%name', '2')
            config.set('num%ber', '%23')

            with self.subTest(0):
                def raises_error():
                    config.set('attr', '%(num')

                self.assertRaises(ValueError, raises_error)

            with self.subTest(1):
                compare(config.get('%name'), 2)

            with self.subTest(2):
                compare(config.get('num%ber'), '%23')

    def test_returns_false_if_filename_not_absolute(self):
        with self.subTest(0):
            config = ConfigReader(self.file_path)
            self.assertTrue(os.path.isabs(config.filename))

        with self.subTest(1):
            config = ConfigReader()
            self.assertTrue(os.path.isabs(config.filename))

        with self.subTest(2):
            filename = os.path.join(
                os.getcwd(), 'settings.ini')
            config = ConfigReader()
            self.assertEqual(filename, config.filename)

        config.close()

        try:
            os.remove(config.filename)
        except FileNotFoundError:
            pass

    def test_returns_false_if_default_name_not_match(self):
        self.config = ConfigReader(self.file_path)
        expected = self.file_path
        self.assertEqual(self.config.filename, expected)
        self.config.close()

    def test_returns_false_if_name_not_changed(self):
        config = self._get_config()
        directory = fake.word()
        test_dir = self.tempdir.makedir(directory)
        path = os.path.join(test_dir, fake.config_file())
        config.filename = path
        self.assertEqual(config.filename, path)
        config.close()

    def test_returns_false_if_config_file_not_exists(self):
        self.config = ConfigReader(self.file_path)
        self.assertFalse(os.path.isfile(self.config.filename))
        self.config.close()

    def test_returns_false_if_config_file_exists(self):
        config = self._get_config()
        config.save()
        self.assertTrue(os.path.isfile(config.filename))
        config.close()

    def test_returns_false_if_sections_not_exists(self):
        config = self._get_config()
        config.set('Sample', 'Example', 'MainSection')
        config.set('Sample', 'Example', 'OtherSection')
        expected = ['MainSection', 'OtherSection', 'main']
        self.assertListEqual(
            sorted(config.sections), sorted(expected))
        config.close()

    def test_returns_false_if_section_not_removed(self):
        config = self._get_config()
        config.set('Sample', 'Example', 'MainSection')
        config.set('Sample', 'Example', 'OtherSection')
        config.remove_section('main')
        expected = ['MainSection', 'OtherSection']
        self.assertListEqual(
            sorted(config.sections), sorted(expected))
        config.close()

    def test_returns_false_if_key_not_removed(self):
        config = self._get_config()
        config.set('Sample', 'Example', 'MainSection')
        config.set('Sample', 'Example', 'OtherSection')
        config.remove_option('Sample', 'MainSection')

        with self.subTest(0), self.assertRaises(MissingOptionError):
            config.get('Sample', section='MainSection')

        with self.subTest(1):
            expected = ['MainSection', 'main', 'OtherSection']
            self.assertListEqual(sorted(
                config.sections), sorted(expected))
        config.close()

    def test_returns_false_if_dict_not_returned(self):
        config = self._get_config()
        config.set('Sample', 'Example', 'MainSection')
        config.set('Sample', 'Example', 'OtherSection')
        config.set('Name', 'File', 'OtherSection')
        self.assertIsInstance(
            config.show(output=False), dict)
        config.close()

    def test_returns_false_if_json_not_dumped(self):
        config = self._get_config()
        config.set('Sample', 'Example', 'MainSection')
        config.set('Sample', 'Example', 'OtherSection')
        config.set('name', 'File', 'OtherSection')
        config.remove_section('main')
        s_io = StringIO()
        config.to_json(s_io)
        s_io.seek(0)
        expected = s_io.read()

        self.assertEqual(config.to_json(), expected)
        config.close()

    def test_returns_false_if_json_file_not_created(self):
        config = self._get_config()
        directory = fake.word()
        test_dir = self.tempdir.makedir(directory)

        filename = os.path.join(test_dir, fake.file_name(extension='json'))
        with open(filename, 'w') as f:
            config.to_json(f)
        self.assertTrue(os.path.isfile(filename))
        config.close()

    def test_returns_false_if_defaults_are_changed(self):
        filename = self._get_config_file()

        with open(filename, "w") as config_file:
            config_file.write('[main]\nnewt = False\n')
            config_file.close()

        with ConfigReader(filename) as config:
            self.assertFalse(config.get('newt'))

    def test_returns_false_if_environment_variables_not_set(self):
        config = self._get_config()
        config.set('country', 'Kenya')
        config.set('continent', 'Africa')
        config.set('state', 'None')
        config.to_env()

        with self.subTest(0):
            self.assertEqual(os.environ['MAIN_COUNTRY'], 'Kenya')

        with self.subTest(1):
            self.assertEqual(os.environ['MAIN_CONTINENT'], 'Africa')

        with self.subTest(2):
            self.assertEqual(os.environ['MAIN_STATE'], 'None')
        config.close()

    def test_returns_false_if_section_prepend_failed(self):
        file_path_1 = self._get_config_file()
        file_path_2 = self._get_config_file()
        f = open(file_path_1, 'w+')
        config = ConfigReader(file_path_2, f)
        config.set('country', 'Kenya')
        config.set('continent', 'Africa')
        config.set('state', 'None')
        config.set('count', '0', section='first')
        config.to_env()
        f.close()

        with self.subTest(0):
            self.assertEqual(os.environ.get('MAIN_COUNTRY'), 'Kenya')

        with self.subTest(1):
            self.assertEqual(os.environ.get('MAIN_CONTINENT'), 'Africa')

        with self.subTest(2):
            self.assertEqual(os.environ.get('MAIN_STATE'), 'None')

        with self.subTest(3):
            self.assertEqual(os.environ.get('FIRST_COUNT'), '0')

    def test_returns_false_if_value_not_evaluated(self):
        config = self._get_config()
        config.set('truth', 'True')
        config.set('empty', '')
        config.set('count', '0', section='first')
        config.set('None', 'None', section='first')

        with self.subTest(0):
            self.assertTrue(config.get('truth'))

        with self.subTest(1):
            self.assertEqual(config.get('empty'), '')

        with self.subTest(2), self.assertRaises(MissingOptionError):
            config.get('count')

        with self.subTest(3):
            self.assertEqual(
                config.get('count', section='first'), 0)

        with self.subTest(4):
            self.assertIsNone(config.get('None', default='None'))
        config.close()

    def test_returns_false_if_exception_not_raised(self):
        config = self._get_config()

        def edit_sections():
            config.sections = ['new_section']

        self.assertRaises(AttributeError, edit_sections)
        config.close()

    def test_returns_false_if_threshold_error_not_raised(self):
        config = self._get_config()

        def do_search(threshold):
            config.search('read', threshold=threshold)

        with self.subTest(0):
            self.assertRaises(ThresholdError, do_search, 1.01)

        with self.subTest(1):
            self.assertRaises(ThresholdError, do_search, -1.0)
        config.close()

    def test_returns_false_if_match_not_found(self):
        file_path = self.tempdir.write(fake.config_file(), b'')
        with ConfigReader(file_path) as config:

            with self.subTest(0):
                self.assertEqual(config.get_items('main'), OrderedDict([('reader', 'configreader')]))

            with self.subTest(1):
                expected = ('reader', 'configreader', 'main')
                result = config.search('reader')
                self.assertIn(expected, result)

    def test_returns_false_if_match_not_found_2(self):
        file_path = self.tempdir.write(fake.config_file(), b'[main]')
        with ConfigReader(file_path) as config:
            with self.subTest(0):
                self.assertEqual(config.get_items('main'), OrderedDict([('reader', 'configreader')]))

            with self.subTest(1):
                expected = ('reader', 'configreader', 'main')
                result = config.search('reader')
                self.assertIn(expected, result)

    def test_returns_false_if_not_match_best(self):
        config = self._get_config()
        config.set('header', 'confreader')

        expected = (('reader', 'configreader', 'main'), ('header', 'confreader', 'main'))
        result = config.search('confgreader')

        for index, item in enumerate(expected):
            with self.subTest(index):
                self.assertIn(item, result)

        config.close()

    def test_returns_false_if_exact_match_not_found(self):
        config = self._get_config()
        config.set('title', 'The Place')

        expected = ('title', 'The Place', 'main')
        result = config.search('The Place', exact_match=True)
        self.assertEqual(result, expected)
        config.close()

    def test_returns_false_if_exact_match_found(self):
        config = self._get_config()
        config.set('title', 'The Place')

        result = config.search('The place', exact_match=True)
        self.assertEqual(result, None)
        config.close()

    def test_returns_false_if_exact_match_not_found_case_insensitive(self):
        config = self._get_config()
        config.set('title', 'The Place')

        expected = ('title', 'The Place', 'main')
        result = config.search('The place',
                               exact_match=True,
                               case_sensitive=False)
        self.assertEqual(result, expected)
        config.close()

    def test_returns_false_if_path_not_changed(self):
        file_path = self.tempdir.write(fake.config_file(), b'[main]')
        new_path = os.path.join(self.tempdir.path, fake.config_file())

        with open(file_path, 'w+') as f, ConfigReader(file_object=f) as config:
            with self.subTest(0):
                self.assertTrue(os.path.isfile(file_path))

            with self.subTest(1):
                self.assertFalse(os.path.isfile(new_path))

            config.filename = new_path

            with self.subTest(2):
                self.assertFalse(os.path.isfile(file_path))

            with self.subTest(3):
                self.assertFalse(os.path.isfile(new_path))

            config.save()

            with self.subTest(4):
                self.assertTrue(os.path.isfile(new_path))

    def test_returns_false_if_old_file_object_writable(self):
        file_path = self.tempdir.write(fake.config_file(), b'[main]')

        with open(file_path, 'w+') as f, ConfigReader(file_object=f) as config:
            new_path = os.path.join(
                os.path.expanduser('~'), fake.config_file()
            )

            config.filename = new_path

            self.assertRaises(ValueError, lambda: f.write(''))

    def test_returns_false_if_contents_not_similar(self):
        file_path = self.tempdir.write(fake.config_file(), b'[main]')
        new_path = os.path.join(self.tempdir.path, fake.config_file())

        with open(file_path, 'w+') as f, ConfigReader(file_object=f) as config:
            f.seek(0)
            expected = f.read()

            config.filename = new_path
            config.save()

            with open(new_path) as f2:
                result = f2.read()
            self.assertEqual(result, expected)

    def test_returns_false_if_file_object_cannot_update(self):
        f = open(self.file_path, 'w')

        self.assertRaises(ModeError, lambda: ConfigReader(file_object=f))
        f.close()

    def test_returns_false_if_contents_not_updated(self):
        f = open(self.file_path, 'w+')
        config = ConfigReader(file_object=f)
        config.set('name', 'first')

        with self.subTest(0):
            with open(self.file_path) as f2:
                result = f2.read()
            self.assertNotEqual(result, '')

        config.save()

        with self.subTest(1):
            with open(self.file_path) as f3:
                result = f3.read()
            self.assertNotEqual(result, '')
        f.close()

    def test_returns_false_if_file_object_and_filename_not_similar(self):
        with open(self.file_path, 'w+') as f:
            config = ConfigReader(file_object=f)
            self.assertEqual(config.filename, f.name)
            config.close()

    def test_returns_false_if_changes_not_written_to_file(self):
        file_path = fake.config_file(self.tempdir.path)
        config = ConfigReader(file_path)
        config.set('name', 'first')

        with ConfigReader(file_path) as d, self.subTest(0):
            with self.assertRaises(MissingOptionError):
                d.get('name')

        config.set('name', 'last', commit=True)
        config.close()

        d = ConfigReader(file_path)
        with self.subTest(1):
            self.assertEqual(d.get('name'), 'last')
        d.close()

    def test_returns_false_if_option_not_removed_from_file(self):
        config = self._get_config()
        config.set('name', 'first', section='two')

        with self.subTest(0):
            self.assertEqual(config.get('name', section='two'), 'first')

        config.remove_key('name', section='two', commit=True)

        with ConfigReader(self.file_path) as d, self.subTest(1), self.assertRaises(MissingOptionError):
            d.get('name', section='two')
        config.close()

    def test_returns_false_if_file_object_not_closed(self):
        config = self._get_config()
        config.close()

        self.assertRaises(AttributeError,
                          config.set, 'first', 'false')

    def test_returns_false_if_items_not_match(self):
        file_path_1 = self.tempdir.write(fake.config_file(), b'')
        file_path_2 = self.tempdir.write(fake.config_file(), b'')
        file_ = open(file_path_1, 'w+')

        config = ConfigReader(filename=file_path_2, file_object=file_)
        config.remove_section('main')
        config.set('start', 'True', section='defaults')
        config.set('value', '45', section='defaults')
        items = config.get_items('main')

        with self.subTest(0):
            self.assertIsNone(items)

        items = config.get_items('defaults')

        with self.subTest(1):
            self.assertIsInstance(items, OrderedDict)

        with self.subTest(2):
            expected = OrderedDict([
                ('start', True),
                ('value', 45)
            ])
            self.assertEqual(items, expected)
        config.close()

        with self.subTest('Test returns false if file object still writable'):
            self.assertRaises(ValueError, file_.write, '')

    def test_returns_false_if_error_not_raised(self):
        config = ConfigReader()

        with self.subTest(0):
            self.assertRaises(SectionNameNotAllowed,
                              lambda: config.set('start', 'True', section='default'))

        with self.subTest(1):
            self.assertRaises(SectionNameNotAllowed,
                              lambda: config.set('start', 'True', section='deFault'))

        with self.subTest(2):
            self.assertRaises(SectionNameNotAllowed,
                              lambda: config.set('start', 'True', section='DEFAULT'))

    def test_returns_false_if_object_not_context(self):
        with ConfigReader(self.file_path) as config:
            config.set('name', 'First', commit=True)
            name = config.get('name')

        self.assertEqual(name, 'First')

    @unittest.skipIf(os.name == 'nt', 'Path for *NIX systems')
    def test_returns_false_if_absolute_path_not_exist(self):
        path = '/home/path/does/not/exist'
        self.assertRaises(FileNotFoundError, ConfigReader, path)

    @unittest.skipIf(os.name != 'nt', 'Path for Windows systems')
    def test_returns_false_if_abs_path_not_exist(self):
        path = 'C:\\home\\path\\does\\not\\exist'
        self.assertRaises(FileNotFoundError, ConfigReader, path)

    def test_returns_false_if_default_not_returned(self):
        file_path = self.tempdir.write(fake.config_file(), b'')
        with ConfigReader(file_path) as config:
            value = config.get('members', default='10')

        self.assertEqual(value, 10)

    def test_returns_false_if_prepend_fails(self):
        file_path = self.tempdir.write(fake.config_file(), b'')
        with ConfigReader(file_path) as config:
            config.set('counter', 'default', section='team')
            config.set('play', '1', section='team')

        config.to_env()

        with self.subTest(0):
            self.assertEqual(os.environ['TEAM_COUNTER'], 'default')

        with self.subTest(1):
            self.assertEqual(os.environ['TEAM_PLAY'], '1')

        with self.subTest(2):
            self.assertRaises(KeyError, lambda: os.environ['PLAY'])

        config.to_env(prepend=False)

        with self.subTest(3):
            self.assertEqual(os.environ['PLAY'], '1')

        with self.subTest(4):
            self.assertEqual(os.environ['COUNTER'], 'default')

    @unittest.skipIf(os.name == 'nt', 'Testing environment variable for Windows')
    def test_returns_false_if_load_fails_linux(self):
        file_path = self.tempdir.write(fake.config_file(), b'')
        config = ConfigReader(file_path, case_sensitive=True)
        config.set('states', '35', section='country')
        config.set('counties', 'None', section='country')

        environment = os.environ.copy()
        user = 'guest'
        environment['USER'] = user
        environment['COUNTER'] = 'never'

        config.to_env(environment)
        config.load_env(environment)

        items = config.get_items('main')
        with self.subTest(0):
            self.assertEqual(items['HOME'], os.path.expanduser('~'))

        with self.subTest(1):
            self.assertEqual(items['USER'], user)

        with self.subTest(2):
            self.assertEqual(items['PWD'], os.environ['PWD'])

        with self.subTest(3):
            self.assertRaises(KeyError, lambda: items['home'])

        with self.subTest(4):
            self.assertEqual(items['COUNTER'], 'never')

    @unittest.skipIf(os.name == 'nt', 'Testing environment variable for Linux')
    def test_returns_false_if_load_fails_case_insensitive_linux(self):
        config = self._get_config()
        config.set('states', '35', section='country')
        config.set('counties', 'None', section='country')

        config.to_env()
        config.load_env()

        items = config.get_items('main')
        with self.subTest(0):
            self.assertEqual(items['home'], os.path.expanduser('~'))

        with self.subTest(1):
            self.assertEqual(items['user'], os.environ['USER'])

        with self.subTest(2):
            self.assertEqual(items['pwd'], os.environ['PWD'])

        with self.subTest(3):
            def call():
                return items['PWD']

            self.assertRaises(KeyError, call)

    @unittest.skipIf(os.name != 'nt', 'Testing environment variable for Windows')
    def test_returns_false_if_load_fails_windows(self):
        file_path = self.tempdir.write(fake.config_file(), b'')
        config = ConfigReader(file_path, case_sensitive=True)
        config.set('states', '35', section='country')
        config.set('counties', 'None', section='country')

        environment = os.environ.copy()
        user = 'guest'
        environment['USER'] = user
        environment['COUNTER'] = 'never'

        config.to_env(environment)
        config.load_env(environment)

        items = config.get_items('main')
        with self.subTest(0):
            self.assertEqual(items['APPDATA'], os.environ['APPDATA'])

        with self.subTest(1):
            self.assertEqual(items['USER'], user)

        with self.subTest(2):
            self.assertEqual(items['ALLUSERSPROFILE'], os.environ['ALLUSERSPROFILE'])

        with self.subTest(3):
            self.assertRaises(KeyError, lambda: items['home'])

        with self.subTest(4):
            self.assertEqual(items['COUNTER'], 'never')

    @unittest.skipIf(os.name != 'nt', 'Testing environment variable for Linux')
    def test_returns_false_if_load_fails_case_insensitive_windows(self):
        config = self._get_config()
        config.set('states', '35', section='country')
        config.set('counties', 'None', section='country')

        config.to_env()
        config.load_env()

        items = config.get_items('main')
        with self.subTest(0):
            self.assertEqual(items['appdata'], os.environ['APPDATA'])

        with self.subTest(1):
            self.assertEqual(items['allusersprofile'], os.environ['ALLUSERSPROFILE'])

        with self.subTest(2):
            self.assertEqual(items['homedrive'], os.environ['HOMEDRIVE'])

        with self.subTest(3):
            def call():
                return items['PWD']

            self.assertRaises(KeyError, call)

    def test_returns_false_if_load_prefixed_fails(self):
        config = self._get_config()
        config.set('states', '35', section='countrymain')
        config.set('counties', 'None', section='countrymain')

        config.to_env()
        config.remove_section('countrymain')
        with self.subTest(0):
            self.assertIsNone(config.get_items('countrymain'))
        config.load_env(prefix='countrymain')

        items = config.get_items('countrymain')
        with self.subTest(1):
            self.assertEqual(len(items), 2)

        with self.subTest(2):
            self.assertEqual(items['states'], 35)

        with self.subTest(3):
            self.assertIsNone(items['counties'])

    def test_returns_false_if_variable_not_expanded(self):
        config = self._get_config()
        config.set('path', 'drive')
        config.set('dir', '%(path)s-directory')
        config.set('suffix', 'dir-%(dir)s')

        with self.subTest(0):
            self.assertEqual(config.get('path'), 'drive')

        with self.subTest(1):
            self.assertEqual(config.get('dir'), 'drive-directory')

        with self.subTest(2):
            self.assertEqual(config.get('suffix'), 'dir-drive-directory')

    def test_returns_false_if_environment_variables_not_expanded(self):
        config = self._get_config()
        config.set('path', 'drive', section='test')
        config.set('dir', '%(path)s-directory', section='test')
        config.set('suffix', 'dir-%(dir)s', section='test')

        environment = os.environ.copy()
        config.to_env(environment)

        with self.subTest(0):
            self.assertEqual(environment['TEST_PATH'], 'drive')

        with self.subTest(1):
            self.assertEqual(environment['TEST_DIR'], 'drive-directory')

        with self.subTest(2):
            self.assertEqual(environment['TEST_SUFFIX'], 'dir-drive-directory')

    def test_returns_false_if_json_not_loaded_from_file(self):
        json_file = os.path.join(self.tempdir.path, fake.file_name(extension='json'))
        d = {
            'name': 'plannet',
            'count': 2,
            'skip': False,
            'handlers': [
                {
                    'name': 'handler_1'
                },
                {
                    'name': 'handler_2'
                }
            ],
            '@counters': {
                'start': {
                    'name': 'scrollers',
                    'count': 15
                },
                'mid': {
                    'name': 'followers',
                    'count': 0,
                    'helpers': 'available'
                },
                'end': {
                    'name': 'keepers',
                    'count': 5
                }
            }
        }

        try:
            j = open(json_file, 'w', encoding='utf-16')
        except TypeError:
            j = codecs.open(json_file, 'w', encoding='utf-16')
            json.dump(d, j, ensure_ascii=False)
        else:
            json.dump(d, j, ensure_ascii=False)

        j.close()

        config = self._get_config()
        config.load_json(json_file, section='json_data', encoding='utf-16')

        with self.subTest(0):
            compare(config.get('name', section='json_data'), 'plannet')

        with self.subTest(1):
            self.assertFalse(config.get('skip', section='json_data'))

        with self.subTest(2):
            self.assertIsInstance(config.get_items('counters'), OrderedDict)

        with self.subTest(3):
            compare(config.get_items('counters'),
                    OrderedDict([
                        ('start', {
                            'name': 'scrollers',
                            'count': 15
                        }),
                        ('mid', {
                            'name': 'followers',
                            'count': 0,
                            'helpers': 'available'
                        }),
                        ('end', {
                            'name': 'keepers',
                            'count': 5
                        })
                    ]))

    def test_returns_false_if_option_found(self):
        config = self._get_config()
        config.set('path', 'drive', section='test')

        with self.subTest(0):
            compare(config.get('path', 'test'), 'drive')

        with self.subTest(1), self.assertRaises(MissingOptionError):
            config.get('busy', section='test')

        config.close()

    def test_returns_false_if_option_with_default_found(self):
        config = self._get_config()
        config.set('path', 'drive', section='test')

        with self.subTest(0):
            compare(config.get('path', 'test'), 'drive')

        with self.subTest(1):
            compare(config.get('busy', section='test', default='not really'), 'not really')

        config.close()

    @unittest.skipIf(os.name == 'nt', 'Testing environment variables for Linux')
    def test_returns_false_if_environment_not_loaded_by_default_linux(self):
        file_path = self.tempdir.write(fake.config_file(), b'')
        with ConfigReader(file_path) as config:
            config.set('home', '$HOME')
            config.set('user', '$USER')

            with self.subTest(0):
                compare(config.get('home'), os.environ['HOME'])

            with self.subTest(1):
                compare(config.get('shell', default='$SHELL'), os.environ['SHELL'])

    @unittest.skipIf(os.name != 'nt', 'Testing environment variables for Windows')
    def test_returns_false_if_environment_not_loaded_by_default_windows(self):
        file_path = self.tempdir.write(fake.config_file(), b'')
        with ConfigReader(file_path) as config:
            config.set('app_data', '$APPDATA')

            with self.subTest(0):
                compare(config.get('app_data'), os.environ['APPDATA'])

            with self.subTest(1):
                compare(config.get('all_users_profile', default='$ALLUSERSPROFILE'), os.environ['ALLUSERSPROFILE'])

    def test_returns_false_if_reload_fails(self):
        file_path = self.tempdir.write(fake.config_file(),
                                       b'[main]\nreader = configreader\nmain = False\n')
        with ConfigReader(file_path) as config:

            with self.subTest(0):
                compare(config.get_items('main'), OrderedDict([('reader', 'configreader'),
                                                               ('main', False)]))

            config.set('found', 'True')

            with self.subTest(1):
                compare(config.get_items('main'), OrderedDict([('reader', 'configreader'),
                                                               ('main', False), ('found', True)]))

            config.reload()

            with self.subTest(2):
                compare(config.get_items('main'), OrderedDict([('reader', 'configreader'),
                                                               ('main', False)]))

    def test_returns_false_if_case_sensistivity_fails(self):
        file_path = self.tempdir.write(fake.config_file(), b'')
        with ConfigReader(file_path, case_sensitive=True) as config:
            config.set('NAME', 'cup')
            config.set('LEAGUE', '1')

            compare(config.get_items('main'), OrderedDict([('reader', 'configreader'),
                                                           ('NAME', 'cup'),
                                                           ('LEAGUE', 1)]))

    def test_returns_false_if_set_many_fails(self):
        file_path = self._get_config_file()
        config = ConfigReader(file_path)
        config.set_many({'name': 'one', 'number': '2'})

        with self.subTest('Test returns false if data not in default section'):
            self.assertListEqual([config.get('name'), config.get('number')],
                                 ['one', 2])

        config.reload()
        with self.subTest(), self.assertRaises(MissingOptionError):
            config.get('number')

        data = OrderedDict([('people', 'true'), ('count', 30)])
        config.set_many(data, section='demo')
        with self.subTest('Test returns false if data not in specified section'):
            self.assertDictEqual(config.get_items('demo'), data)

        config.close(save=True)
        with ConfigReader(file_path) as d, self.subTest():
            self.assertEqual(d.get('people', section='demo'), 'true')

    def test_returns_false_if_option_with_default_not_evaluated(self):
        config = self._get_config()

        with self.subTest(0):
            res = config.get('count', 'test', default=2)
            compare(res, 2)

        with self.subTest(1):
            compare(config.get('counter', 'test', default='20'), 20)

        config.close()

    def test_returns_false_if_option_with_string_default_not_evaluated(self):
        config = self._get_config()

        with self.subTest(0):
            compare(config.get('count', 'test', default='3'), 3)

        with self.subTest(1):
            compare(config.get('counter', 'test', default='20'), 20)

        config.close()


if __name__ == "__main__":
    unittest.main()
