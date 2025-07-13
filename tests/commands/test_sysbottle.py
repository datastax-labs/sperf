# Copyright 2020 DataStax, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""validates the sysbottle args are in place"""
import unittest
import argparse
import os
from pysper.commands import sysbottle
from tests import get_current_dir


class TestSysBottleCommand(unittest.TestCase):
    """tests the command line args of sysbottle"""

    def test_args(self):
        """verify schema args are wired up correctly"""
        parser = argparse.ArgumentParser(
            prog="sysbottle", description="sysbottle is parsed"
        )
        subparsers = parser.add_subparsers()
        sysbottle.build(subparsers)
        args = parser.parse_args(
            [
                "sysbottle",
                "abc.txt",
                "-c",
                "90",
                "-q",
                "1",
                "-d",
                "sda",
                "-i",
                "5",
                "-t",
                "3",
            ]
        )
        self.assertTrue(hasattr(args, "file"))
        self.assertTrue(hasattr(args, "cpu"))
        self.assertTrue(hasattr(args, "diskQ"))
        self.assertTrue(hasattr(args, "disks"))
        self.assertTrue(hasattr(args, "iowait"))
        self.assertTrue(hasattr(args, "throughput"))

    def test_sysbottle_run(self):
        """validates we don't get a bad exit code"""
        parser = argparse.ArgumentParser(
            prog="sysbottle", description="sysbottle is parsed"
        )
        subparsers = parser.add_subparsers()
        sysbottle.build(subparsers)
        test_file_1 = os.path.join(get_current_dir(__file__), "..", "testdata", "iostat")
        args = parser.parse_args(
            [
                "sysbottle",
                test_file_1,
                "-c",
                "90",
                "-q",
                "1",
                "-d",
                "sda",
                "-i",
                "5",
                "-t",
                "3",
            ]
        )
        sysbottle.run(args)
