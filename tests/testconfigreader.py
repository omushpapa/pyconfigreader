#! /usr/bin/env python3

import os
import unittest
from configparser import ConfigParser
from io import StringIO
from pyconfigreader import ConfigReader
from pyconfigreader.exceptions import ThresholdError, ModeError
from uuid import uuid4
from testfixtures import TempDirectory


class TestConfigReaderTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tempdir = TempDirectory()
        cls.file_path = os.path.join(cls.tempdir.path, '{}.ini'.format(str(uuid4())))
        cls.filename = os.path.basename(cls.file_path)
        cls.test_dir = cls.tempdir.makedir('test_path')
        cls.config_file = 'settings.ini'

    @classmethod
    def tearDownClass(cls):
        cls.tempdir.cleanup()

    def setUp(self):
        self.config = ConfigReader(self.file_path)

    def test_returns_false_if_filename_not_absolute(self):
        with self.subTest(0):
            config = ConfigReader(self.file_path)
            self.assertTrue(os.path.isabs(config.filename))

        with self.subTest(1):
            config = ConfigReader()
            self.assertTrue(os.path.isabs(config.filename))

    def test_returns_false_if_default_name_not_match(self):
        expected = self.file_path
        self.assertEqual(self.config.filename, expected)

    def test_returns_false_if_name_not_changed(self):
        self.config = ConfigReader(self.file_path)
        path = os.path.join(self.test_dir, 'abc.ini')
        self.config.filename = path
        expected = path
        self.assertEqual(self.config.filename, expected)

    def test_returns_false_if_config_file_not_exists(self):
        self.config = ConfigReader(self.file_path)
        self.assertFalse(os.path.isfile(self.config.filename))

    def test_returns_false_if_config_file_exists(self):
        self.config = ConfigReader(self.file_path)
        self.config.to_file()
        self.assertTrue(os.path.isfile(self.config.filename))
        os.remove(self.config.filename)

    def test_returns_false_if_sections_not_exists(self):
        self.config = ConfigReader(self.file_path)
        self.config.set('Sample', 'Example', 'MainSection')
        self.config.set('Sample', 'Example', 'OtherSection')
        expected = ['MainSection', 'OtherSection', 'main']
        self.assertListEqual(
            sorted(self.config.sections), sorted(expected))

    def test_returns_false_if_section_not_removed(self):
        self.config = ConfigReader(self.file_path)
        self.config.set('Sample', 'Example', 'MainSection')
        self.config.set('Sample', 'Example', 'OtherSection')
        self.config.remove_section('main')
        expected = ['MainSection', 'OtherSection']
        self.assertListEqual(
            sorted(self.config.sections), sorted(expected))

    def test_returns_false_if_key_not_removed(self):
        self.config = ConfigReader(self.file_path)
        self.config.set('Sample', 'Example', 'MainSection')
        self.config.set('Sample', 'Example', 'OtherSection')
        self.config.remove_option('Sample', 'MainSection')

        with self.subTest(0):
            self.assertIsNone(self.config.get(
                'Sample', section='MainSection'))

        with self.subTest(1):
            expected = ['MainSection', 'main', 'OtherSection']
            self.assertListEqual(sorted(
                self.config.sections), sorted(expected))

    def test_returns_false_if_dict_not_returned(self):
        self.config = ConfigReader(self.file_path)
        self.config.set('Sample', 'Example', 'MainSection')
        self.config.set('Sample', 'Example', 'OtherSection')
        self.config.set('Name', 'File', 'OtherSection')
        expected = {
            'main': {
                'reader': 'configreader'
            },
            'MainSection': {
                'sample': 'Example'
            },
            'OtherSection': {
                'sample': 'Example',
                'name': 'File'
            }
        }
        self.assertIsInstance(
            self.config.show(output=False), dict)

    def test_returns_false_if_key_exists(self):
        self.config = ConfigReader(self.file_path)
        self.assertIsNone(self.config.get('Sample'))

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

    def test_returns_false_if_json_file_not_created(self):
        self.config = ConfigReader(self.file_path)

        filename = os.path.join(self.test_dir, 'abc.json')
        with open(filename, 'w') as f:
            self.config.to_json(f)
        self.assertTrue(os.path.isfile(filename))

    def test_returns_false_if_defaults_are_changed(self):
        dr = ConfigParser()
        dr.add_section('main')
        dr.add_section('MainSection')
        dr.set('main', 'new', 'False')
        dr.set('MainSection', 'browser', 'default')
        dr.set('MainSection', 'header', 'False')

        with open(self.file_path, "w") as config_file:
            dr.write(config_file)

        self.config = ConfigReader(self.file_path)
        self.config.set('browser', 'default', 'MainSection')

        with self.subTest(0):
            result = self.config.get('new')
            self.assertFalse(result)

        with self.subTest(1):
            expected = 'default'
            self.assertEqual(
                self.config.get('browser', section='MainSection'), expected)

        with self.subTest(2):
            self.assertIsNone(self.config.get('browser'))

        with self.subTest(3):
            expected = 'Not set'
            self.assertEqual(
                self.config.get('default', default='Not set'), expected)

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

    def test_returns_false_if_exception_not_raised(self):
        config = ConfigReader(self.file_path)

        def edit_sections():
            config.sections = ['new_section']
        self.assertRaises(AttributeError, edit_sections)

    def test_returns_false_if_threshold_error_not_raised(self):
        config = ConfigReader(self.file_path)

        def do_search(threshold):
            config.search('read', threshold=threshold)

        with self.subTest(0):
            self.assertRaises(ThresholdError, do_search, 1.01)

        with self.subTest(1):
            self.assertRaises(ThresholdError, do_search, -1.0)

    def test_returns_false_if_match_not_found(self):
        config = ConfigReader(self.file_path)
        expected = ('reader', 'configreader', 'main')
        result = config.search('reader')
        self.assertEqual(result, expected)

    def test_returns_false_if_not_match_best(self):
        config = ConfigReader(self.file_path)
        config.set('header', 'confreader')

        expected = ('reader', 'configreader', 'main')
        result = config.search('confgreader')
        self.assertEqual(result, expected)

    def test_returns_false_if_exact_match_not_found(self):
        config = ConfigReader(self.file_path)
        config.set('title', 'The Place')

        expected = ('title', 'The Place', 'main')
        result = config.search('The Place', exact_match=True)
        self.assertEqual(result, expected)

    def test_returns_false_if_exact_match_found(self):
        config = ConfigReader(self.file_path)
        config.set('title', 'The Place')

        expected = ()
        result = config.search('The place', exact_match=True)
        self.assertEqual(result, expected)

    def test_returns_false_if_exact_match_not_found_case_insensitive(self):
        config = ConfigReader(self.file_path)
        config.set('title', 'The Place')

        expected = ('title', 'The Place', 'main')
        result = config.search('The place',
                               exact_match=True,
                               case_sensitive=False)
        self.assertEqual(result, expected)

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

        config.to_file()

        with self.subTest(3):
            self.assertTrue(os.path.isfile(new_path))

        #with self.subTest(4):
        #    self.assertRaises(ValueError, f.readable())

    def test_returns_false_if_contents_not_similar(self):
        f = open(self.file_path, 'w+')
        config = ConfigReader(file_object=f)
        new_path = os.path.join(
            os.path.expanduser('~'), '{}.ini'.format(str(uuid4()))
        )

        f.seek(0)
        expected = f.read()

        config.filename = new_path
        config.to_file()

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

        config.to_file()

        with self.subTest(1):
            with open(self.file_path) as f3:
                result = f3.read()
            self.assertNotEqual(result, '')
        f.close()

    def test_returns_false_if_file_object_and_filename_not_similar(self):
        with open(self.file_path, 'w+') as f:
            config = ConfigReader(file_object=f)
            self.assertEqual(config.filename, f.name)


if __name__ == "__main__":
    unittest.main()
