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

"""module for the filtercache report"""
import functools
import sys
from collections import OrderedDict
from operator import attrgetter, itemgetter
from pysper import dates, diag, parser, util, humanize, recs

def sort_evict_freq(first_block, second_block):
    """sorts in ascending order if value is greater than 0
    , otherwise all 0 values are placed last"""
    first = first_block.avg_evict_freq
    second = second_block.avg_evict_freq
    if first == 0.0 and second == 0.0:
        return 0
    if first == 0:
        return sys.float_info.min
    if second == 0:
        return float("inf")
    return first - second

class NodeReportBlock:
    """each row in the final report for final stats"""
    def __init__(self, first_evict, last_evict, name):
        self.name = name
        min_utc_time = dates.min_utc_time()
        max_utc_time = dates.max_utc_time()
        if last_evict == min_utc_time:
            first_evict = min_utc_time
            last_evict = min_utc_time
        if first_evict == max_utc_time:
            first_evict = min_utc_time
            last_evict = min_utc_time
        self.evict_range = (last_evict - first_evict).total_seconds() * 1000
        self.log_duration = 0
        self.byte_limit = 0
        self.last_byte_limit = last_evict
        self.item_limit = 0
        self.last_item_limit = 0
        self.avg_evict_duration = 0.0
        self.avg_evict_freq = 0.0

    def __repr__(self):
        """string representation for debugging"""
        return "name %s freq: %.2f duration: %.2f byte limit: %i item limit: %i logs ms: %i" % \
                (self.name, self.avg_evict_freq, self.avg_evict_duration, self.byte_limit, \
                self.item_limit, self.evict_range)

class BytesFCStats:
    """represents a single bytes based filter cache eviction"""

    def __init__(self, event):
        self.name = "byte"
        self.time_stamp = event.get("date")
        self.fc_id = event.get("id")
        self.duration = 0
        self.usage_after = None
        self.usage_after_unit = None
        self.maximum = event.get("maximum", 0)
        self.maximum_unit = event.get("maximum_unit", "GB")

    def add_duration_event(self, event):
        """adds the duration event to the stats"""
        self.duration = event.get("duration", 0)
        self.usage_after = event.get("usage", 0)
        self.usage_after_unit = 'bytes'

    def __repr__(self):
        """string verion of fc stats"""
        return "name: byte ts: %s id: %s duration: %i" % \
                (self.time_stamp, self.fc_id, self.duration)

class ItemFCStats:

    """represents a single item based filter cache eviction"""
    def __init__(self, event):
        self.name = "item"
        self.time_stamp = event.get("date")
        self.fc_id = event.get("id")
        self.entries = event.get("entries")
        self.maximum = event.get("maximum", 0)
        self.duration = 0
        self.usage = None
        self.usage_unit = None

    def add_duration_event(self, event):
        """adds the duration event to the stats"""
        self.duration = event.get("duration", 0)
        self.usage = event.get("usage", 0)
        self.usage_unit = event.get("usage_unit", "GB")

    def __repr__(self):
        """string verion of fc stats"""
        return "name: item ts: %s id: %s duration: %i" % \
                (self.time_stamp, self.fc_id, self.duration)

def _get_stats(events, ctor, key_name):
    """adds the corresponding duration event. 
    Note the the get_id hack is error prone when spanning logs as half an event could not finish
    """
    eviction_stats = {event.get("id", i): ctor(event) for (i, event) \
                      in enumerate([event for event in events if event.get('event_type', '') == key_name])
                     }
    duration_stats = {event.get("id", i): event for (i, event) \
                      in enumerate([event for event in events if event.get('event_type', '') == (key_name + "_duration")])
                     }
    for key, stats in eviction_stats.items():
        duration_event = duration_stats.get(key)
        if not duration_event:
            duration_event = OrderedDict()
        stats.add_duration_event(duration_event)
    return eviction_stats

def parse(args):
    """parse entry point, generates a report object
    from a tarball or series of files"""
    logs = diag.find_files(args, args.system_log_prefix)
    print("from directory '%s':" % args.diag_dir)
    node_stats = OrderedDict()
    after_time = dates.date_parse(args.after)
    before_time = dates.date_parse(args.before)
    for log in logs:
        start_log_time, last_log_time = diag.log_range(log)
        with diag.FileWithProgress(log) as log_file:
            raw_events = parser.read_system_log(log_file)
            filter_cache_events_all = [event for event in raw_events \
                                   if event.get('event_category', '') == 'filter_cache']
            filter_cache_events = [event for event in filter_cache_events_all \
                                   if 'date' in event and event['date'] > after_time and event['date'] < before_time]
            item_eviction_stats = _get_stats(filter_cache_events, ItemFCStats, 'eviction_items')
            bytes_eviction_stats = _get_stats(filter_cache_events, BytesFCStats, 'eviction_bytes')
            node = util.extract_node_name(log, True)
            node_stats[node] = OrderedDict([("evictions" , (bytes_eviction_stats, item_eviction_stats)), \
                ("start", start_log_time), ("end", last_log_time), \
                ])
    return OrderedDict([ \
            ("nodes", node_stats), \
            ("after_time", after_time), \
            ("before_time", before_time), \
            ])

def create_report_block(first_evict, last_evict, events, log_duration, name):
    """creates the report block for the node"""
    report_block = NodeReportBlock(first_evict, last_evict, name)
    report_block.log_duration = log_duration
    stats = [stat for event in events for stat in event.values() if stat.duration > 0]
    byte_evictions = [stat for stat in stats if stat.name == "byte"]
    byte_limit = len(byte_evictions)
    item_evicitions = [stat for stat in stats if stat.name == "item"]
    item_limit = len(item_evicitions)
    total_evictions = byte_limit + item_limit
    duration = sum([x.duration for x in stats])
    report_block.avg_evict_freq = float(report_block.evict_range)/float(total_evictions) \
            if report_block.evict_range and total_evictions else 0.0
    report_block.avg_evict_duration = float(duration)/float(total_evictions) \
            if duration and total_evictions else 0.0
    report_block.item_limit = item_limit
    report_block.byte_limit = byte_limit
    report_block.last_item_limit = item_evicitions[-1].maximum if item_evicitions else 0
    report_block.last_byte_limit = humanize.to_bytes(byte_evictions[-1].maximum, \
            byte_evictions[-1].maximum_unit) if byte_evictions else 0
    return report_block

def calculate_report(parsed):
    """generates calculations"""
    start_log = dates.max_utc_time()
    last_log = dates.min_utc_time()
    #make this it's own method
    node_info_agg = []
    for node, events in parsed["nodes"].items():
        node_end_time = events.get("end")
        before_time = parsed["before_time"]
        if before_time != dates.max_utc_time() and node_end_time > before_time:
            node_end_time = before_time
        if node_end_time > last_log:
            last_log = node_end_time
        node_start_time = events.get("start")
        after_time = parsed["after_time"]
        if after_time != dates.min_utc_time() and node_start_time < after_time:
            node_start_time = after_time
        if node_start_time < start_log:
            start_log = node_start_time
        log_duration = (node_end_time - node_start_time).total_seconds() * 1000
        first_node_evict = dates.max_utc_time()
        last_node_evict = dates.min_utc_time()
        for info in events.get("evictions"):
            for value in info.values():
                if value.time_stamp > last_node_evict:
                    last_node_evict = value.time_stamp
                if value.time_stamp < first_node_evict:
                    first_node_evict = value.time_stamp
        if log_duration < 0:
            log_duration = 0
        node_info_agg.append(create_report_block(first_node_evict, \
                last_node_evict, events.get("evictions"), log_duration, node))
    node_info_agg = sorted(node_info_agg, key=attrgetter('name'))
    node_info_agg = sorted(node_info_agg, key=attrgetter('avg_evict_duration'), reverse=True)
    node_info_agg = sorted(node_info_agg, key=functools.cmp_to_key(sort_evict_freq))
    return OrderedDict([
        ("start_log", start_log),
        ("last_log", last_log),
        ("node_info", node_info_agg),
        ])

def generate_recommendations(report, node_info):
    """generate recommendations and add them to report"""
    report.append("recommendations")
    report.append("---------------")
    # generate recommendations
    fc_recs = OrderedDict()
    for node in node_info:
        key = recs.analyze_filter_cache_stats(node)
        if key[0] and key[1]:
            if key not in fc_recs:
                fc_recs[key] = []
            fc_recs[key].append(node.name)
    if not fc_recs:
        report.append("No recommendations\n")
        return
    sorted_recs = []
    for rec in fc_recs:
        nodes = fc_recs[rec]
        sorted_recs.append((rec[0], rec[1], nodes, len(nodes)))
    sorted(sorted_recs, key=itemgetter(3), reverse=True)
    if len(sorted_recs) > 1:
        report.append("NOTE: Do top recommendation first.")
        report.append("")
    for rec in sorted_recs:
        nodes_fmtd = humanize.format_list(rec[2], newline="\n" + " " * 17) #allows nodes to be tabbed out for a block look
        report.append("* affects nodes: %s\n  reason: %s\n  fix: %s" % (nodes_fmtd, rec[0], rec[1]))
    report.append("")

def generate_report(parsed):
    """generates a report from the result of parsing a
    tarball or series of files"""
    calculated = calculate_report(parsed)
    report = []
    report.append("")
    report.append("NOTE: as of version 0.3.13 all evictions with duration of 0 ms " + \
            "are deducted from the item eviction count and are not part of the " + \
            "eviction freq or duration calculations")
    report.append("")
    if not calculated.get('start_log'):
        report.append("start log: 'None'")
    else:
        report.append("start log: '%s'" % \
            calculated.get('start_log').strftime(dates.CASSANDRA_LOG_FORMAT))
    if not calculated.get('last_log'):
        report.append("end log: 'None'")
    else:
        report.append("end log:   '%s'" % \
                calculated.get('last_log').strftime(dates.CASSANDRA_LOG_FORMAT))
    report.append("")
    node_info = calculated.get('node_info', [])
    generate_recommendations(report, node_info)
    if not node_info:
        return "\nNo Logs Found For Processing\n"
    table = []
    table.append(["node", "Avg time between evictions", "Avg eviction duration",  \
            "Times (byte/item) limit reached", "Most recent limit (byte/item)", "Log duration"])
    table.append(["----", "--------------------------", "---------------------", \
            "-------------------------------", "-----------------------------", "------------"])
    for node in node_info:
        table.append([node.name, humanize.format_millis(node.avg_evict_freq), \
                humanize.format_millis(node.avg_evict_duration), \
                "%i/%i" % \
                (node.byte_limit, node.item_limit), \
                "%s/%i" % \
                (humanize.format_bytes(node.last_byte_limit), node.last_item_limit), \
                humanize.format_millis(node.log_duration)])
    humanize.pad_table(table)
    for row in table:
        report.append("  ".join(row))
    report.append("") #provides empty line after last line
    return "\n".join(report)
