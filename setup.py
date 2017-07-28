import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup (
    name='ezi',
    version='0.0.2',
    packages=['ezi'],
    install_requires=["Django>=1.7"],
    include_package_data=True,
    description="Quick framework for creating JSON APIs",
    long_description=README,
    url='https://github.com/ianbro/ezi',
)
