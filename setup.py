from setuptools import setup

setup (
    name='ezi',
    version='0.0.1',
    packages=['ezi'],
    install_requires=["Django>=1.7"],
    include_package_data=True,
    description="Quick framework for creating JSON APIs",
    long_description=README,
    url='https://github.com/ianbro/ezi',
)
