#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='organizador_parser',
      version='0.1',
      description='Parser para el organizador',
      author='Alejandro Pernin',
      author_email='apernin@fi.uba.ar',
      packages=find_packages(exclude=('tests', 'tests.*')),
)
