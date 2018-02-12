# ConfigReader

[![Travis-CI](https://img.shields.io/travis/giantas/daterelate.svg?maxAge=2592000)](https://travis-ci.org/giantas/daterelate)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/a5b7006d480e4a0691586c2e86e277c5)](https://www.codacy.com/app/giantas/configreader?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=giantas/configreader&amp;utm_campaign=Badge_Grade)
[![Issues](https://img.shields.io/github/issues-raw/giantas/daterelate/website.svg)](https://github.com/giantas/daterelate/issues)

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
