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

"""paresr test for outputlog"""
import unittest
import os
from pysper.parser import outputlog
from pysper import parser
from tests import get_test_dir


class TestOutputLog(unittest.TestCase):
    """output log tests"""

    def test_versions_from_output_log(self):
        """retrieve server versions present"""
        output_log_path = os.path.join(get_test_dir(), "output.log")
        with open(output_log_path, "r") as log:
            events = list(parser.read_output_log(log))
            solr_version = None
            spark_version = None
            dse_spark_connector_version = None
            for event in events:
                if "spark_version" in event:
                    spark_version = event["spark_version"]
                if "dse_spark_connector_version" in event:
                    dse_spark_connector_version = event["dse_spark_connector_version"]
                if "solr_version" in event:
                    solr_version = event["solr_version"]
                if "version" in event:
                    dse_version = event["version"]
            self.assertEqual(dse_version, "6.7.7")
            self.assertEqual(solr_version, "6.0.1.2.2647")
            self.assertEqual(spark_version, "2.2.3.9")
            self.assertEqual(dse_spark_connector_version, "6.7.7")

    def test_versions_cassandra_21(self):
        """retrieve server versions present"""
        output_log_path = os.path.join(get_test_dir(), "cassandra21", "system.log")
        with open(output_log_path, "r") as log:
            events = list(parser.read_output_log(log))
            cassandra_version = None
            for event in events:
                if "cassandra_version" in event:
                    cassandra_version = event["cassandra_version"]
            self.assertEqual(cassandra_version, "2.1.21")

    def test_versions_cassandra_22(self):
        """retrieve server versions present"""
        output_log_path = os.path.join(get_test_dir(), "cassandra22", "system.log")
        with open(output_log_path, "r") as log:
            events = list(parser.read_output_log(log))
            cassandra_version = None
            for event in events:
                if "cassandra_version" in event:
                    cassandra_version = event["cassandra_version"]
            self.assertEqual(cassandra_version, "2.2.15")

    def test_versions_cassandra_30(self):
        """retrieve server versions present"""
        output_log_path = os.path.join(get_test_dir(), "cassandra30", "system.log")
        with open(output_log_path, "r") as log:
            events = list(parser.read_output_log(log))
            cassandra_version = None
            for event in events:
                if "cassandra_version" in event:
                    cassandra_version = event["cassandra_version"]
            self.assertEqual(cassandra_version, "3.0.19")

    def test_versions_cassandra_311(self):
        """retrieve server versions present"""
        output_log_path = os.path.join(get_test_dir(), "cassandra311", "system.log")
        with open(output_log_path, "r") as log:
            events = list(parser.read_output_log(log))
            cassandra_version = None
            for event in events:
                if "cassandra_version" in event:
                    cassandra_version = event["cassandra_version"]
            self.assertEqual(cassandra_version, "3.11.5")

    def test_parser_output_log(self):
        """make sure the parse_log gets the configuration from the log"""
        output_log_path = os.path.join(get_test_dir(), "output.log")
        with open(output_log_path, "r") as log:
            events = list(parser.read_output_log(log))
            cpu_cores, threads_per_core, ram_in_mb, heap_size, gc_type = (
                None,
                None,
                None,
                None,
                None,
            )
            disk_access_mode, index_access_mode, commit_log_access_mode = (
                None,
                None,
                None,
            )
            for event in events:
                if "cpu_cores" in event:
                    cpu_cores = event["cpu_cores"]
                if "threads_per_core" in event:
                    threads_per_core = event["threads_per_core"]
                if "jvm_args" in event:
                    if "-Ddse.system_memory_in_mb" in event["jvm_args"]:
                        for ram in event["jvm_args"]["-Ddse.system_memory_in_mb"]:
                            # just get the last one
                            ram_in_mb = ram
                    for args in event["jvm_args"]:
                        if args.startswith("-Xmx"):
                            heap_size = "".join(args[4:])
                        if args == "-XX:+UseG1GC":
                            gc_type = "G1GC"
                if "logged_disk_access_mode" in event:
                    disk_access_mode = event["logged_disk_access_mode"]
                if "logged_index_access_mode" in event:
                    index_access_mode = event["logged_index_access_mode"]
                if "logged_commit_log_access_mode" in event:
                    commit_log_access_mode = event["logged_commit_log_access_mode"]
            self.assertEqual(disk_access_mode, "standard")
            self.assertEqual(index_access_mode, "standard")
            self.assertEqual(commit_log_access_mode, "standard")
            self.assertEqual(cpu_cores, 8)
            self.assertEqual(threads_per_core, 1)
            self.assertEqual(ram_in_mb, "15038")
            self.assertEqual(gc_type, "G1GC")
            self.assertEqual(heap_size, "3759M")

    def test_parse_disk_access_mode_48(self):
        """validate the 4.8 modes are handled correctly"""
        line = "INFO 10:13:16,088  DiskAccessMode 'auto' determined to be mmap, indexAccessMode is mmap"
        fields = outputlog.capture_line(line)
        self.assertIsNotNone(fields)
        self.assertEqual(fields["logged_disk_access_mode"], "mmap")
        self.assertEqual(fields["logged_index_access_mode"], "mmap")

    def test_parse_disk_access_mode_50(self):
        """validate the 5.0 modes are handled correctly"""
        line = "INFO 11:15:02,584 DatabaseDescriptor.java:320 - DiskAccessMode 'auto' determined to be mmap, indexAccessMode is mmap"
        fields = outputlog.capture_line(line)
        self.assertIsNotNone(fields)
        self.assertEqual(fields["logged_disk_access_mode"], "mmap")
        self.assertEqual(fields["logged_index_access_mode"], "mmap")
        line = "INFO 11:12:24,303 DatabaseDescriptor.java:326 - DiskAccessMode is standard, indexAccessMode is mmap"
        fields = outputlog.capture_line(line)
        self.assertIsNotNone(fields)
        self.assertEqual(fields["logged_disk_access_mode"], "standard")
        self.assertEqual(fields["logged_index_access_mode"], "mmap")
        line = "INFO 11:13:34,429 DatabaseDescriptor.java:331 - DiskAccessMode is standard, indexAccessMode is standard"
        fields = outputlog.capture_line(line)
        self.assertIsNotNone(fields)
        self.assertEqual(fields["logged_disk_access_mode"], "standard")
        self.assertEqual(fields["logged_index_access_mode"], "standard")

    def test_parse_disk_access_mode_51(self):
        """validates 5.1 parses correctly"""
        line = (
            "INFO [main] 2018-01-09 12:18:13,157 DatabaseDescriptor.java:374 - "
            + "DiskAccessMode is standard, indexAccessMode is mmap"
        )
        fields = outputlog.capture_line(line)
        self.assertIsNotNone(fields)
        self.assertEqual(fields["logged_disk_access_mode"], "standard")
        self.assertEqual(fields["logged_index_access_mode"], "mmap")

    def test_parse_disk_access_mode_60(self):
        """validates 6.0 which is a totally new format parses correctly"""
        line = (
            "INFO [main] 2018-01-09 12:32:23,568 DatabaseDescriptor.java:425 - "
            + "DiskAccessMode is standard, indexAccessMode is standard, commitlogAccessMode is standard"
        )
        fields = outputlog.capture_line(line)
        self.assertIsNotNone(fields)
        self.assertEqual(fields["logged_disk_access_mode"], "standard")
        self.assertEqual(fields["logged_index_access_mode"], "standard")
        self.assertEqual(fields["logged_commit_log_access_mode"], "standard")

    def test_parse_threads_per_core(self):
        """validates the threads per core log format"""
        line = "INFO  [main] 2017-01-11 12:19:06,187  DseConfig.java:455 - This instance appears to have 2 threads per CPU core and 16 total CPU threads."
        fields = outputlog.capture_line(line)
        self.assertIsNotNone(fields)
        self.assertEqual(fields["threads_per_core"], 2)
        self.assertEqual(fields["cpu_cores"], 16)

    def test_1_thread_per_core_long_format(self):
        """thread instead of threads per core"""
        line = "INFO  [main] 2018-01-09 10:12:11,864  DseConfig.java:448 - This instance appears to have 1 thread per CPU core and 8 total CPU threads."
        fields = outputlog.capture_line(line)
        self.assertIsNotNone(fields)
        self.assertEqual(fields["threads_per_core"], 1)
        self.assertEqual(fields["cpu_cores"], 8)

    def test_parse_threads_per_core_short_format(self):
        """validates the threads per core log format"""
        line = "INFO  01:07:18,474  This instance appears to have 2 threads per CPU core and 8 total CPU threads."
        fields = outputlog.capture_line(line)
        self.assertIsNotNone(fields)
        self.assertEqual(fields["threads_per_core"], 2)
        self.assertEqual(fields["cpu_cores"], 8)

    def test_parse_1_thread_per_core_short_format(self):
        """validates the threads per core log format"""
        line = "INFO  01:06:12,474  This instance appears to have 1 thread per CPU core and 8 total CPU threads."
        fields = outputlog.capture_line(line)
        self.assertIsNotNone(fields)
        self.assertEqual(fields["threads_per_core"], 1)
        self.assertEqual(fields["cpu_cores"], 8)

    def test_parse_threads_per_core_old_format(self):
        """pre 5.1 behavior"""
        line = "INFO 10:12:10,183 DseConfig.java:437 - This machine appears to have 1 thread per CPU core."
        fields = outputlog.capture_line(line)
        self.assertIsNotNone(fields)
        self.assertEqual(fields["threads_per_core"], 1)

    def test_parse_threads_per_core_old_format_with_2_cores(self):
        """pre 5.1 behavior"""
        line = "INFO 10:12:10,382 DseConfig.java:437 - This machine appears to have 2 threads per CPU core."
        fields = outputlog.capture_line(line)
        self.assertIsNotNone(fields)
        self.assertEqual(fields["threads_per_core"], 2)
