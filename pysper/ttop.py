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

""" ttop file analyzer """
import re
from collections import OrderedDict
from pysper.parser.rules import date
from pysper.util import textbar
from pysper.dates import date_parse
from pysper.humanize import format_bytes
from pysper import env, VERSION
from pysper.core import OrderedDefaultDict

class TTopParser:
    """ parses ttop output files """
    BEGIN = 'begin'
    PROCESS = 'process'
    APPLICATION = 'application'
    OTHER = 'other'
    THREAD = 'thread'
    HEAP = 'heap'
    TINFO = 'tinfo'

    # pylint: disable=line-too-long

    # 2019-08-29T13:08:03.605+0000 Process summary
    begin_match = re.compile(r'(?P<date>.{10}T.{17}) Process summary')
    # process cpu=602.43%
    process_match = re.compile(r' +process cpu=(?P<cpu_total>-?[0-9]+.[0-9]+)%')
    # application cpu=586.44% (user=350.39% sys=236.05%)
    application_match = re.compile(r' +application cpu=(?P<app_cpu>-?[0-9]+\.[0-9]+)% \(user=(?P<user_cpu>-?[0-9]+\.[0-9]+)% sys=-?(?P<sys_cpu>[0-9]+\.[0-9]+)%\)')
    #   other: cpu=15.98%
    other_match = re.compile(r' +other: cpu=(?P<other_cpu>-?[0-9]+\.[0-9]+)')
    #   thread count: 444
    thread_match = re.compile(r' +thread count: (?P<thread_count>[0-9]+)')
    #  heap allocation rate 435mb/s
    heap_match = re.compile(r' +heap allocation rate (?P<heap_rate>[0-9]+)(?P<heap_unit>[m|k]?b)/s')
    # [001900] user= 4.87% sys= 5.52% alloc= 2172kb/s - RMI TCP Connection(184)-127.0.0.1
    tinfo_match = re.compile(r' *\[(?P<thread_id>[0-9]+)\] user= *(?P<user_cpu>-?[0-9]+\.[0-9]+)% sys= *(?P<sys_cpu>-?[0-9]+\.[0-9]+)% alloc= *(?P<heap_rate>[0-9]+)(?P<heap_unit>[m|k]?b)/s - (?P<thread_name>.+)')

    def __init__(self, start=None, end=None):
        self.state = None
        self.start = None
        self.end = None
        if start:
            self.start = date_parse(start)
        if end:
            self.end = date_parse(end)

    # pylint: disable=too-many-statements, too-many-branches
    def parse(self, log):
        """ parse ttop output """
        total = OrderedDict()
        threads = OrderedDefaultDict(dict)
        for line in log:
            if self.state is None:
                m = self.begin_match.match(line)
                if m:
                    dt = date('%Y-%m-%dT%H:%M:%S.%f%z')(m.group('date'))
                    if self.start and dt < self.start:
                        continue
                    if self.end and dt > self.end:
                        continue
                    total['date'] = dt
                    self.state = self.BEGIN
                    continue
            if self.state == self.BEGIN:
                m = self.process_match.match(line)
                if not m:
                    raise ValueError("process line not found in " + line)
                self.state = self.PROCESS
                total['cpu_total'] = float(m.group('cpu_total'))
                continue
            if self.state == self.PROCESS:
                m = self.application_match.match(line)
                if not m:
                    raise ValueError("application line not found in " + line)
                self.state = self.APPLICATION
                total['app_cpu'] = float(m.group('app_cpu'))
                total['user_cpu'] = float(m.group('user_cpu'))
                total['sys_cpu'] = float(m.group('sys_cpu'))
                continue
            if self.state == self.APPLICATION:
                m = self.other_match.match(line)
                if not m:
                    raise ValueError("other line not found in '" + line + "'")
                self.state = self.OTHER
                total['other_cpu'] = float(m.group('other_cpu'))
                continue
            if self.state == self.OTHER:
                m = self.thread_match.match(line)
                if not m:
                    raise ValueError("thread line not found in '" + line + "'")
                self.state = self.THREAD
                total['thread_count'] = int(m.group('thread_count'))
                continue
            if self.state == self.THREAD:
                m = self.heap_match.match(line)
                if not m:
                    raise ValueError("heap line not found in '" + line + "'")
                self.state = self.TINFO
                total['heap_rate'] = self.convert(m.group('heap_rate'), m.group('heap_unit'))
                continue
            if self.state == self.TINFO:
                if line == '\n':
                    self.state = None
                    yield total, threads
                    total = OrderedDict()
                    threads = OrderedDefaultDict(dict)
                else:
                    m = self.tinfo_match.match(line)
                    if not m:
                        raise ValueError("thread info not found in '" + line + "'")
                    threads[m.group('thread_name')]['user_cpu'] = float(m.group('user_cpu'))
                    threads[m.group('thread_name')]['sys_cpu'] = float(m.group('sys_cpu'))
                    threads[m.group('thread_name')]['total_cpu'] = float(m.group('sys_cpu')) + float(m.group('user_cpu'))
                    threads[m.group('thread_name')]['heap_rate'] = self.convert(m.group('heap_rate'), m.group('heap_unit'))
                    continue

    def convert(self, rate, unit):
        """ converts rate to bytes """
        if unit == 'mb':
            return int(rate) * 1024 * 1024
        if unit == 'kb':
            return int(rate) * 1024
        return int(rate)

class TTopAnalyzer:
    """ analyzes ttop info """

    def __init__(self, files):
        self.files = files

    def collate_threads(self, threads):
        """ combines similar threads """
        ret = OrderedDefaultDict(lambda: OrderedDefaultDict(float))
        exprs = []
        exprs.append(r':.*')
        exprs.append(r'-\d+.*')
        exprs.append(r'-\/.*')
        for thread in threads:
            name = thread
            for e in exprs:
                name = re.sub(e, '', name)
            for t, v in threads[thread].items():
                ret[name][t] = round(ret[name][t] + v, 2)
                ret[name]['thread_count'] += 1
        return ret

    # pylint: disable=too-many-locals, too-many-arguments, too-many-branches
    def print_report(self, top=None, alloc=False, collate=True, start=None, end=None):
        """ analyze and report on ttop files """
        parser = TTopParser(start=start, end=end)
        print("ttop version %s" % VERSION)
        print()
        for file in self.files:
            log = open(file, 'r')
            if env.DEBUG:
                print("parsing", file)
            for total, threads in parser.parse(log):
                if alloc:
                    print('{0:<40} {1:<10} {2:<10} {3:<10}'.format(total['date'].strftime("%Y-%m-%d %H:%M:%S"),
                                                                   'Threads', 'Alloc/s',
                                                                   "Total: " + format_bytes(total['heap_rate'])))
                else:
                    print('{0:<40} {1:<10} {2:<10} {3:<10}'.format(total['date'].strftime("%Y-%m-%d %H:%M:%S"),
                                                                   'Threads', 'CPU%',
                                                                   "Total: " + str(total['app_cpu']) + '%'))
                print('='*80)
                combined = threads
                if collate:
                    combined = self.collate_threads(threads)
                ordered = []
                if alloc:
                    ordered = sorted(combined.items(), key=lambda k: k[1]['heap_rate'], reverse=True)
                else:
                    ordered = sorted(combined.items(), key=lambda k: k[1]['total_cpu'], reverse=True)
                if top:
                    ordered = ordered[0:top]
                for name, value in ordered:
                    count = 1
                    if collate:
                        count = int(value['thread_count'])
                    if alloc:
                        print('{0:<40} {1:<10} {2:<10} {3:<10}'.format(name, count, format_bytes(value['heap_rate']),
                                                                       textbar(total['heap_rate'], value['heap_rate'])))
                    else:
                        print('{0:<40} {1:<10} {2:<10} {3:<10}'.format(name, count, value['total_cpu'],
                                                                       textbar(total['app_cpu'], value['total_cpu'])))
                print()
