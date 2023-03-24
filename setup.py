# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='pylibgraph',
    version='0.1.0',
    description='python grapher for nm symbols',
    long_description=readme,
    author='Gilles Betteto',
    author_email='gnetwb@hotmail.com',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
