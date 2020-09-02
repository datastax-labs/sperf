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
ParkedThreadsMonitor                               4       23.52 -----------------
RMI TCP Connection(2)                              4       2.90  --
CoreThread                                         20      1.20  -
DseGossipStateUpdater                              4       0.10
ScheduledTasks                                     4       0.08
NodeHealthPlugin-Scheduler-thread                  4       0.06
OptionalTasks                                      4       0.05
JMX server connection timeout 425                  4       0.04
ContainerBackgroundProcessor[StandardEngine[Solr]] 4       0.02
PO-thread                                          4       0.02
GossipTasks                                        4       0.01
AsyncAppender-Worker-ASYNCDEBUGLOG                 4       0.01
LeasePlugin                                        4       0.01
NonPeriodicTasks                                   4       0.01
RxSchedulerPurge                                   4       0.01
internode-messaging RemoteMessageServer acceptor   4       0.00""",
            output,
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
            """================================================================================
CoreThread                                         20      2.14 mb   -------------
RMI TCP Connection(2)                              4       1.14 mb   -------
DseGossipStateUpdater                              4       38.00 kb
ScheduledTasks                                     4       24.00 kb
NodeHealthPlugin-Scheduler-thread                  4       19.00 kb
ContainerBackgroundProcessor[StandardEngine[Solr]] 4       6.01 kb
JMX server connection timeout 425                  4       4.18 kb
PO-thread                                          4       2.47 kb
AsyncAppender-Worker-ASYNCDEBUGLOG                 4       1.90 kb
LeasePlugin                                        4       1.38 kb
NonPeriodicTasks                                   4       1.07 kb
GossipTasks                                        4       841 bytes
RxSchedulerPurge                                   4       710 bytes
OptionalTasks                                      4       323 bytes
ParkedThreadsMonitor                               4       317 bytes
internode-messaging RemoteMessageServer acceptor   4       0 byte""",
            output,
        )
