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

"""tests jarcheck"""
import unittest
import os
from pysper import jarcheck
from tests import get_current_dir, steal_output


class TestJarCheck(unittest.TestCase):
    """test the jarcheck module"""

    def test_read_line_output(self):
        """jar check parser test"""
        test_file = os.path.join(
            get_current_dir(__file__), "testdata", "simple-output.log"
        )
        parser = jarcheck.JarCheckParser(files=[test_file])
        parser.analyze()
        self.assertEqual(len(parser.jars), 501)
        self.assertTrue("exp4j-0.4.8.jar" in parser.jars)

    def test_run_jarcheck_diff_only(self):
        """integration test for the full command with diff_only"""
        test_file_1 = os.path.join(
            get_current_dir(__file__), "testdata", "simple-output.log"
        )
        test_file_2 = os.path.join(
            get_current_dir(__file__), "testdata", "simple-output2.log"
        )
        parser = jarcheck.JarCheckParser(files=[test_file_1, test_file_2])
        output = steal_output(parser.print_report, diff_only=True)
        self.assertIn(
            """Inconsistent jars
------------------------------
dse-advrep-6.7.1.jar

Analyzed 2 files""",
            output,
        )

    def test_run_jarcheck_found_no_files(self):
        """no files found output"""
        parser = jarcheck.JarCheckParser()
        output = steal_output(parser.print_report, diff_only=False)
        self.assertEqual(output, "Nothing analyzed")

    def test_run_jarcheck_with_empty_file(self):
        """integration test for a single file with no jar data in it"""
        test_file_1 = os.path.join(get_current_dir(__file__), "testdata", "empty.log")
        parser = jarcheck.JarCheckParser(files=[test_file_1])
        output = steal_output(parser.print_report)
        self.assertEqual(output, "Analyzed 1 file")
