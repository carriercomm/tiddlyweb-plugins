
# YOU NEED TO EDIT THESE
AUTHOR = 'Chris Dent'
AUTHOR_EMAIL = 'cdent@peermore.com'
NAME = 'tiddlywebplugins.diststore'
DESCRIPTION = 'Use multiple stores in the same TiddlyWeb instance.'
VERSION = '0.2'

import os
from setuptools import setup, find_packages

# You should review the below so that it seems correct. install_requires
# especially.
setup(
        namespace_packages = ['tiddlywebplugins'],
        name = NAME,
        version = VERSION,
        description = DESCRIPTION,
        long_description=file(os.path.join(os.path.dirname(__file__), 'README')).read(),
        author = AUTHOR,
        url = 'http://pypi.python.org/pypi/%s' % NAME,
        packages = find_packages(exclude='test'),
        author_email = AUTHOR_EMAIL,
        platforms = 'Posix; MacOS X; Windows',
        install_requires = ['setuptools', 'tiddlyweb'],
        )
