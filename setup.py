#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'beautifulsoup4==4.10.0',
    'more-itertools==8.12.0',
    'openpyxl==3.0.9',
    'pandas==1.3.5',
    'requests==2.27.1',
    'lxml==4.7.1',
    'numpy==1.22.0'
]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="kk",
    author_email='kari.kalliojarvi@kolumbus.fi',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Kelly betting",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='Kelly',
    name='Kelly',
    packages=find_packages(include=['Kelly']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/kjkalliojarvi/Kelly',
    version='0.5.0',
    zip_safe=False,
    entry_points={
        'console_scripts':[
            'kelly=Kelly.__main__:kelly'
        ]
    },
)
