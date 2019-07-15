# pyconfigreader

[![Travis-CI](https://img.shields.io/travis/giantas/pyconfigreader.svg?maxAge=220)](https://travis-ci.org/giantas/pyconfigreader)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/5f3132cafe78478dbdeb081b53d3661d)](https://www.codacy.com/app/giantas/pyconfigreader?utm_source=github.com&utm_medium=referral&utm_content=giantas/pyconfigreader&utm_campaign=Badge_Coverage)
[![Issues](https://img.shields.io/github/issues-raw/giantas/pyconfigreader/website.svg)](https://github.com/giantas/pyconfigreader/issues)
[![Python](https://img.shields.io/pypi/pyversions/pyconfigreader.svg)](https://img.shields.io/pypi/pyversions/pyconfigreader.svg)

A configuration file handler for the most basic stuff in ini files that will get you up and running in no time.

pyconfigreader's `ConfigReader` uses Python's ConfigParser to parse config files.

***PS***: This is just to get you working on other stuff and not focus on config files. 
If you need advanced features head to [Python's ConfigParser](https://docs.python.org/3/library/configparser.html) or 
read [pyconfigreader's documentation](https://pyconfigreader.readthedocs.io/).

# Usage

## Installation
```
$ pip install pyconfigreader
```

## Setting Values

`ConfigReader` creates a default `main` section in which key-value pairs are inserted if no section is specified.

```python
from pyconfigreader import ConfigReader
config = ConfigReader(filename='config.ini')
config.set('version', '2')  # Saved to section `main`
config.set('Key', 'Value', section='Section')   # Creates a section `Section` on-the-fly
config.set('name', 'main')
config.close(save=True)  # Save on close
# Or explicitly call
# config.save()
# config.close()
```

By default, changes are not immediately written to the file on disk but are kept in memory.
`commit=True` writes the changes to the file on disk.

```python
from pyconfigreader import ConfigReader
config = ConfigReader(filename='config.ini')
config.set('okay', 'True', commit=True)
```

## Getting values

Getting values only requires specifying the key. If the key does not exist then None is returned. No exception is raised.

```python
from pyconfigreader import ConfigReader
config = ConfigReader(filename='config.ini')
name = config.get('name')
okay = config.get('okay')
section = config.get('Key', section='Section')  # Get from the section `Section`

agency = config.get('agency')  # Raises NoOptionError

print(config.sections)  # Get a list of sections

key, value, section = config.search('config')   # Search for the parameters of a value. Returns a tuple

help(config)
config.close()  # Don't forget to close the file object
```

Sometimes, if a key is not available a return value may be added using the `default` argument
```python
from pyconfigreader import ConfigReader
config = ConfigReader(filename='config.ini')
name = config.get('country', default='Kenya')   # Returns Kenya since key was not available in config file
config.close()
```

The return value, by default, is not saved to file but this can be enabled by 
setting `default_commit`=True
```python
from pyconfigreader import ConfigReader
config = ConfigReader(filename='config.ini')
name = config.get('name', default='Kenya', default_commit=True)
config.close()
```

Any call to `commit` saves all the in-memory changes to the file on disk.

## Options

Options can be remove permanently

```python
from pyconfigreader import ConfigReader
config = ConfigReader(filename='config.ini')
config.remove_option('reader')  # the reader option is always set by default
# or config.remove_key('reader')
config.set('name', 'first', section='Details')
config.remove_option('name', section='Details')
config.close(save=True)
```

## Sections
Sections are created when keys and values are added to them.

```python
from pyconfigreader import ConfigReader
config = ConfigReader(filename='config.ini')
config.set('name', 'first', section='Details')  # Save key `name` with value `first` in section `Details`
config.close()
```

Sections can be removed explicitly.
```python
from pyconfigreader import ConfigReader
config = ConfigReader(filename='config.ini')
config.set('name', 'first', section='Details') # Creates section `Details`
config.remove_section('Details')    # Removes section `Details` plus all the keys and values
config.close(save=True)
```

Section items can be acquired as dictionary values
```python
from pyconfigreader import ConfigReader
config = ConfigReader(filename='config.ini')
config.set('name', 'first', section='Details')

config.get_items('Details')
# OrderedDict([('name', 'first')])
config.close()  # Or config.close(save=True)
```

## Environment Variables
Configuration values can be save to the environment (`os.environ`)

```python
import os
from pyconfigreader import ConfigReader
config = ConfigReader(filename='config.ini')
config.set('name', 'first', section='Details')
config.to_env()
os.environ['DETAILS_NAME']
# first
os.environ['MAIN_READER']
# configreader
config.close()
```

The environment keys are formed from the section name and the key name.

## Saving

Changes are not written to disk unless `commit` is set to True.

Another alternative is calling `to_file`

```python
from pyconfigreader import ConfigReader
config = ConfigReader(filename='config.ini')
config.set('name', 'first', section='Details')
config.save()
config.close()
```

As a context, the changes are saved when the object is closed.

```python
from pyconfigreader import ConfigReader
with ConfigReader(filename='config.ini') as config:
    config.set('name', 'first', section='Details')
```

The contents of the config file can also be dumped to a JSON file.
```python
from pyconfigreader import ConfigReader
reader = ConfigReader()
reader.set('name', 'first', section='Details')
with open('config.json', 'w') as f:
    reader.to_json(f)
    
reader.close()
```

A lot more on `help(config)`

# More
See [pyconfigreader documentation](https://pyconfigreader.readthedocs.io/).

# License
Distributed under [MIT](LICENSE)
