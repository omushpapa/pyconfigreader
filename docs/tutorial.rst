Getting Started
===============

Installation
------------

Installation is as simple as running this command in the terminal.

.. code-block:: bash

   $ pip install pyconfigreader


QuickStart
----------

To read a configuration file create a file ``settings.ini`` in the current directory
and paste the following content::

   [main]
   reader = configreader
   name = pyconfigreader
   language = python
   versions = [2.7, 3.4, 3.5, 3.6]

   [DATA]
   language = English
   development = None
   path = /home/ubuntu/
   user = Ubuntu
   groups = 1000


In a Python console, import :class:`~pyconfigreader.reader.ConfigReader`::
   
   >>> from pyconfigreader import ConfigReader

Declare the path to your ``settings.ini`` file::

   >>> settings_ini = '/path/to/settings.ini'

Read the settings file::

   >>> config = ConfigReader(settings_ini)

Get data from the config::

   >>> config.get('reader')
   ... 'configreader'
   >>> config.get('groups', section='DATA')
   ... 1000

Set values::

   >>> config.set('key', 'value', section='section')
   >>> config.set('number', 4, section='NEW')

Save changes::

   >>> config.save()

Close the :class:`~pyconfigreader.reader.ConfigReader` object::

   >>> config.close()  # Close without saving changes
   >>> # or
   >>> config.close(save=True)  # Save the changes then close

