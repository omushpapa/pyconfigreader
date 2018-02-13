# ConfigReader

[![Travis-CI](https://img.shields.io/travis/giantas/pyconfigreader.svg?maxAge=2592000)](https://travis-ci.org/giantas/pyconfigreader)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/5f3132cafe78478dbdeb081b53d3661d)](https://www.codacy.com/app/giantas/pyconfigreader?utm_source=github.com&utm_medium=referral&utm_content=giantas/pyconfigreader&utm_campaign=Badge_Coverage)
[![Issues](https://img.shields.io/github/issues-raw/giantas/pyconfigreader/website.svg)](https://github.com/giantas/pyconfigreader/issues)

A simple settings.ini handler in python

## Usage

```
$ pip install pyconfigparser
```

```python
from pyconfigreader.reader import ConfigReader

config = ConfigReader(filename='config.ini')
config.set('Key', 'Value', section='Section')
config.set('name', 'main')
config.set('okay', 'True')

name = config.get('name')
okay = config.get('okay')
```
For more info check: `help(config)`

# More
... to be added

# etc
Distributed under [MIT](LICENSE)
