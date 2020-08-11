from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert_file('README.md', 'rst')
except (ImportError, OSError, RuntimeError):
    long_description = 'Usage available at http://github.com/giantas/pyconfigreader'

setup(name='pyconfigreader',
      version='0.8.2',
      description='A module for handling simple configuration requirements',
      long_description=long_description,
      url='http://github.com/giantas/pyconfigreader',
      author='Aswa Paul',
      license='MIT',
      packages=['pyconfigreader'],
      install_requires=[],
      zip_safe=False,
      python_requires='>3.4, <3.8',
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
      ]
)
