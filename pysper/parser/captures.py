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

""" capture rules """
from pysper.parser.rules import capture

#pylint: disable=line-too-long
system_capture_rule = capture(
        r' *(?P<level>[A-Z]*) *\[(?P<thread_name>[^\]]*?)[:_-]?(?P<thread_id>[0-9]*)\] (?P<date>.{10} .{12}) *(?P<source_file>[^:]*):(?P<source_line>[0-9]*) - (?P<message>.*)',
        r' *(?P<level>[A-Z]*) \[(?P<thread_name>[^\]]*?)[:_-]?(?P<thread_id>[0-9]*)\] (?P<date>.{10} .{12}) (?P<source_file>[^ ]*) \(line (?P<source_line>[0-9]*)\) (?P<message>.*)',
        #db-2552 5.x format
        #ReadStage                         0         0        4248543         0                 0
        r'^(?P<pool_name>[A-Za-z_-]+) +((?P<active>[0-9]+)|n\/a) +(?P<pending>[0-9]+)(\/(?P<pending_responses>[0-9]+))?( +(?P<completed>[0-9]+) +(?P<blocked>[0-9]+) +(?P<all_time_blocked>[0-9]+))$',
        #db-2552 5.x header format
        #Pool Name                    Active   Pending      Completed   Blocked  All Time Blocked
        r'^(?P<header>.*) Name +Active +Pending +Completed +Blocked  +All Time Blocked$',
        #db-2552 statuslogger format
        r'^(?P<pool_name>[A-Za-z0-9_/#]+) +((?P<active>[0-9]+)|n/a) +(?P<pending>[0-9]+) +\(((?P<backpressure>[0-9]+)|N/A)\) +((?P<delayed>[0-9]+)|N/A) +(?P<completed>[0-9]+) +((?P<blocked>[0-9]+)|N/A) +(?P<all_time_blocked>[0-9]+)$',
        #db-2552 statuslogger header format
        r'^(?P<header>.*) Name +Active +Pending \(w/Backpressure\) +(?P<delayed_header>.*) +Completed +Blocked +All Time Blocked$',
        #db-2552 table header format ColumnFamily matches column_family_header
        r'^(?P<column_family_header>.*) +Memtable ops,data',
        #db-2552 table format
        r'^(?P<keyspace>[^.]*)\.(?P<table>[^ ]*) +(?P<ops>[0-9]*),(?P<data>[0-9]*)$',
        #db-2552 cache header format
        r'^(?P<cache_header>.*) Type +Size +Capacity +KeysToSave\(Provider\)?$',
        #db-2552 cache format
        r'^(?P<cache_type>[A-Za-z]*Cache(?! Type)) *(?P<size>[0-9]*) *(?P<capacity>[0-9]*) *(?P<keys_to_save>[^ ]*) *(?P<provider>[A-Za-z_.$]*)$'
        )

output_capture_rule = capture(
        #INFO  [main] 2019-06-21 02:59:14,304  DatabaseDescriptor.java:418 - DiskAccessMode is standard, indexAccessMode is standard, commitlogAccessMode is standard
        r' *(?P<level>[A-Z]*) *\[(?P<thread_name>[^\]]*?)[:_-]?(?P<thread_id>[0-9]*)\] (?P<date>.{10} .{12}) *(?P<source_file>[^:]*):(?P<source_line>[0-9]*) - (?P<message>.*)',
        r' *(?P<level>[A-Z]*) \[(?P<thread_name>[^\]]*?)[:_-]?(?P<thread_id>[0-9]*)\] (?P<date>.{10} .{12}) (?P<source_file>[^ ]*) \(line (?P<source_line>[0-9]*)\) (?P<message>.*)',
        #format with no thread
        r' *(?P<level>[A-Z]*) *(?P<date>.{12}) *(?P<source_file>[^:]*):(?P<source_line>[0-9]*) - (?P<message>.*)',
        #short format
        r'(?P<level>[A-Z]*) *\s(?P<date>.{12}) *\s(?P<message>.*)'
        )
