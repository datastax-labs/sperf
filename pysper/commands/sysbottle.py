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

"""sysbottle subcommand wiring"""
from pysper import sysbottle
from pysper.commands import flags

def build(subparsers):
    """builds the systbottle command up"""
    sbparser = subparsers.add_parser('sysbottle',
                                     help="""sysbottle provides analysis of an iostat file. Supports iostat
                                     files generated via `iostat -x -c -d -t`""",
                                     formatter_class=flags.LineWrapRawTextHelpFormatter)
    sbparser.add_argument("file", help="iostat file to generate report on")
    sbparser.add_argument('-c', '--cpu', type=float, const=50, default=50, nargs='?',
                          help="""percentage cpu usage minus iowait%% above this threshold is busy.
                          Assumes hyperthreading is enabled (default 50)""")
    sbparser.add_argument('-q', '--diskQ', type=float, nargs='?', const=1, default=1,
                          help="disk queue depth. above this threshold is considered busy. (default 1)")
    sbparser.add_argument('-d', '--disks', type=str, nargs='?',
                          help="""comma separated list of disks to include in report, if no disks
                           are provided then all found disks are included in report""")
    sbparser.add_argument('-i', '--iowait', type=float, const=5, default=5, nargs='?',
                          help="percentage iowait above this threshold is marked as a busy disk (default 5)")
    sbparser.add_argument('-t', '--throughput', type=float, const=5, default=5, nargs='?',
                          help="""percentage of total time where we consider a node 'busy' for bottleneck
                          summary. Example by default (5.0%%) if the CPU and Disk are busy 5.0%% of the total
                          time measured then it is considered busy. (default 5)""")
    sbparser.set_defaults(func=run)

def run(args):
    """"sysbottle subcommand"""
    conf = {}
    conf['iowait_threshold'] = args.iowait
    conf['cpu_threshold'] = args.cpu
    if args.disks:
        conf['disks'] = args.disks.split(',')
    else:
        conf['disks'] = []
    conf['queue_threshold'] = args.diskQ
    conf['busy_threshold'] = args.throughput
    reporter = sysbottle.SysbottleReport(args.file, conf)
    reporter.print_report()
