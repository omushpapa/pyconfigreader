from setuptools import setup

setup(name='pyconfigreader',
      version='0.1.0',
      description='A simple module for handling configurations and config files',
      url='http://github.com/giantas/pyconfigreader',
      author='Aswa Paul',
      license='MIT',
      packages=['pyconfigreader'],
      install_requires=[
          'testfixtures',
      ],
      python_requires='>=3',
      zip_safe=False)