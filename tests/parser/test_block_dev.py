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

"""block dev report parsing"""
import unittest
import os
from pysper.parser.block_dev import capture_line
from pysper.parser import read_block_dev
from tests import test_dse_tarball


class TestBlockDev(unittest.TestCase):
    """test block dev"""

    def test_parse_file(self):
        """test parsing a file"""
        events = None
        with open(
            os.path.join(
                test_dse_tarball(), "nodes", "10.101.33.205", "blockdev_report"
            )
        ) as blockdev_file:
            events = list(read_block_dev(blockdev_file))
            self.assertEqual(len(events), 4)
            first_event = events[0]
            self.assertEqual(first_event["ra"], 256)

    def test_capture_device_line(self):
        """correct capture testing"""
        line = "rw     8   512  4096          0    800166076416   /dev/sdb"
        event = capture_line(line)
        self.assertIsNotNone(event)
        self.assertEqual(event["ro"], "rw")
        self.assertEqual(event["ra"], 8)
        self.assertEqual(event["ssz"], 512)
        self.assertEqual(event["blk_sz"], 4096)
        self.assertEqual(event["start_sec"], 0)
        self.assertEqual(event["size"], 800166076416)
        self.assertEqual(event["device"], "/dev/sdb")

    def test_ignores_header(self):
        """expect a skipped header"""
        line = "RO    RA   SSZ   BSZ   StartSec            Size   Device"
        event = capture_line(line)
        self.assertIsNone(event)

    def test_ignores_default_blockdev_error(self):
        """validates that each line is ignored when a failed blockdev report is generated"""
        self.assertIsNone(capture_line("/sbin/blockdev --report"))
        self.assertIsNone(capture_line("exit status: 1"))
        self.assertIsNone(capture_line("stderr:"))
        self.assertIsNone(capture_line("sudo: a password is required"))
