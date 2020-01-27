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

""" pysper gc inspector module """
import heapq
import itertools
import datetime
from collections import defaultdict
from pysper import parser
from pysper.parser import gc
from pysper import VERSION
from pysper.diag import find_logs
from pysper.util import node_name, bucketize, get_percentiles, get_percentile_headers
from pysper.dates import date_parse
from pysper.humanize import pad_table

class GCInspector:
    """ GCInspector class """
    def __init__(self, diag_dir=None, files=None, start=None, end=None):
        self.diag_dir = diag_dir
        self.files = files
        self.pauses = defaultdict(lambda: defaultdict(list))
        self.gc_types = defaultdict(int)
        self.start = None
        self.end = None
        self.starts = defaultdict(datetime.datetime)
        self.ends = defaultdict(datetime.datetime)
        self.analyzed = False
        self.start_time = None
        self.end_time = None
        if start:
            self.start_time = date_parse(start)
        if end:
            self.end_time = date_parse(end)

    def analyze(self):
        """ analyze files """
        target = None
        if self.files:
            target = self.files
        elif self.diag_dir:
            target = find_logs(self.diag_dir)
        else:
            raise Exception("no diag dir and no files specified")
        for file in target:
            node = node_name(file)
            log = open(file, 'r')
            for event in parser.read_log(log, gc.capture_line):
                if event['event_type'] == 'pause':
                    if self.start_time and event['date'] < self.start_time:
                        continue
                    if self.end_time and event['date'] > self.end_time:
                        continue
                    self.__setdates(event['date'], node)
                    self.pauses[node][event['date']].append(event['duration'])
                    self.gc_types[event['gc_type']] += 1
        self.analyzed = True

    def __setdates(self, date, node):
        """ track start/end times """
        # global
        if not self.start:
            self.start = date
            self.end = date
        if date > self.end:
            self.end = date
        if date < self.start:
            self.start = date
        # node specific
        if not node in self.starts:
            self.starts[node] = date
            self.ends[node] = date
            return
        if date > self.ends[node]:
            self.ends[node] = date
        if date < self.starts[node]:
            self.starts[node] = date

    def all_pauses(self):
        """ get pauses for all nodes """
        pauses = defaultdict(list)
        for pausedata in self.pauses.values():
            for time, pause in pausedata.items():
                pauses[time].extend(pause)
        return pauses

    def print_report(self, interval=3600, by_node=False, top=3):
        """ print gc report """
        print("gcinspector version %s" % VERSION)
        print('')
        if not self.analyzed:
            self.analyze()
        if not self.pauses:
            print("No pauses found")
            return
        if not by_node:
            pauses = self.all_pauses()
            self.__print_gc(sorted(bucketize(pauses,
                                             start=self.start, end=self.end, seconds=interval).items(),
                                   key=lambda t: t[0]))
            plist = []
            for time in pauses:
                plist.extend(pauses[time])
            worst_k = heapq.nlargest(top, plist)
            print("Worst pauses in ms:")
            print(worst_k)

        else:
            for node in self.pauses:
                print(node)
                self.__print_gc(sorted(
                    bucketize(self.pauses[node],
                              start=self.starts[node], end=self.ends[node], seconds=interval).items(),
                    key=lambda t: t[0]))
                plist = []
                for time, pauses in self.pauses[node].items():
                    plist.extend(pauses)
                worst_k = heapq.nlargest(top, plist)
                print("Worst pauses in ms:")
                print(worst_k)
                print('')
        print('')
        print("Collections by type")
        print('-'*20)
        for collection, count in self.gc_types.items():
            print("* %s: %s" % (collection, count))
        print('')

    def __print_gc(self, data):
        """ print data to the user, expecting datetime keys and list(int) values """
        print(". <300ms + 301-500ms ! >500ms")
        print('-'*30)
        busiest = None
        for time, pauses in data:
            total = sum(pauses)
            if not busiest:
                busiest = (time, total)
            elif total > busiest[1]:
                busiest = (time, total)
            print(time.strftime("%Y-%m-%d %H:%M:%S"), end=' ')
            print(len(pauses), end=' ')
            for pause in pauses:
                c = '.'
                if pause > 300:
                    c = '+'
                if pause > 500:
                    c = '!'
                print(c, end='')
            print('')
        print('')
        print('busiest period: %s (%sms)' % (busiest[0].strftime("%Y-%m-%d %H:%M:%S"), busiest[1]))
        print('')
        percentiles = [[]]
        percentiles.append(get_percentile_headers("GC pauses"))
        header = [""]
        header.extend(["---" for i in range(6)])
        percentiles.append(header)
        percentiles.append(get_percentiles("ms", list(itertools.chain.from_iterable(
            pauses for time, pauses in data)), strformat="%i"))
        pad_table(percentiles, min_width=11, extra_pad=2)
        for line in percentiles:
            print("".join(line))
        print()
