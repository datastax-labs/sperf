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

""" analyzes debug.logs for slow queries """
import re
from collections import defaultdict
import numpy as np
from pysper.diag import find_logs
from pysper.parser.rules import date
from pysper.util import bucketize
from pysper.dates import date_parse
from pysper import VERSION

class SlowQueryParser:
    """ parses logs for slow queries """
    BEGIN = 'begin'
    # pylint: disable=line-too-long
    begin_match = re.compile(r' *(?P<level>[A-Z]*) *\[(?P<thread_name>[^\]]*?)[:_-]?(?P<thread_id>[0-9]*)\] (?P<date>.{10} .{12}) *(?P<source_file>[^:]*):(?P<source_line>[0-9]*) - (?P<numslow>\d+) operations were slow in the last (?P<timeslow>\d+) msecs:')
    slow_match = re.compile(r'(?P<query>.*), was slow (?P<count>\d+) times: avg/min/max (?P<avg>\d+)/(?P<min>\d+)/(?P<max>\d+) msec - slow timeout (?P<threshold>\d+) msec(?P<cross>/cross-node)?')
    slow_match_single = re.compile(r'(?P<query>.*), time (?P<time>\d+) msec - slow timeout (?P<threshold>\d+) msec(?P<cross>/cross-node)?')
    fail_match = re.compile(r'(?P<query>.*), timed out (?P<count>\d+) times: avg/min/max (?P<avg>\d+)/(?P<min>\d+)/(?P<max>\d+) msec -timeout (?P<threshold>\d+) msec(?P<cross>/cross-node)?')
    fail_match_single = re.compile(r'(?P<query>.*), total time (?P<time>\d+) msec - timeout (?P<threshold>\d+) msec(?P<cross>/cross-node)?')

    def __init__(self):
        self.state = None

    def parse(self, logfile):
        """ parses a debug log for slow queries """
        ret = {}
        for line in logfile:
            if self.state is None:
                m = self.begin_match.match(line)
                if m:
                    self.state = self.BEGIN
                    ret['numslow'] = int(m.group('numslow'))
                    ret['timeslow'] = int(m.group('timeslow'))
                    ret['date'] = date('%Y-%m-%d %H:%M:%S,%f')(m.group('date'))
                continue
            if self.state == self.BEGIN:
                for match in [self.slow_match, self.fail_match, self.slow_match_single, self.fail_match_single]:
                    m = match.match(line)
                    if m:
                        ret.update(m.groupdict())
                        if match in [self.fail_match, self.fail_match_single]:
                            ret['type'] = 'fail'
                        else:
                            ret['type'] = 'slow'
                        self.state = None
                        yield ret
                        break

class SlowQueryAnalyzer:
    """ analyzes results from parsing slow queries """

    def __init__(self, diag_dir, files=None, start=None, end=None):
        self.diag_dir = diag_dir
        self.files = files
        self.parser = SlowQueryParser()
        self.querytimes = defaultdict(list)
        self.queries = []
        self.analyzed = False
        self.start = None
        self.end = None
        self.cross = 0
        self.start_time = None
        self.end_time = None
        if start:
            self.start_time = date_parse(start)
        if end:
            self.end_time = date_parse(end)

    def analyze(self):
        """ analyze slow queries """
        parser = SlowQueryParser()
        target = find_logs(self.diag_dir, 'debug.log')
        if self.files:
            target = self.files
        for file in target:
            log = open(file, 'r')
            for query in parser.parse(log):
                if self.start_time and query['date'] < self.start_time:
                    continue
                if self.end_time and query['date'] > self.end_time:
                    continue
                if not self.start:
                    self.start = query['date']
                    self.end = query['date']
                if query['date'] > self.end:
                    self.end = query['date']
                if query['date'] < self.start:
                    self.start = query['date']
                if 'numslow' in query:
                    # pylint: disable=unused-variable
                    for x in range(query['numslow']):
                        self.querytimes[query['date']].append(query['timeslow'])
                else:
                    self.querytimes[query['date']].append(query['timeslow'])
                self.queries.append((query['query'], int(query['timeslow'])))
                if query['cross'] is not None:
                    self.cross += 1
        self.analyzed = True

    def print_report(self, command_name, interval=3600, top=3):
        """ print the report """
        if not self.analyzed:
            self.analyze()
        print("%s version %s" % (command_name, VERSION))
        print('')
        if not self.queries:
            if self.files:
                print("no queries found the files provided")
                for file_name in self.files:
                    print("- %s" % file_name)
            else:
                print("no queries found in diag tarball '%s'" % self.diag_dir)
            return
        self.__print_query_times(sorted(bucketize(self.querytimes, start=self.start, end=self.end,
                                                  seconds=interval).items(),
                                        key=lambda t: t[0]))
        print(len(self.queries), "slow queries, %s cross-node" % self.cross)
        print()
        print("Top %s slow queries:" % top)
        print('-'*30)
        for query, time in sorted(self.queries, key=lambda t: t[1], reverse=True)[0:top]:
            print("%sms: %s" % (time, query))
            print('')

    def __print_query_times(self, data):
        """ print data to the user, expecting datetime keys and list(int) values """
        timings = np.array([q[1] for q in self.queries])
        window = np.percentile(timings, 25) - 1
        window2 = np.percentile(timings, 50) - 1
        window3 = np.percentile(timings, 75) - 1
        window4 = np.percentile(timings, 99) - 1
        print(". <%sms + >%sms ! >%sms X >%sms" % (window, window2, window3, window4))
        print('-'*30)
        worst = None
        for time, qtimes in data:
            total = sum(qtimes)
            if not worst:
                worst = (time, total)
            elif total > worst[1]:
                worst = (time, total)
            print(time, ' ', end='')
            for qtime in qtimes:
                c = '.'
                if qtime > window2:
                    c = '+'
                if qtime > window3:
                    c = '!'
                if qtime > window4:
                    c = 'X'
                print(c, end='')
            print('')
        print('')
        print('worst period: %s (%sms)' % worst)
        print('')
