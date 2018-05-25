from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert_file('README.md', 'rst')
except (ImportError, OSError, RuntimeError):
    long_description = 'Usage available at http://github.com/giantas/pyconfigreader'

setup(name='pyconfigreader',
      version='0.3.2',
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
