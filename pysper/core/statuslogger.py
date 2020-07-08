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

""" pysper statuslogger module """
import re
from collections import defaultdict
from pysper import VERSION
from pysper import env
from pysper import parser
from pysper.diag import find_logs, UniqEventPerNodeFilter, UnknownStatusLoggerWriter
from pysper.util import get_percentiles, get_percentile_headers, node_name
from pysper.humanize import format_seconds, format_bytes, format_num, pad_table
from pysper.recs import Engine, Stage
from pysper.dates import date_parse
from pysper.core import OrderedDefaultDict

WANTED_STAGES_PREFIXES = ('TPC/all/READ', 'TPC/all/WRITE', 'Gossip', 'Messaging',
                          'Compaction', 'MemtableFlush', 'Mutation', 'Read', 'Native')
class Table:
    """ represents a dse table """
    def __init__(self, ops=0, data=0):
        self.ops = ops
        self.data = data

    def __repr__(self):
        return "%s ops / %s data" % (format_num(self.ops), format_bytes(self.data))

class Node:
    """ represents a cassandra/dse node """
    def __init__(self):
        self.start = None
        self.end = None
        self.tables = OrderedDefaultDict(Table)
        self.stages = OrderedDefaultDict(lambda: defaultdict(list))
        self.pauses = []
        self.version = None
        self.lines = 0
        self.skipped_lines = 0
        self.cassandra_version = None
        self.dumps_analyzed = 0

    def get_busiest_tables(self, by_prop):
        """ return busiest tables by_prop (data or ops) """
        return sorted(self.tables.items(), key=lambda table: getattr(table[1], by_prop), reverse=True)

    def longest_tp_name_length(self):
        """ find the length of the thread pool with the longest name """
        longest = 0
        for stage in self.stages.values():
            slen = len(max(stage, key=len))
            if slen > longest:
                longest = slen
        return longest

    def longest_tp_value_length(self):
        """ find the length of the longest value in any threadpool """
        longest = 0
        for stage in self.stages.values():
            for vals in stage.values():
                vlen = len(max(map(str, vals), key=len))
                if vlen > longest:
                    longest = vlen
        return longest

    def duration(self):
        """ duration this node was analyzed """
        return self.end - self.start

class Summary:
    """ summarizes a group of nodes """
    def __init__(self, nodes):
        if env.DEBUG:
            print(nodes)
        self.nodes = nodes
        if nodes:
            self.start = min([n.start for n in nodes.values() if n.start])
            self.end = max([n.end for n in nodes.values() if n.end])
            self.duration = self.end - self.start
        else:
            self.start, self.end, self.duration = 0, 0, 0
        self.lines = sum([n.lines for n in nodes.values()])
        self.skipped_lines = sum([n.skipped_lines for n in nodes.values()])
        self.versions = [n.version for n in nodes.values() if n.version]
        self.cassandra_versions = [n.cassandra_version for n in nodes.values() if n.cassandra_version]

    def get_busiest_tables(self, by_op):
        """ get busiest tables by_op """
        busiest = []
        for name, node in self.nodes.items():
            table = next(iter(node.get_busiest_tables(by_op)), None)
            if table:
                busiest.append([name, table])
        return sorted(busiest, key=lambda table: getattr(table[1][1], by_op), reverse=True)

    def get_busiest_stages(self):
        """ get all stages sorted by highest value """
        allstages = []
        for name, node in self.nodes.items():
            for status, stage in node.stages.items():
                for tp, vals in stage.items():
                    allstages.append([name, status, tp, next(iter(sorted(vals, reverse=True)))])
        return sorted(allstages, key=lambda x: x[3], reverse=True)

    def get_stages_in(self, status):
        """ return all stages in a given status """
        ret = {}
        for name, node in self.nodes.items():
            for stage in node.stages:
                if stage == status:
                    ret[name] = node.stages[status]
        return ret

    def get_pauses(self):
        """ get all gc pauses """
        pauses = []
        for node in self.nodes.values():
            pauses += node.pauses
        return sorted(pauses, reverse=True)

class StatusLogger:
    """ status logger """

    # pylint: disable=too-many-arguments
    def __init__(self, diag_dir, files=None, start=None, end=None, \
         wanted_stages=WANTED_STAGES_PREFIXES, command_name="sperf core statuslogger",
                 syslog_prefix="system.log", dbglog_prefix="debug.log"):
        self.diag_dir = diag_dir
        self.files = files
        self.wanted_stages = wanted_stages
        if env.DEBUG:
            print("wanted stages:", self.wanted_stages)
        self.nodes = defaultdict(Node)
        self.analyzed = False
        self.dumps_analyzed = 0
        self.rule_types = defaultdict(int)
        self.command_name = command_name
        self.syslog_prefix = syslog_prefix
        self.dbglog_prefix = dbglog_prefix
        self.start = None
        self.end = None
        if start:
            self.start = date_parse(start)
        if end:
            self.end = date_parse(end)

    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    def analyze(self):
        """ analyze log files """
        if self.analyzed:
            return
        # pylint: disable=too-many-nested-blocks
        event_filter = UniqEventPerNodeFilter()
        target = None
        if self.files:
            target = self.files
        elif self.diag_dir:
            target_system = find_logs(self.diag_dir, file_to_find=self.syslog_prefix)
            target_debug = find_logs(self.diag_dir, file_to_find=self.dbglog_prefix)
            target = target_system + target_debug
        else:
            raise Exception("no diag dir and no files specified")
        for file in target:
            nodename = node_name(file)
            event_filter.set_node(nodename)
            node = self.nodes[nodename]
            if env.DEBUG:
                print("parsing", file)
            log = open(file, 'r')
            statuslogger_fixer = UnknownStatusLoggerWriter()
            for event in parser.read_system_log(log):
                statuslogger_fixer.check(event)
                if self.start and event['date'] < self.start:
                    continue
                if self.end and event['date'] > self.end:
                    continue
                self.__setdates(node, statuslogger_fixer.last_event_date)
                node.lines += 1
                if event_filter.is_duplicate(event):
                    node.skipped_lines += 1
                    continue
                if env.DEBUG:
                    if 'rule_type' in event:
                        self.rule_types[event['rule_type']] += 1
                    elif event['event_type'] == 'unknown':
                        self.rule_types['unknown'] += 1
                    else:
                        self.rule_types['no type'] += 1
                if event['event_type'] == 'server_version':
                    if event.get('version'):
                        node.version = event['version']
                    elif event.get('cassandra_version'):
                        node.cassandra_version = event['cassandra_version']
                    #skipping solr, spark etc as it maybe too much noise for statuslogger
                elif event['event_type'] == 'memtable_status':
                    tname = '.'.join([event['keyspace'], event['table']])
                    if event['ops'] > node.tables[tname].ops:
                        node.tables[tname].ops = event['ops']
                    try:
                        if event['data'] > node.tables[tname].data:
                            node.tables[tname].data = event['data']
                    except Exception as e:
                        print(event)
                        raise e
                elif event['event_type'] == 'pause':
                    node.pauses.append(event['duration'])
                elif event['event_type'] == 'threadpool_header':
                    node.dumps_analyzed += 1
                    self.dumps_analyzed += 1
                elif event['event_type'] == 'threadpool_status':
                    if re.match(r"TPC/\d+$", event['pool_name']):
                        if not node.version:
                            node.version = "6.x"
                        if 'delayed' in event and event['delayed']:
                            print(event)
                            val = event['delayed']
                            node.stages['local backpressure'][event['pool_name']].append(val)
                    else:
                        for pool in ['active', 'pending',
                                     'blocked', 'all_time_blocked']:
                            if pool in event and event[pool]:
                                if not self.wanted_stages or event['pool_name'].startswith(self.wanted_stages):
                                    node.stages[pool][event['pool_name']].append(event[pool])
        self.analyzed = True
        if env.DEBUG:
            print(self.rule_types.items())

    def __setdates(self, node, date):
        if not node.start:
            node.start = date
            node.end = date
            return
        if date > node.end:
            node.end = date
        if date < node.start:
            node.start = date

    def print_histogram(self):
        """ print histogram report, analyzing if necessary """
        self.analyze()
        print("%s version: %s" % (self.command_name, VERSION))
        print('')
        print("Histogram")
        print('')
        if not self.nodes:
            print("Nothing found!")
            return

        for name, node in self.nodes.items():
            print(name)
            print('-'*60)
            print("%s lines" % format_num(node.lines))
            print("%s skipped lines" % format_num(node.skipped_lines))
            print("dse version: %s" % (node.version or 'unknown'))
            print("cassandra version: %s" % (node.cassandra_version or 'unknown'))
            print("log start time: %s" % node.start)
            print("log end time: %s"  % node.end)
            if not node.dumps_analyzed:
                print("Nothing found!")
                continue
            print("duration: %s" % format_seconds(int(node.duration().total_seconds())))
            print("stages analyzed: %s" % node.dumps_analyzed)
            if node.pauses:
                percentiles = [[]]
                percentiles.append(get_percentile_headers("GC pauses"))
                header = [""]
                header.extend(["---" for i in range(6)])
                percentiles.append(header)
                percentiles.append(get_percentiles("ms", node.pauses, strformat="%i"))
                pad_table(percentiles, min_width=11, extra_pad=2)
                for line in percentiles:
                    print("".join(line))
                print("total GC events: %s" % len(node.pauses))
            print('')
            ops = node.get_busiest_tables('ops')[:5]
            if ops:
                print("busiest tables (ops)")
                print('-'*30)
                nlen = max(len(o[0]) for o in ops)
                for n, t in ops:
                    print(n.ljust(nlen), t)
                data = node.get_busiest_tables('data')[:5]
                print("busiest tables (data)")
                print('-'*30)
                nlen = max(len(d[0]) for d in data)
                for n, t in data:
                    print(n.ljust(nlen), t)
            print('')
            if node.stages:
                percentiles = []
                percentiles.append(get_percentile_headers('stages'))
                percentiles.append([])
                for status, stage in node.stages.items():
                    header = [status.upper()]
                    header.extend("" for i in range(6))
                    percentiles.append(header)
                    for tpname, vals in sorted(stage.items(), key=lambda tpool: max(tpool[1]), reverse=True):
                        percentiles.append(get_percentiles(tpname, vals, strformat="%i"))
                    percentiles.append([])
                pad_table(percentiles, extra_pad=2)
                for line in percentiles:
                    print("".join(line))
        print('')
        self.__print_recs()

    def __print_recs(self):
        engine = Engine()
        recs = set()
        for node in self.nodes.values():
            rstage = defaultdict(dict)
            for status, stage in node.stages.items():
                for tpname, vals in stage.items():
                    rstage[tpname][status] = max(vals)
            for tpname in rstage:
                for sname in ('active', 'pending', 'local backpressure',
                              'completed', 'blocked', 'all_time_blocked'):
                    if not sname in rstage[tpname]:
                        rstage[tpname][sname] = 0
                s = Stage(tpname, rstage[tpname]['active'], rstage[tpname]['pending'],
                          rstage[tpname]['local backpressure'], rstage[tpname]['completed'], rstage[tpname]['blocked'],
                          rstage[tpname]['all_time_blocked'])
                reason, rec = engine.analyze_stage(s)
                if reason:
                    recs.add((rec, reason))
        if recs:
            print("recommmendations")
            print("----------------")
        for rec, reason in recs:
            print("* %s (%s)" % (rec, reason))

    # pylint: disable=too-many-locals
    def print_summary(self):
        """ prints a summary report """
        self.analyze()
        summary = Summary(self.nodes)
        print("%s version: %s" % (self.command_name, VERSION))
        print('')
        print("Summary (%s lines)" % format_num(summary.lines))
        print("Summary (%s skipped lines)" % format_num(summary.skipped_lines))
        print('')
        print("dse versions: %s" % (set(summary.versions) or 'unknown'))
        print("cassandra versions: %s" % (set(summary.cassandra_versions) or 'unknown'))
        print("first log time: %s" % summary.start)
        print("last log time: %s" % summary.end)
        if not self.dumps_analyzed:
            print("Nothing found!")
            return
        print("duration: %s" % format_seconds(int(summary.duration.total_seconds())))
        print("total stages analyzed: %s" % self.dumps_analyzed)
        print("total nodes analyzed: %s" % len(summary.nodes))
        pauses = summary.get_pauses()
        if pauses:
            print('')
            percentiles = []
            percentiles.append(get_percentile_headers("GC pauses"))
            percentiles.append(["", "---", "---", "---", "---", "---", "---"])
            percentiles.append(get_percentiles("ms", pauses, strformat="%i"))
            pad_table(percentiles, min_width=11, extra_pad=2)
            for line in percentiles:
                print("".join(line))
            print("total GC events: %s" % len(pauses))
        print('')
        ops = summary.get_busiest_tables('ops')[:5]
        if ops:
            print("busiest tables by ops across all nodes")
            print('-'*30)
            for onode, (oname, num) in ops:
                print("* %s: %s: %s" % (onode, oname, num))
            print('')
            print("busiest table by data across all nodes")
            print('-'*30)
            for dnode, (dname, data) in summary.get_busiest_tables('data')[:5]:
                print("* %s: %s: %s" % (dnode, dname, data))
            print('')
        print("busiest stages across all nodes")
        print('-'*30)
        data = []
        for (name, status, stage, value) in summary.get_busiest_stages():
            data.append(["* %s %s:" % (stage, status), str(value), "(%s)" % name])
        pad_table(data, extra_pad=2)
        for line in data:
            print("".join(line))
        pending = summary.get_stages_in('pending')
        data = []
        if pending:
            data.append([])
            self.__print_stages('pending', pending, data)
        delayed = summary.get_stages_in('local backpressure')
        if delayed:
            data.append([])
            self.__print_backpressure(delayed, data)
        data.append([])
        pad_table(data, extra_pad=2)
        for line in data:
            print("".join(line))
        self.__print_recs()

    def __print_backpressure(self, stages, data):
        nodes = {}
        #get total backpressure and max backpressure per node
        for name, stage in stages.items():
            if name not in nodes:
                #if not present initialize so aggregate code can safely assume 0 value is already populated
                nodes[name] = {"total": 0, "count": 0, "max": 0}
            node_agg = nodes[name]
            for vals in  stage.values():
                node_agg["count"] += len(vals)
                node_agg["total"] += sum(vals)
                node_agg["max"] = max(max(vals), node_agg["max"])
        data.append(['busiest LOCAL BACKPRESSURE'])
        data.append(['-'*30])
        # sort to make the node with the worst backpressure total first
        for name, val in sorted(nodes.items(), key=lambda kvp: kvp[1]["total"]/float(kvp[1]["count"]), reverse=True):
            data.append(["%s:" % name])
            avg_backpressure = val["total"]/float(val["count"])
            data.append([" "*5, "avg backpressure", "%.2f" % avg_backpressure])
            data.append([" "*5, "max backpressure", str(nodes[name]["max"])])

    def __print_stages(self, status, stages, data):
        data.append(['busiest stages in %s' % status.upper()])
        data.append(['-'*30])
        # sort to make the worst node first
        for name, stage in sorted(stages.items(), key=lambda tpool: max(tpool[1].values()), reverse=True):
            data.append(["%s:" % name])
            # sort again to make the worst stage on the node first
            for tp, vals in sorted(stage.items(), key=lambda stg: max(stg[1]), reverse=True):
                data.append([" "*5, "%s:" % tp, str(max(vals))])
