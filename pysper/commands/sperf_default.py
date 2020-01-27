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

"""sperf bare command that is aimed at new users and provides a general summary
"""
from pysper import sperf_default
from pysper.commands.core.diag import add_args
#from pysper import VERSION

def build(diag_parser):
    """build uses the args from the new command"""
#    help_text = 'Simple diag tarball report. Supports Cassandra 2.1-4.0, DSE 5.0-6.7'
#    diag_parser = subparsers.add_parser(name,
#                                        help=help_text,
#                                        formatter_class=flags.LineWrapRawTextHelpFormatter)
    add_args(diag_parser)
    #diag_parser.set_defaults(func=run)

def run(args):
    """launches 'sperf default command'"""
    sperf_default.run(args)
