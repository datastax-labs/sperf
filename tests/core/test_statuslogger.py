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
