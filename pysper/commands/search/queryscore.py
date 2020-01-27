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

"""solr query agg command wiring"""
from pysper.commands import flags
from pysper import VERSION
from pysper.search import queryscore as qs

def add_flags(subparsers, name, run_default_func, is_deprecated=False):
    """adds the flags so legacy commands can share code"""
    help_text = 'Tries to summarize queries in the debug ' + \
            'log based on score that attempts to ' + \
            'estimate the relative potential cost ' + \
            'of queries. DSE Search 5.0-6.7'
    if is_deprecated:
        help_text = help_text + ". DEPRECATED use 'sperf search queryscore' instead"
    queryscore_parser = subparsers.add_parser(name,
                                              help=help_text,
                                              formatter_class=flags.LineWrapRawTextHelpFormatter)

    queryscore_parser.add_argument('-s', '--scorethreshold', type=int, default=1, \
                help="The score threshold to list a 'bad query'")
    queryscore_parser.add_argument('-t', '--top', type=int, default=5, \
                help="show the top N worst queries by score.")
    queryscore_parser.add_argument('-u', '--uniquereasons', action='store_true', \
                help="show only queries with a unique score and combination of reasons.")
    queryscore_parser.add_argument('-l', '--log_prefix',
                                   default='debug.log',
                                   help='if debug.log in the diag tarball has a different, ' + \
                                            'name, sperf can still look based on this prefix ' + \
                                         '(default "debug.log")')
    flags.files_and_diag(queryscore_parser)
    queryscore_parser.set_defaults(func=run_default_func)

def build(subparsers):
    """adds the flags to queryscore"""
    add_flags(subparsers, 'queryscore', run)

def run(args):
    """launches 'sperf search queryscore'"""
    run_func(args, 'sperf search queryscore')

def run_func(args, command_name):
    """for function sharing between deprecated and supported"""
    print("%s: %s\n" % (command_name, VERSION))
    parsed = qs.parse(args)
    print(qs.generate_report(parsed))
