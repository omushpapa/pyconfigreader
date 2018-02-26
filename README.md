# ConfigReader

[![Travis-CI](https://img.shields.io/travis/giantas/pyconfigreader.svg?maxAge=2592001)](https://travis-ci.org/giantas/pyconfigreader)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/5f3132cafe78478dbdeb081b53d3661d)](https://www.codacy.com/app/giantas/pyconfigreader?utm_source=github.com&utm_medium=referral&utm_content=giantas/pyconfigreader&utm_campaign=Badge_Coverage)
[![Issues](https://img.shields.io/github/issues-raw/giantas/pyconfigreader/website.svg)](https://github.com/giantas/pyconfigreader/issues)

A configuration file handler for the most basic stuff in ini files that will get you up and running in no time.

***PS***: This is just to get you working on other stuff and not focus on config files. If you need advanced features head to [Python's ConfigParser](https://docs.python.org/3/library/configparser.html).

## Usage

```
$ pip install pyconfigreader
```

```python
from pyconfigreader import ConfigReader

config = ConfigReader(filename='config.ini')
config.set('Key', 'Value', section='Section')
config.set('name', 'main')
config.set('okay', 'True', commit=True)

name = config.get('name')
okay = config.get('okay')
section = config.get('Key', section='Section')

agency = config.get('agency')  # agency is None, it doesn't exist

print(config.sections)

key, value, section = config.search('config')

help(config)
config.close()  # Don't forget to close the file object
```
A lot more on `help(config)`

# More
Docs to come :)

# License
Distributed under [MIT](LICENSE)
