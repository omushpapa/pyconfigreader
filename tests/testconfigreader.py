#! /usr/bin/env python3

import os
import unittest
from configparser import ConfigParser
from io import StringIO
from configreader import ConfigReader
from uuid import uuid4
from testfixtures import TempDirectory


class TestConfigReaderTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tempdir = TempDirectory()
        cls.file_path = cls.tempdir.write(str(uuid4()), b'')
        cls.filename = os.path.basename(cls.file_path)
        cls.test_dir = cls.tempdir.makedir('test_path')
        cls.config_file = 'settings.ini'

    @classmethod
    def tearDownClass(cls):
        cls.tempdir.cleanup()

    def setUp(self):
        self.config = ConfigReader(self.file_path)

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
        self.assertTrue(os.path.isfile(self.config.filename))

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
            self.config.print(output=False), dict)

    def test_returns_false_if_key_exists(self):
        self.config = ConfigReader(self.file_path)
        self.assertIsNone(self.config.get('Sample'))

    def test_returns_false_if_json_not_dumped(self):
        self.config = ConfigReader(self.file_path)
        self.config.set('Sample', 'Example', 'MainSection')
        self.config.set('Sample', 'Example', 'OtherSection')
        self.config.set('name', 'File', 'OtherSection')
        self.config.remove_section('main')
        in_dict = {
            'MainSection': {
                'sample': 'Example'
            },
            'OtherSection': {
                'sample': 'Example',
                'name': 'File'
            }
        }
        s_io = StringIO()
        self.config.to_json(s_io)
        s_io.seek(0)
        expected = s_io.read()

        with self.subTest(0):
            self.assertTrue(os.path.isfile(self.config.filename))
        with self.subTest(1):
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


if __name__ == "__main__":
    unittest.main()
