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
