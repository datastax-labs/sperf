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

"""jarcheck wiring"""
from pysper import jarcheck, VERSION
from pysper.commands import flags

def build(subparsers):
    """add jarcheck flags"""
    jarcheck_parser = subparsers.add_parser('jarcheck',
                                            help='Checks jar versions in output.logs. ' + \
                                            'Supports tarballs and files. DSE 5.0-6.7',
                                            formatter_class=flags.LineWrapRawTextHelpFormatter)
    jarcheck_parser.set_defaults(func=run)
    flags.files_and_diag(jarcheck_parser)
    jarcheck_parser.add_argument('-o', '--diffonly', dest="diff_only", action='store_true',
                                 help='only report on the jars that are different')

def run(args):
    """subcommand that is launched when 'sperf jarcheck' is called"""
    print("sperf jarcheck: %s\n" % VERSION)
    files = None
    if args.files:
        files = args.files.split(',')
    parser = jarcheck.JarCheckParser(args.diag_dir, files)
    parser.analyze()
    parser.print_report(args.diff_only)
