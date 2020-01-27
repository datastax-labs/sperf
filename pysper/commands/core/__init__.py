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

"""core subcommands package. Includes also the parent core command which provides an entry point to the
cassandra/DSE core specific subcommands
"""
from pysper.commands.core import bgrep, diag, gc, jarcheck, schema, slowquery, statuslogger
from pysper import env

def build(subparsers):
    """build up subcommands"""
    help_text = 'Cassandra and DSE Core specific sub-commands'
    cass_parser = subparsers.add_parser('core', help=help_text)
    def run(args):
        if env.DEBUG:
            print(args)
        cass_parser.print_help()
    cass_parser.set_defaults(func=run)
    cass_sub = cass_parser.add_subparsers(title='DSE Core/Cassandra Commands')
    bgrep.build(cass_sub)
    diag.build(cass_sub)
    gc.build(cass_sub)
    jarcheck.build(cass_sub)
    schema.build(cass_sub)
    slowquery.build(cass_sub)
    statuslogger.build(cass_sub)
