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

"""feltercache command wiring"""
from pysper import VERSION
from pysper.commands import flags
from pysper.search import filtercache

def add_flags(subparsers, run_func, is_deprecated=False):
    """add_flags is so we can share logic between deprecated and new commands"""
    help_text = 'Generates a report of filter cache evictions. DSE Search 5.0.5+,5.1-6.7.'
    if is_deprecated:
        help_text = help_text + " DEPRECATED for 'sperf search filtercache'"
    filtercache_parser = subparsers.add_parser('filtercache',
                                               help=help_text,
                                               formatter_class=flags.LineWrapRawTextHelpFormatter)
    flags.files_and_diag(filtercache_parser)
    filtercache_parser.add_argument('-s', '--system_log_prefix',
                                    default='system.log',
                                    help='if system.log in the diag tarball has a different, ' + \
                                            'name, sperf can still look based on this prefix ' + \
                                         '(default "system.log")')
    filtercache_parser.add_argument('-a', '--after',
                                    default='0001-01-01 00:00:00,000000',
                                    help='optional filter for log times to only look at ' + \
                                            'logs after this time')
    filtercache_parser.add_argument('-b', '--before',
                                    default='9999-12-31 23:59:59,999999',
                                    help='optional filter for log times to only look at ' + \
                                            'logs before this time')
    filtercache_parser.set_defaults(func=run_func)

def build(subparsers):
    """adds the flags for filtercache cmd"""
    add_flags(subparsers, run)

def run(args):
    """entrypoint for filtercache command"""
    print("sperf filtercache: %s\n" % VERSION)
    parsed = filtercache.parse(args)
    print(filtercache.generate_report(parsed))
