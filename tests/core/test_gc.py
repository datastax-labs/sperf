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

""" tests the gcinspector module """
import os
import pytest
from pysper.core.gcinspector import GCInspector
from tests import steal_output, test_dse_tarball

@pytest.mark.skipif(os.environ.get("TEST_LEVEL") == "fast", reason="fast mode")
def test_gcinspector():
    """ test gcinspector analysis """
    g = GCInspector(test_dse_tarball())
    g.analyze()
    assert len(g.pauses) == 3
    assert len(g.all_pauses()) == 236
    output = steal_output(g.print_report)
    assert '!!++.+.+.!++.+.+...+.+..+.+.+.+..+++....++..+++....+..++.+++.+!+..+.+.+.+!......+++....+' in output
