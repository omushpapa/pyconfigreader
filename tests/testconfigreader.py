#! /usr/bin/env python3

import json
import unittest
import os
from testfixtures import compare
from configreader import ConfigReader
from uuid import uuid4
from testfixtures import TempDirectory


def create_file(func):
    def _decorator(self, *args, **kwargs):
        self.config_path = self.tempdir.write(
            '{}.ini'.format(str(uuid4())), b'')
        return func(self, *args, **kwargs)
    return _decorator


class TestConfigReaderTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tempdir = TempDirectory()
        cls.test_dir = cls.tempdir.makedir('test_path')
        cls.config_file = 'settings.ini'

    @classmethod
    def tearDownClass(cls):
        cls.tempdir.cleanup()

    @create_file
    def test_returns_false_if_default_name_not_match(self):
        c = ConfigReader(self.config_path)
        expected = self.config_path
        compare(c.filename, expected)

    @create_file
    def test_compare_config_path(self):
        c = ConfigReader(self.config_path)
        expected = self.config_path
        compare(c.filename, expected)

    @create_file
    def test_returns_false_if_name_not_changed(self):
        c = ConfigReader(self.config_path)
        c.filename = os.path.join(self.test_dir, 'abc.ini')
        expected = os.path.join(self.test_dir, 'abc.ini')
        compare(c.filename, expected)
        os.remove(expected)

    @create_file
    def test_returns_false_if_config_file_not_exists(self):
        c = ConfigReader(self.config_path)
        expected = True
        compare(os.path.isfile(c.filename), expected)

    @create_file
    def test_returns_false_if_sections_not_exists(self):
        c = ConfigReader(self.config_path)
        c.set('Sample', 'Example', 'MainSection')
        c.set('Sample', 'Example', 'OtherSection')
        expected = ['MainSection', 'OtherSection', 'main']
        compare(sorted(c.sections), sorted(expected))

    @create_file
    def test_returns_false_if_section_not_removed(self):
        c = ConfigReader(self.config_path)
        c.set('Sample', 'Example', 'MainSection')
        c.set('Sample', 'Example', 'OtherSection')
        c.remove_section('main')
        expected = ['MainSection', 'OtherSection']
        compare(sorted(c.sections), sorted(expected))

    @create_file
    def test_returns_false_if_key_not_removed(self):
        c = ConfigReader(self.config_path)
        c.set('Sample', 'Example', 'MainSection')
        c.set('Sample', 'Example', 'OtherSection')
        c.remove_option('Sample', 'MainSection')
        expected = None
        with self.subTest(0):
            compare(c.get('Sample', section='MainSection'), expected)
        with self.subTest(1):
            expected = ['MainSection', 'main', 'OtherSection']
            compare(sorted(c.sections), sorted(expected))

    @create_file
    def test_returns_false_if_dict_not_returned(self):
        c = ConfigReader(self.config_path)
        c.set('Sample', 'Example', 'MainSection')
        c.set('Sample', 'Example', 'OtherSection')
        c.set('Name', 'File', 'OtherSection')
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
        compare(c.print(output=False), expected)

    @create_file
    def test_returns_false_if_key_exists(self):
        c = ConfigReader(self.config_path)
        expected = None
        compare(c.get('Sample'), expected)

    @create_file
    def test_returns_false_if_json_not_dumped(self):
        c = ConfigReader(self.config_path)
        c.set('Sample', 'Example', 'MainSection')
        c.set('Sample', 'Example', 'OtherSection')
        c.set('name', 'File', 'OtherSection')
        c.remove_section('main')
        in_dict = {
            'MainSection': {
                'sample': 'Example'
            },
            'OtherSection': {
                'sample': 'Example',
                'name': 'File'
            }
        }
        expected = json.dumps(in_dict)
        with self.subTest(0):
            compare(os.path.isfile(c.filename), True)
        with self.subTest(1):
            compare(c.to_json(), expected)

    @create_file
    def test_returns_false_if_json_file_not_created(self):
        c = ConfigReader(self.config_path)

        filename = os.path.join(self.test_dir, 'abc.json')
        c.to_json(filename)
        compare(os.path.isfile(filename), True)

    @create_file
    def test_returns_false_if_json_not_dumped_to_file(self):
        c = ConfigReader(self.config_path)
        c.set('Simple', 'Example', 'MainSection')
        c.set('Simple', 'Example', 'OtherSection')
        c.set('none', 'File', 'OtherSection')
        c.remove_section('main')
        in_dict = {
            'MainSection': {
                'simple': 'Example'
            },
            'OtherSection': {
                'simple': 'Example',
                'none': 'File'
            }
        }
        expected = json.dumps(in_dict)
        filename = '{}.json'.format(str(uuid4()))

        file_path = self.tempdir.write(filename, b'')
        c.to_json(file_path)

        content = open(file_path, 'r').read()
        print('content:', content)
        compare(content, expected)
        os.remove(file_path)

    @create_file
    def test_returns_false_if_defaults_are_changed(self):
        dr = ConfigReader(self.config_path)
        dr.set('new', 'False')
        dr.set('browser', 'default','MainSection')
        dr.set('header', 'False', 'MainSection')

        config = ConfigReader(self.config_path)
        config.set('browser', 'default', 'MainSection')
        with self.subTest(0):
            expected = False
            result = config.get('new')
            print('result:', result)
            compare(result, expected)
        with self.subTest(1):
            expected = 'default'
            compare(config.get('browser', section='MainSection'), expected)
        with self.subTest(2):
            expected = None
            compare(config.get('browser'), expected)
        with self.subTest(3):
            expected = 'Not set'
            compare(config.get('default', default='Not set'), expected)


if __name__ == "__main__":
    unittest.main()
