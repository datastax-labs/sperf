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
