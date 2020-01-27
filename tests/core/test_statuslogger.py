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

""" tests the statuslogger module """
from pysper.core.statuslogger import StatusLogger, Summary
from tests import test_dse_tarball

def test_skip_duplicate_events_diag():
    """should merge events on the same node in different logs"""
    sl = StatusLogger(test_dse_tarball())
    sl.analyze()
    assert sl.analyzed
    assert len(sl.nodes) == 3
    s = Summary(sl.nodes)
    assert s.lines == 22054
    assert s.skipped_lines == 444
    assert s.get_busiest_stages()[0] == ['10.101.35.102', 'active', 'CompactionExecutor', 1]
