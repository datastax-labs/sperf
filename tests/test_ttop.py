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

""" ttop test module """
import unittest
import os
from tests import current_dir, steal_output
from pysper.ttop import TTopAnalyzer
import pprint


class TestTTop(unittest.TestCase):
    """tttop tests"""

    def test_ttop_report(self):
        """ttop parser test"""
        test_file = os.path.join(current_dir(__file__), "testdata", "ttop-cpu.out")
        ttop = TTopAnalyzer([test_file])
        output = steal_output(ttop.print_report)
        self.maxDiff = None
        self.assertIn(
            """2020-01-09 16:08:06                                Threads CPU%  Total: 28.06%
================================================================================
ParkedThreadsMonitor                               1       23.52 -----------------
RMI TCP Connection(2)                              1       2.90  --
CoreThread                                         5       1.20  -
DseGossipStateUpdater                              1       0.10
ScheduledTasks                                     1       0.08
NodeHealthPlugin-Scheduler-thread                  1       0.06
OptionalTasks                                      1       0.05
JMX server connection timeout 425                  1       0.04
ContainerBackgroundProcessor[StandardEngine[Solr]] 1       0.02
PO-thread                                          1       0.02
GossipTasks                                        1       0.01
AsyncAppender-Worker-ASYNCDEBUGLOG                 1       0.01
LeasePlugin                                        1       0.01
NonPeriodicTasks                                   1       0.01
RxSchedulerPurge                                   1       0.01
internode-messaging RemoteMessageServer acceptor   1       0.00""",
            output,
            output.replace("\\n", "\n"),
        )

    def test_ttop_allocation_report(self):
        """ttop parser allocation test"""
        test_file = os.path.join(current_dir(__file__), "testdata", "ttop-cpu.out")
        ttop = TTopAnalyzer([test_file])

        def run():
            ttop.print_report(alloc=True)

        self.maxDiff = None
        output = steal_output(run)
        self.assertIn(
            """2020-01-09 16:08:46                                Threads Alloc/s   Total: 3.24 mb
================================================================================
CoreThread                                         7       2.15 mb   -------------
RMI TCP Connection(2)                              1       1.05 mb   ------
ScheduledTasks                                     1       24.00 kb
ContainerBackgroundProcessor[StandardEngine[Solr]] 1       4.18 kb
JMX server connection timeout 425                  1       4.08 kb
BatchlogTasks                                      1       1.55 kb
LeasePlugin                                        1       1.49 kb
GossipTasks                                        1       916 bytes
RxSchedulerPurge                                   1       646 bytes
ParkedThreadsMonitor                               1       317 bytes
OptionalTasks                                      1       305 bytes
http-bio                                           1       57 bytes
AsyncFileHandlerWriter                             1       32 bytes
internode-messaging RemoteMessageServer acceptor   1       0 byte""",
            output,
            output.replace("\\n", "\n"),
        )

    def test_collate_threads(self):
        ttop = TTopAnalyzer([])
        res = ttop.collate_threads(
            {
                "My Single Thread": {
                    "user_cpu": 1.00,
                    "sys_cpu": 2.00,
                    "heap_rate": 10,
                },
                "RemoteMessageServer query worker - 15": {
                    "user_cpu": 1.00,
                    "sys_cpu": 1.00,
                    "heap_rate": 10,
                },
                "RemoteMessageServer query worker - 14": {
                    "user_cpu": 1.00,
                    "sys_cpu": 1.00,
                    "heap_rate": 10,
                },
                "RemoteMessageServer query worker - 13": {
                    "user_cpu": 1.00,
                    "sys_cpu": 1.00,
                    "heap_rate": 10,
                },
                "RemoteMessageServer query worker - 12": {
                    "user_cpu": 1.00,
                    "sys_cpu": 1.00,
                    "heap_rate": 10,
                },
                "RemoteMessageServer query worker - 11": {
                    "user_cpu": 1.00,
                    "sys_cpu": 1.00,
                    "heap_rate": 10,
                },
                "RemoteMessageServer query worker - 10": {
                    "user_cpu": 1.00,
                    "sys_cpu": 1.00,
                    "heap_rate": 10,
                },
                "RemoteMessageServer query worker - 9": {
                    "user_cpu": 1.00,
                    "sys_cpu": 1.00,
                    "heap_rate": 10,
                },
                "RemoteMessageServer query worker - 8": {
                    "user_cpu": 1.00,
                    "sys_cpu": 1.00,
                    "heap_rate": 10,
                },
                "RemoteMessageServer query worker - 2": {
                    "user_cpu": 1.00,
                    "sys_cpu": 1.00,
                    "heap_rate": 10,
                },
                "RemoteMessageServer query worker - 1": {
                    "user_cpu": 1.00,
                    "sys_cpu": 1.00,
                    "heap_rate": 10,
                },
                "RemoteMessageServer query worker - 0": {
                    "user_cpu": 1.00,
                    "sys_cpu": 1.00,
                    "heap_rate": 10,
                },
                "RemoteMessageServer query worker - 7": {
                    "user_cpu": 1.00,
                    "sys_cpu": 1.00,
                    "heap_rate": 10,
                },
                "RemoteMessageServer query worker - 5": {
                    "user_cpu": 1.00,
                    "sys_cpu": 1.00,
                    "heap_rate": 10,
                },
                "RemoteMessageServer query worker - 6": {
                    "user_cpu": 1.00,
                    "sys_cpu": 1.00,
                    "heap_rate": 10,
                },
                "RemoteMessageServer query worker - 3": {
                    "user_cpu": 1.00,
                    "sys_cpu": 1.00,
                    "heap_rate": 10,
                },
                "RemoteMessageServer query worker - 4": {
                    "user_cpu": 49.00,
                    "sys_cpu": 17.00,
                    "heap_rate": 10,
                },
            }
        )
        pprint.pprint(res)
        self.assertEqual(res["RemoteMessageServer query worker "]["thread_count"], 16.0)
        self.assertEqual(res["RemoteMessageServer query worker "]["sys_cpu"], 32.0)
        self.assertEqual(res["RemoteMessageServer query worker "]["user_cpu"], 64.0)
        self.assertEqual(res["RemoteMessageServer query worker "]["heap_rate"], 160.0)

        self.assertEqual(res["My Single Thread"]["heap_rate"], 10.0)
        self.assertEqual(res["My Single Thread"]["thread_count"], 1)
        self.assertEqual(res["My Single Thread"]["user_cpu"], 1.0)
        self.assertEqual(res["My Single Thread"]["sys_cpu"], 2.0)
