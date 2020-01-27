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

"Parses and reports on iostat output"
from datetime import datetime
from collections import defaultdict
from pysper import VERSION, env, humanize
from pysper.util import get_percentiles, get_percentile_headers

class IOStatParser:
    "Parses iostat"
    # states
    CPU = 'cpu'
    DATE = 'date'
    DEVICE = 'device'

    #us, eu date formats, and one seen in sper66
    datefmts = ['%m/%d/%Y %I:%M:%S %p', '%d/%m/%y %H:%M:%S', '%m/%d/%y %H:%M:%S']

    def __init__(self):
        self.state = None
        self.__mkiostat()

    def __mkiostat(self):
        self.iostat = {
            'cpu': {'cols': [], 'stat': []},
            'device': {'cols': [], 'stat': {}},
            'date': None
            }

    def _parse(self, line):
        if line == '\n': # empty lines are the reset switch
            if self.state == self.DEVICE:
                yield self.iostat
                self.__mkiostat()
            self.state = None
            return

        line = line.strip()

        if self.state == self.CPU:
            self._parse_cpu(line)
        elif self.state == self.DEVICE:
            self._parse_device(line)
        elif line[0].isdigit():
            self._parse_date(line)
        else:
            if line.startswith('avg-cpu'):
                self.state = self.CPU
                self.iostat['cpu']['cols'] = self._parse_columns(line)
            elif line.startswith('Device'):
                self.state = self.DEVICE
                self.iostat['device']['cols'] = self._parse_columns(line)

    def _parse_columns(self, line):
        return line.split()[1:]

    def _parse_cpu(self, line):
        self.iostat['cpu']['stat'] = [float(i.replace(',', '.')) for i in line.split()]

    def _parse_device(self, line):
        parts = line.split()
        self.iostat['device']['stat'][parts[0]] = [float(i.replace(',', '.')) for i in parts[1:]]

    def _parse_date(self, line):
        date = None
        for datefmt in self.datefmts:
            try:
                date = datetime.strptime(line, datefmt)
            except ValueError as e:
                if env.DEBUG:
                    print(e)
        if not date:
            raise ValueError("tried parsing in the following formats " + \
                    "'%s' but %s does not match" % (self.datefmts, line))
        self.iostat['date'] = date

    def parse(self, infile):
        "parse an iostat file"
        with open(infile, 'r') as f:
            for line in f:
                for stat in self._parse(line):
                    yield stat

class SysbottleReport:
    "Produces a report from iostat output"
    def __init__(self, infile, conf=None):
        self.infile = infile
        self.parser = IOStatParser()

        self.count = 0
        self.cpu_exceeded = 0
        self.iowait_exceeded = 0
        self.devices = defaultdict(lambda: defaultdict(list))
        self.cpu_stats = defaultdict(list)
        self.queuedepth = defaultdict(int)
        self.start = None
        self.end = None

        self.device_index = {}
        self.cpu_index = {}
        self.conf = conf or self.__mk_conf()
        self.recs = set()
        self.analyzed = False

    def __mk_conf(self):
        conf = {}
        conf['iowait_threshold'] = 5
        conf['cpu_threshold'] = 50
        conf['disks'] = []
        conf['queue_threshold'] = 1
        conf['busy_threshold'] = 5
        return conf

    def analyze(self):
        "analyzes the file this class was initialized with"
        for io in self.parser.parse(self.infile):
            self.count += 1
            if not self.device_index:
                self.__mk_col_idx(io)
            self.__analyze_disk(io)
            self.__analyze_cpu(io)
            if not self.start:
                self.start = io['date']
            if not self.end or io['date'] > self.end:
                self.end = io['date']
        self.analyzed = True

    def __mk_col_idx(self, stat):
        for i, col in enumerate(stat['device']['cols']):
            self.device_index[col] = i
        for i, col in enumerate(stat['cpu']['cols']):
            self.cpu_index[col] = i

    def __want_disk(self, name):
        if not self.conf['disks']:
            return True
        return name in self.conf['disks']

    def __analyze_disk(self, stat):
        for disk, values in stat['device']['stat'].items():
            if self.__want_disk(disk):
                for col in self.device_index:
                    val = values[self.device_index[col]]
                    self.devices[disk][col].append(val)
                    if 'qu' in col and val >= self.conf['queue_threshold']:
                        self.queuedepth[disk] += 1
                        self.recs.add("* decrease activity on %s" % disk)

    def __analyze_cpu(self, stat):
        total = 0
        for cpu in ['system', 'user', 'nice', 'steal']:
            total += stat['cpu']['stat'][self.cpu_index['%' + cpu]]
        self.cpu_stats['total'].append(total)
        if total > self.conf['cpu_threshold']:
            self.cpu_exceeded += 1
            self.recs.add("* tune for less CPU usage")
        for col in self.cpu_index:
            val = stat['cpu']['stat'][self.cpu_index[col]]
            self.cpu_stats[col].append(val)
        if stat['cpu']['stat'][self.cpu_index['%iowait']] > self.conf['iowait_threshold']:
            self.iowait_exceeded += 1
            self.recs.add("* tune for less IO")

    def print_report(self):
        "prints a report for the file this class was initialized with, analyzing if necessary"
        if not self.analyzed:
            self.analyze()
        print("sysbottle version %s" % VERSION)
        print()
        print()
        print("* total records: %s" % self.count)
        if self.count:
            report_percentage = lambda a: (float(a)/float(self.count)) * 100.0
            print("* total bottleneck time: %.2f%% (cpu bound, io bound, or both)" % \
                report_percentage(self.iowait_exceeded+self.cpu_exceeded))
            print("* cpu+system+nice+steal time > %.2f%%: %.2f%%" % \
                (self.conf['cpu_threshold'], report_percentage(self.cpu_exceeded)))
            print("* iowait time > %.2f%%: %.2f%%" % \
                (self.conf['iowait_threshold'], report_percentage(self.iowait_exceeded)))
            print("* start %s" % self.start)
            print("* end %s" % self.end)
            log_time_seconds = (self.end - self.start).total_seconds() + 1
            print("* log time: %ss" % log_time_seconds)
            print("* interval: %ss" % report_percentage(log_time_seconds))
            for device in self.devices.keys():
                print("* %s time at queue depth >= %.2f: %.2f%%" % \
                    (device, self.conf['queue_threshold'], report_percentage(self.queuedepth[device])))
            print()
            lines = []
            lines.append(get_percentile_headers())
            lines.append(['', "---", "---", "---", "---", "---", "---"])
            lines.append(get_percentiles('cpu', self.cpu_stats['total']))
            lines.append(get_percentiles('iowait', self.cpu_stats['%iowait']))
            lines.append([])
            lines.append(get_percentile_headers())
            lines.append(['', "---", "---", "---", "---", "---", "---"])
            for device in self.devices:
                lines.append([device, "", "", "", "", "", ""])
                for iotype in self.devices[device].keys():
                    if 'qu' in iotype or 'wait' in iotype:
                        lines.append(get_percentiles('- ' + iotype + ':', self.devices[device][iotype]))
            lines.append([])
            humanize.pad_table(lines, 8, 2)
            for line in lines:
                print("".join(line))
            self.print_recommendations()

    def print_recommendations(self):
        """print recommendations"""
        if not self.recs:
            return
        print('recommendations')
        print('-'*15)
        for rec in self.recs:
            print(rec)

if __name__ == '__main__':
    import os

    iostat = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'iostat')

    report = SysbottleReport(iostat)
    report.print_report()
