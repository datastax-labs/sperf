"""setup script for sperf"""

from setuptools import setup
import setuptools

setup(
    name='sperf',
    version='0.6.0',
    description='Diagnostic utility for DSE and Cassandra',
    url='https://www.github.com/DataStax-Toolkit/sperf',
    app=["sperf.py"],
    setup_requires=['PyInstaller', 'pytest'],
    package_dir={'': 'pysper'},
)
