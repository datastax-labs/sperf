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

"""validates the statuslogger args are in place"""
import unittest
import argparse
import os
from pysper.commands.core import statuslogger
from tests import current_dir


class TestStatusLoggerCommand(unittest.TestCase):
    """status logger command args"""

    def test_args(self):
        """verify schema args are wired up correctly"""
        parser = argparse.ArgumentParser(prog="mine", description="entry point")
        subparsers = parser.add_subparsers()
        statuslogger.build(subparsers)
        args = parser.parse_args(
            ["statuslogger", "-f", "foo", "-d", "diag", "-s", "stages", "-r", "report"]
        )
        self.assertTrue(hasattr(args, "files"))
        self.assertTrue(hasattr(args, "diag_dir"))
        self.assertTrue(hasattr(args, "stages"))
        self.assertTrue(hasattr(args, "reporter"))

    def test_statuslogger_run(self):
        """validates we don't get a bad exit code"""
        parser = argparse.ArgumentParser(prog="mine", description="entry point")
        subparsers = parser.add_subparsers()
        statuslogger.build(subparsers)
        test_dir_1 = os.path.join(
            current_dir(__file__), "..", "testdata", "diag", "statuslogger"
        )
        args = parser.parse_args(["statuslogger", "-d", test_dir_1, "-r", "histogram"])
        statuslogger.run(args)
