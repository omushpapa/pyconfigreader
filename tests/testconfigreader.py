#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import codecs
import unittest2 as unittest
from pyconfigreader import ConfigReader
from pyconfigreader.exceptions import (ThresholdError, SectionNameNotAllowed,
                                       ModeError, FileNotFoundError)
from uuid import uuid4
from testfixtures import TempDirectory, compare
from collections import OrderedDict

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser as ConfigParser

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class TestConfigReaderTestCase(unittest.TestCase):

    def setUp(self):
        self.tempdir = TempDirectory()
        self.tempdir.cleanup()
        self.tempdir = TempDirectory()
        self.file_path = os.path.join(self.tempdir.path, '{}.ini'.format(str(uuid4())))
        self.filename = os.path.basename(self.file_path)
        self.test_dir = self.tempdir.makedir('test_path')
        self.config_file = 'settings.ini'

    def tearDown(self):
        self.tempdir.cleanup()

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
        self.config = ConfigReader(self.file_path)
        path = os.path.join(self.test_dir, 'abc.ini')
        self.config.filename = path
        expected = path
        self.assertEqual(self.config.filename, expected)
        self.config.close()

    def test_returns_false_if_config_file_not_exists(self):
        self.config = ConfigReader(self.file_path)
        self.assertFalse(os.path.isfile(self.config.filename))
        self.config.close()

    def test_returns_false_if_config_file_exists(self):
        self.config = ConfigReader(self.file_path)
        self.config.save()
        self.assertTrue(os.path.isfile(self.config.filename))
        self.config.close()
        os.remove(self.config.filename)

    def test_returns_false_if_sections_not_exists(self):
        config = ConfigReader(self.file_path)
        config.set('Sample', 'Example', 'MainSection')
        config.set('Sample', 'Example', 'OtherSection')
        expected = ['MainSection', 'OtherSection', 'main']
        self.assertListEqual(
            sorted(config.sections), sorted(expected))
        config.close()

    def test_returns_false_if_section_not_removed(self):
        config = ConfigReader(self.file_path)
        config.set('Sample', 'Example', 'MainSection')
        config.set('Sample', 'Example', 'OtherSection')
        config.remove_section('main')
        expected = ['MainSection', 'OtherSection']
        self.assertListEqual(
            sorted(config.sections), sorted(expected))
        config.close()

    def test_returns_false_if_key_not_removed(self):
        config = ConfigReader(self.file_path)
        config.set('Sample', 'Example', 'MainSection')
        config.set('Sample', 'Example', 'OtherSection')
        config.remove_option('Sample', 'MainSection')

        with self.subTest(0):
            self.assertIsNone(config.get(
                'Sample', section='MainSection'))

        with self.subTest(1):
            expected = ['MainSection', 'main', 'OtherSection']
            self.assertListEqual(sorted(
                config.sections), sorted(expected))
        config.close()

    def test_returns_false_if_dict_not_returned(self):
        self.config = ConfigReader(self.file_path)
        self.config.set('Sample', 'Example', 'MainSection')
        self.config.set('Sample', 'Example', 'OtherSection')
        self.config.set('Name', 'File', 'OtherSection')
        self.assertIsInstance(
            self.config.show(output=False), dict)
        self.config.close()

    def test_returns_false_if_key_exists(self):
        self.config = ConfigReader(self.file_path)
        self.assertIsNone(self.config.get('Sample'))
        self.config.close()

    def test_returns_false_if_json_not_dumped(self):
        self.config = ConfigReader(self.file_path)
        self.config.set('Sample', 'Example', 'MainSection')
        self.config.set('Sample', 'Example', 'OtherSection')
        self.config.set('name', 'File', 'OtherSection')
        self.config.remove_section('main')
        s_io = StringIO()
        self.config.to_json(s_io)
        s_io.seek(0)
        expected = s_io.read()

        self.assertEqual(self.config.to_json(), expected)
        self.config.close()

    def test_returns_false_if_json_file_not_created(self):
        self.config = ConfigReader(self.file_path)

        filename = os.path.join(self.test_dir, 'abc.json')
        with open(filename, 'w') as f:
            self.config.to_json(f)
        self.assertTrue(os.path.isfile(filename))
        self.config.close()

    def test_returns_false_if_defaults_are_changed(self):
        filename = os.path.join(os.path.expanduser('~'), 'settings.ini')

        config_file = open(filename, "w")
        config_file.write('[main]\nnew = False\n')
        config_file.close()

        with ConfigReader(filename) as config:
            self.assertFalse(config.get('new'))

        os.remove(filename)

    def test_returns_false_if_environment_variables_not_set(self):
        self.config = ConfigReader(self.file_path)
        self.config.set('country', 'Kenya')
        self.config.set('continent', 'Africa')
        self.config.set('state', None)
        self.config.to_env()

        with self.subTest(0):
            self.assertEqual(os.environ['MAIN_COUNTRY'], 'Kenya')

        with self.subTest(1):
            self.assertEqual(os.environ['MAIN_CONTINENT'], 'Africa')

        with self.subTest(2):
            self.assertEqual(os.environ['MAIN_STATE'], 'None')
        self.config.close()

    def test_returns_false_if_section_prepend_failed(self):
        f = open('default.ini', 'w+')
        config = ConfigReader(self.file_path, f)
        config.set('country', 'Kenya')
        config.set('continent', 'Africa')
        config.set('state', None)
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
        config = ConfigReader(self.file_path)
        config.set('truth', 'True')
        config.set('empty', '')
        config.set('count', '0', section='first')
        config.set('None', 'None', section='first')

        with self.subTest(0):
            self.assertTrue(config.get('truth'))

        with self.subTest(1):
            self.assertEqual(config.get('empty'), '')

        with self.subTest(2):
            self.assertIsNone(config.get('count'))

        with self.subTest(3):
            self.assertEqual(
                config.get('count', section='first'), 0)

        with self.subTest(4):
            self.assertIsNone(config.get('None'))
        config.close()

    def test_returns_false_if_exception_not_raised(self):
        config = ConfigReader(self.file_path)

        def edit_sections():
            config.sections = ['new_section']

        self.assertRaises(AttributeError, edit_sections)
        config.close()

    def test_returns_false_if_threshold_error_not_raised(self):
        config = ConfigReader(self.file_path)

        def do_search(threshold):
            config.search('read', threshold=threshold)

        with self.subTest(0):
            self.assertRaises(ThresholdError, do_search, 1.01)

        with self.subTest(1):
            self.assertRaises(ThresholdError, do_search, -1.0)
        config.close()

    def test_returns_false_if_match_not_found(self):
        config = ConfigReader(self.file_path)
        expected = ('reader', 'configreader', 'main')
        result = config.search('reader')
        self.assertEqual(result, expected)
        config.close()

    def test_returns_false_if_not_match_best(self):
        config = ConfigReader(self.file_path)
        config.set('header', 'confreader')

        expected = ('reader', 'configreader', 'main')
        result = config.search('confgreader')
        self.assertEqual(result, expected)
        config.close()

    def test_returns_false_if_exact_match_not_found(self):
        config = ConfigReader(self.file_path)
        config.set('title', 'The Place')

        expected = ('title', 'The Place', 'main')
        result = config.search('The Place', exact_match=True)
        self.assertEqual(result, expected)
        config.close()

    def test_returns_false_if_exact_match_found(self):
        config = ConfigReader(self.file_path)
        config.set('title', 'The Place')

        expected = ()
        result = config.search('The place', exact_match=True)
        self.assertEqual(result, expected)
        config.close()

    def test_returns_false_if_exact_match_not_found_case_insensitive(self):
        config = ConfigReader(self.file_path)
        config.set('title', 'The Place')

        expected = ('title', 'The Place', 'main')
        result = config.search('The place',
                               exact_match=True,
                               case_sensitive=False)
        self.assertEqual(result, expected)
        config.close()

    def test_returns_false_if_path_not_changed(self):
        f = open(self.file_path, 'w+')
        config = ConfigReader(file_object=f)
        new_path = os.path.join(
            os.path.expanduser('~'), '{}.ini'.format(str(uuid4()))
        )

        with self.subTest(0):
            self.assertFalse(os.path.isfile(new_path))

        config.filename = new_path

        with self.subTest(1):
            self.assertFalse(os.path.isfile(self.file_path))

        with self.subTest(2):
            self.assertFalse(os.path.isfile(new_path))

        config.save()

        with self.subTest(3):
            self.assertTrue(os.path.isfile(new_path))
        config.close()
        try:
            os.remove(new_path)
        except FileNotFoundError:
            pass

    def test_returns_false_if_old_file_object_writable(self):
        f = open(self.file_path, 'w+')
        config = ConfigReader(file_object=f)
        new_path = os.path.join(
            os.path.expanduser('~'), '{}.ini'.format(str(uuid4()))
        )

        config.filename = new_path

        self.assertRaises(ValueError, lambda: f.write(''))
        config.close()
        try:
            os.remove(new_path)
        except FileNotFoundError:
            pass

    def test_returns_false_if_contents_not_similar(self):
        f = open(self.file_path, 'w+')
        config = ConfigReader(file_object=f)
        new_path = os.path.join(
            os.path.expanduser('~'), '{}.ini'.format(str(uuid4()))
        )

        f.seek(0)
        expected = f.read()

        config.filename = new_path
        config.save()

        with open(new_path) as f2:
            result = f2.read()
        self.assertEqual(result, expected)
        config.close()
        try:
            os.remove(new_path)
        except FileNotFoundError:
            pass

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
        config = ConfigReader(self.file_path)
        config.set('name', 'first')

        d = ConfigReader(self.file_path)
        with self.subTest(0):
            self.assertIsNone(d.get('name'))
        config.set('name', 'last', commit=True)
        config.close()

        d = ConfigReader(self.file_path)
        with self.subTest(1):
            self.assertEqual(d.get('name'), 'last')
        d.close()

    def test_returns_false_if_option_not_removed_from_file(self):
        config = ConfigReader(
            os.path.join(self.tempdir.path, '{}.ini'.format(str(uuid4()))))
        config.set('name', 'first', section='two')

        with self.subTest(0):
            self.assertEqual(config.get('name', section='two'), 'first')

        config.remove_key('name', section='two', commit=True)

        d = ConfigReader(self.file_path)
        with self.subTest(1):
            self.assertIsNone(d.get('name', section='two'))
        config.close()
        d.close()

    def test_returns_false_if_file_object_not_closed(self):
        config = ConfigReader(self.file_path)
        config.close()

        self.assertRaises(AttributeError,
                          lambda: config.set('first', 'false'))

    def test_returns_false_if_items_not_match(self):
        file_path = self.tempdir.write('{}.ini'.format(str(uuid4())), b'')
        file_ = open(file_path, 'w+')

        config = ConfigReader(filename='defaults.ini', file_object=file_)
        config.remove_section('main')
        config.set('start', 'True', section='defaults')
        config.set('value', '45', section='defaults')
        items = config.get_items('main')

        with self.subTest(0):
            self.assertIsNone(items)

        items = config.get_items('defaults')

        with self.subTest(0):
            self.assertIsInstance(items, OrderedDict)

        with self.subTest(1):
            expected = OrderedDict([
                ('start', True),
                ('value', 45)
            ])
            self.assertEqual(items, expected)
        config.close()

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

        def call():
            c = ConfigReader(path)

        self.assertRaises(FileNotFoundError, call)

    @unittest.skipIf(os.name != 'nt', 'Path for Windows systems')
    def test_returns_false_if_abs_path_not_exist(self):
        path = 'C:\\home\\path\\does\\not\\exist'

        def call():
            c = ConfigReader(path)

        self.assertRaises(FileNotFoundError, call)

    def test_returns_false_if_default_not_returned(self):
        file_path = self.tempdir.write('{}.ini'.format(str(uuid4())), b'')
        with ConfigReader(file_path) as config:
            value = config.get('members', default='10')

        self.assertEqual(value, 10)

    def test_returns_false_if_prepend_fails(self):
        file_path = self.tempdir.write('{}.ini'.format(str(uuid4())), b'')
        with ConfigReader(file_path) as config:
            config.set('counter', 'default', section='team')
            config.set('play', '1', section='team')

        config.to_env()

        with self.subTest(0):
            self.assertEqual(os.environ['TEAM_COUNTER'], 'default')

        with self.subTest(1):
            self.assertEqual(os.environ['TEAM_PLAY'], '1')

        with self.subTest(2):
            def call():
                return os.environ['PLAY']

            self.assertRaises(KeyError, call)

        config.to_env(prepend=False)

        with self.subTest(3):
            self.assertEqual(os.environ['PLAY'], '1')

        with self.subTest(4):
            self.assertEqual(os.environ['COUNTER'], 'default')

    def test_returns_false_if_load_fails(self):
        file_path = self.tempdir.write('{}.ini'.format(str(uuid4())), b'')
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
            def call():
                return items['home']

            self.assertRaises(KeyError, call)

        with self.subTest(4):
            self.assertEqual(items['COUNTER'], 'never')

    def test_returns_false_if_load_fails_case_insensitive(self):
        file_path = self.tempdir.write('{}.ini'.format(str(uuid4())), b'')
        config = ConfigReader(file_path)
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

    def test_returns_false_if_load_prefixed_fails(self):
        file_path = self.tempdir.write('{}.ini'.format(str(uuid4())), b'')
        config = ConfigReader(file_path)
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
        file_path = self.tempdir.write('{}.ini'.format(str(uuid4())), b'')
        config = ConfigReader(file_path)
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
        file_path = self.tempdir.write('{}.ini'.format(str(uuid4())), b'')
        config = ConfigReader(file_path)
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
        file_path = os.path.join(self.tempdir.path, '{}.ini'.format(str(uuid4())))
        json_file = os.path.join(self.tempdir.path, '{}.ini'.format(str(uuid4())))
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
        finally:
            j.close()

        config = ConfigReader(file_path)
        config.load_json(json_file, section='json_data', encoding='utf-16')

        with self.subTest(0):
            compare(config.get('name', section='json_data'), 'plannet')

        with self.subTest(1):
            self.assertFalse(config.get('skip', section='json_file'))

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


if __name__ == "__main__":
    unittest.main()
