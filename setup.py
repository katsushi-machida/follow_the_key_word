# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst', encoding='utf8') as f:
    readme = f.read()

setup(
    name='trace_target_url',
    version='1.0.0',
    description='Search target URL',
    long_description=readme,
    author='katsushi machida',
    install_requires=['requests', 'cchardet', 'beautifulsoup4', 'mock'],
    packages=find_packages(exclude=('tests'))
)
