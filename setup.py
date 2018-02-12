from setuptools import setup

setup(name='pyconfigreader',
      version='0.0.1',
      description='A simple settings.ini handler in python',
      url='http://github.com/giantas/configreader',
      author='Aswa Paul',
      license='MIT',
      packages=['pyconfigreader'],
      install_requires=[
          'testfixtures',
      ],
      zip_safe=False)