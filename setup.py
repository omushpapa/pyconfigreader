from setuptools import setup

setup(name='pyconfigreader',
      version='0.2.1',
      description='A simple module for handling configurations and config files',
      url='http://github.com/giantas/pyconfigreader',
      author='Aswa Paul',
      license='MIT',
      packages=['pyconfigreader'],
      install_requires=[
          'testfixtures',
      ],
      zip_safe=False)