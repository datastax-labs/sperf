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

"""handles the read ahead"""
import json
from pysper import util, parser, diag

def add_block_dev_to_config(cass_drive_ra, node_configs):
    """adds the block dev configuration to the configuration statistics"""
    for node, drive_map in cass_drive_ra.items():
        if node in node_configs:
            node_configs[node]['cass_ra'] = sorted(drive_map.values())

def get_cass_drive_read_ahead(node_info_json, block_dev_reports):
    """searches node_info_json for drive mappings and reports on cass drive read ahead settings"""
    node_info = json.load(node_info_json)
    nodes_cass_drives = {}
    if not node_info:
        return {}
    for node in node_info:
        drives = {}
        drive_data = node_info.get(node, {}).get('partitions', {}).get('data', {})
        if drive_data is None:
            continue
        for drive in drive_data:
            #rename that reverses opscenter behavior if there is a match present
            drive = drive.replace("_", "-")
            drives[drive] = None
            nodes_cass_drives[node] = drives
    for block_dev_report in block_dev_reports:
        node_name = util.extract_node_name(block_dev_report)
        if node_name in nodes_cass_drives:
            with diag.FileWithProgress(block_dev_report) as block_dev_file:
                row_gen = parser.read_block_dev(block_dev_file)
                drives = extract_block_dev(row_gen)
                for drive, ra_bytes in drives.items():
                    if drive in nodes_cass_drives[node_name]:
                        nodes_cass_drives[node_name][drive] = ra_bytes
    return nodes_cass_drives

def extract_block_dev(block_dev_report):
    """pulls device, ssz and ra out of each row to create a map of device and read ahead in bytes"""
    drives = {}
    for row in block_dev_report:
        device = row.get('device')
        if not device:
            continue
        read_ahead = row.get('ra')
        ssz = row.get('ssz')
        drives[device] = read_ahead * ssz
    return drives
