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

"""cassread command wiring"""
from pysper.commands import flags
from pysper import VERSION
from pysper.core.diag import parse_diag, generate_report

def add_args(diag_parser):
    "add arguments that are shared between several commands"""
    flags.add_diagdir(diag_parser)
    diag_parser.add_argument('-s', '--system_log_prefix',
                             default='system.log',
                             help='if system.log in the diag tarball has an oddball name, ' + \
                                         'can still look based on this prefix ' + \
                                         '(default "system.log")')
    diag_parser.add_argument('-l', '--debug_log_prefix',
                             default='debug.log',
                             help='if debug.log in the diag tarball has an oddball name, ' + \
                                         'can still look based on this prefix ' + \
                                         '(default "debug.log")')
    diag_parser.add_argument('-o', '--output_log_prefix',
                             default='output.log',
                             help='if output.log in the diag tarball has an oddball name, ' + \
                                         'can still look based on this prefix ' + \
                                         '(default "output.log")')
    diag_parser.add_argument('-n', '--node_info_prefix',
                             default='node_info.json',
                             help='if node_info.json in the diag tarball has an oddball ' + \
                                 'name, can still look based on this prefix ' + \
                                         '(default "node_info.json")')
    diag_parser.add_argument('-c', '--cfstats_prefix',
                             default='cfstats',
                             help='if cfstats in the diag tarball has an oddball name, ' + \
                                         'can still look based on this prefix ' + \
                                         '(default "cfstats")')
    diag_parser.add_argument('-b', '--block_dev_prefix',
                             default='blockdev_report',
                             help='if blockdev_report in the diag tarball has an oddball name, ' + \
                                         'can still look based on this prefix ' + \
                                         '(default "blockdev_report")')


def add_flags(subparsers, name, run_func, is_deprecated=False):
    """so we can share the parser with the legacy sperf cassread command"""
    help_text = 'Generates a diagtarball report. DSE 5.0-6.7'
    if is_deprecated:
        help_text = help_text + ". DEPRECATED: use 'sperf core diag' instead"
    diag_parser = subparsers.add_parser(name,
                                        help=help_text,
                                        formatter_class=flags.LineWrapRawTextHelpFormatter)
    add_args(diag_parser)
    diag_parser.set_defaults(func=run_func)

def build(subparsers):
    """builds the cassread command up, assumes argparser api"""
    add_flags(subparsers, "diag", run)

def run(args):
    """launches 'sperf core diag'"""
    print("sperf core diag: %s\n" % VERSION)
    parsed = parse_diag(args)
    print(generate_report(parsed))
