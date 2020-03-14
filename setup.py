#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

from os.path import join, dirname

from setuptools import setup, find_packages

RE_REQUIREMENT = re.compile(r'^\s*-r\s*(?P<filename>.*)$')

PYPI_CLEANDOC_FILTERS = (
    # Remove badges lines
    (r'\n.*travis-.*', ''),
    (r'\n.*requires-.*', ''),
    (r'\n.*david-dm.*', ''),
    (r'\n.*gitter-.*', ''),
    (r'\n.*coveralls-.*', ''),
    # Transform links
    (r'\[(.+)\]\[(.+)\]', '`\g<1> <\g<2>_>`_'),
    (r'\[(.+)\]:\s*(.+)\s*', '.. _\g<1>: \g<2>'),
    (r'\[(.+)\]\((.+)\)', '`\g<1> <\g<2>>`_'),
)

ROOT = dirname(__file__)


def clean_doc(filename):
    """Load markdown file and sanitize it for PyPI restructuredtext.

    Remove unsupported github tags:
     - various badges

    Transform markdown links into restructuredtext
    """
    content = open(join(ROOT, filename)).read()
    for regex, replacement in PYPI_CLEANDOC_FILTERS:
        content = re.sub(regex, replacement, content)
    return content


long_description = '\n'.join((
    clean_doc('README.md'),
    clean_doc('CHANGELOG.md'),
))

# Load metadata from  __about__.py file
exec(compile(open('data/__about__.py').read(), 'data/__about__.py', 'exec'))

setup(
    name='pelican-data',
    version=__version__,  # noqa
    description=__description__,  # noqa
    long_description=long_description,
    url='https://github.com/noirbizarre/pelican-data',
    author='Axel Haustant',
    author_email='noirbizarre+github@gmail.com',
    packages=find_packages(),
    python_requires='>=3.6',
    include_package_data=True,
    install_requires=['PyYAML'],
    license='MIT',
    keywords='pelican, data, yaml',
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: System :: Software Distribution',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
    ],
)
