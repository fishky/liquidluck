#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
install_requires=['docutils', 'Jinja2', 'Pygments', 'markdown']
try:
    import argparse # python 2.7+ support argparse
except ImportError:
    install_requires.append('argparse')


from liquidluck import __version__ as version

setup(
    name = 'liquidluck',
    version = version,
    author = 'Hsiaoming Young',
    author_email = 'lepture@me.com',
    url = 'http://github.com/lepture/liquidluck',
    packages = ['liquidluck', 'liquidluck.writers', 'liquidluck.readers'],
    description = 'A lightweight static weblog generator',
    license = 'BSD License',
    entry_points = {
        'console_scripts': ['liquidluck= liquidluck.cli:main'],
    },
    install_requires=install_requires,
    include_package_data = True,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Programming Language :: Python',
    ]
)
