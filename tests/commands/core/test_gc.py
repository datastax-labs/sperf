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

"""validates the gc args are in place"""
import unittest
import argparse
import os
from pysper.commands.core import gc


class TestGCIntegration(unittest.TestCase):
    """integration tests for the gc command"""

    def test_args(self):
        """verify gc args are wired up correctly"""
        parser = argparse.ArgumentParser(prog="mine", description="entry point")
        subparsers = parser.add_subparsers()
        gc.build(subparsers)
        args = parser.parse_args(
            ["gc", "-f", "foo", "-d", "diag", "-i", "3600", "-r", "report"]
        )
        self.assertTrue(hasattr(args, "files"))
        self.assertTrue(hasattr(args, "diag_dir"))
        self.assertTrue(hasattr(args, "interval"))
        self.assertTrue(hasattr(args, "reporter"))

    def test_gc_run(self):
        """validates we don't get a bad exit code"""
        parser = argparse.ArgumentParser(prog="mine", description="entry point")
        subparsers = parser.add_subparsers()
        gc.build(subparsers)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_dir_1 = current_dir + "/../testdata/diag/statuslogger"
        args = parser.parse_args(["gc", "-d", test_dir_1, "-r", "nodes"])
        gc.run(args)
