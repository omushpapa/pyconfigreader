import pypandoc
from setuptools import setup

long_description = pypandoc.convert_file('README.md', 'rst')

setup(name='pyconfigreader',
      version='0.2.3',
      description='A simple module for handling configurations and config files',
      long_description=long_description,
      url='http://github.com/giantas/pyconfigreader',
      author='Aswa Paul',
      license='MIT',
      packages=['pyconfigreader'],
      install_requires=[
          'testfixtures',
      ],
      zip_safe=False)