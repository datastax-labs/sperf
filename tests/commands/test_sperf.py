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

"""validates the sperf commands are wired up correctly"""
import unittest
from pysper.commands import sperf


class TestSperfCommands(unittest.TestCase):
    """tests the default sperf commands"""

    def test_sperf_global_flags(self):
        """testing global flags are wired up"""
        parser = sperf.build_parser()
        args = parser.parse_args(["--debug", "--no-progress"])
        self.assertTrue(hasattr(args, "debug"))
        self.assertTrue(hasattr(args, "noprogress"))

    def test_sperf_global_short_flags(self):
        """tests the global short flag"""
        parser = sperf.build_parser()
        args = parser.parse_args(["-v", "-x"])
        self.assertTrue(hasattr(args, "debug"))
        self.assertTrue(hasattr(args, "noprogress"))

    def test_sperf_will_break_if_incorrect_comamnd_is_used(self):
        """this is here so we can rely on the parser tests
        for subcommands tests being accurate"""
        parser = sperf.build_parser()
        success = False
        try:
            parser.parse_args(["nevergonnabereal"])
        except SystemExit as e:
            success = True
            self.assertEqual(str(e), "2")
        self.assertTrue(success)

    def test_core_diag_wired(self):
        """verify cassread is connected"""
        parser = sperf.build_parser()
        args = parser.parse_args(["core", "diag"])
        self.assertTrue(hasattr(args, "func"))

    def test_search_filtercache_wired(self):
        """verify filtercache is connected"""
        parser = sperf.build_parser()
        args = parser.parse_args(["search", "filtercache"])
        self.assertTrue(hasattr(args, "func"))

    def test_jarcheck_wired(self):
        """verify jarcheck is connected"""
        parser = sperf.build_parser()
        args = parser.parse_args(["core", "jarcheck"])
        self.assertTrue(hasattr(args, "func"))

    def test_schema_wired(self):
        """verify schema is connected"""
        parser = sperf.build_parser()
        args = parser.parse_args(["core", "schema"])
        self.assertTrue(hasattr(args, "func"))

    def test_slowquery_wired(self):
        """verify slowquery is connected"""
        parser = sperf.build_parser()
        args = parser.parse_args(["core", "slowquery"])
        self.assertTrue(hasattr(args, "func"))

    def test_solrqueryagg_wired(self):
        """verify solrqueryagg is connected"""
        parser = sperf.build_parser()
        args = parser.parse_args(["search", "queryscore"])
        self.assertTrue(hasattr(args, "func"))

    def test_sysbottle_wired(self):
        """verify sysbottle is connected"""
        parser = sperf.build_parser()
        args = parser.parse_args(["sysbottle", "iostat.txt"])
        self.assertTrue(hasattr(args, "func"))
