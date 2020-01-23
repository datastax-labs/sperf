"""test the read_ahead module"""
from pysper.core.diag import read_ahead

def test_block_dev():
    """test parsing the block dev report"""
    rows = [
        {"ssz": 512, "ra": 8, "device": "/dev/sda"},
        {"ssz": 512, "ra": 8192, "device": "/dev/sdb"},
    ]
    devices = read_ahead.extract_block_dev(rows)
    assert len(devices) == 2
    assert devices.get("/dev/sda") == 4096
    assert devices.get("/dev/sdb") == 4194304
