"""setup script for sperf"""

from setuptools import setup, find_packages

# setuptools import is needed on 3.5
# pylint: disable=unused-import
import setuptools

setup(
    name="sperf",
    version="0.6.4",
    description="Diagnostic utility for DSE and Cassandra",
    url="https://www.github.com/DataStax-Toolkit/sperf",
    scripts=["scripts/sperf"],
    setup_requires=["PyInstaller"],
    packages=find_packages(include=["pysper", "pysper.*"]),
)
