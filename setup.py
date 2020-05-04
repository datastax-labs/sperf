"""setup script for sperf"""

from setuptools import setup

setup(
    name='sperf',
    version='0.6.0',
    description='Diagnostic utility for DSE and Cassandra',
    url='https://www.github.com/DataStax-Toolkit/sperf',
    app=["sperf.py"],
    setup_requires=['PyInstaller', 'tox'],
    package_dir={'': 'pysper'},
)
