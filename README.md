# ConfigReader

A simple settings.ini handler in python

## Usage

```python
from configreader import ConfigReader

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
