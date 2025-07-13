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

"""tests the node_env.py module"""
import unittest
import os
from pysper.core.diag import node_env
from tests import get_test_dse_tarball


class TestNodeEnv(unittest.TestCase):
    """test node env module"""

    def test_jvm_based_parameter_parsing(self):
        """breaks up jvm args into kv"""
        line = {
            "-Xms31G": None,
            "-Xmx31G": None,
            "-Djdk.nio.maxCachedBufferSize": ["1048576"],
            "-XX:+UseG1GC": None,
            "-XX:MaxGCPauseMillis": ["500"],
            "-Ddse.system_memory_in_mb": ["0", "120663"],
        }
        heap, gc_type, ram = node_env.read_jvm_based_parameters(line)
        self.assertEqual(gc_type, "G1GC")
        self.assertEqual(heap, "31G")
        self.assertEqual(ram, "118 gb")

    def test_read_cassandra_parameter_parsing(self):
        """breaks up jvm args into kv"""
        config = {
            "memtable_cleanup_threshold": "null",
            "memtable_flush_writers": "2",
        }
        configs = node_env.read_cassandra_config(config)
        self.assertEqual(configs["memtable_flush_writers"], "2")
        self.assertEqual(configs["memtable_cleanup_threshold"], "default")

    def test_read_outputlog(self):
        """verify configuration is parsed"""
        configs = {"node1": {}}
        node1 = "10.101.33.205"
        output_logs = [
            os.path.join(
                get_test_dse_tarball(), "nodes", node1, "logs", "cassandra", "output.log"
            )
        ]
        system_logs = [
            os.path.join(
                get_test_dse_tarball(), "nodes", node1, "logs", "cassandra", "system.log"
            )
        ]
        node_env.find_config_in_logs(configs, output_logs, system_logs)
        self.assertEqual(configs[node1]["memtable_cleanup_threshold"], "default")

    def test_read_systemlog_when_outputlog_is_empty(self):
        """verify configuration is parsed"""
        configs = {"node1": {}}
        output_logs = [
            os.path.join(
                get_test_dse_tarball(),
                "nodes",
                "10.101.33.205",
                "logs",
                "cassandra",
                "doesntexist.log",
            )
        ]
        system_logs = [
            os.path.join(
                get_test_dse_tarball(),
                "nodes",
                "10.101.33.205",
                "logs",
                "cassandra",
                "system.log",
            ),
            os.path.join(
                get_test_dse_tarball(),
                "nodes",
                "10.101.33.205",
                "logs",
                "cassandra",
                "system.log.2",
            ),
        ]
        node_env.find_config_in_logs(configs, output_logs, system_logs)
        self.assertEqual(
            configs["10.101.33.205"]["memtable_cleanup_threshold"], "default"
        )
