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

"""the search subcommand package. It also includes a search parent command,
which provides an entry point to the solr specific subcommands.
"""
from pysper.commands.search import filtercache, queryscore
from pysper import env

def build(subparsers):
    """builds the subcommands for the search parent command"""
    help_text = 'Search specific sub-commands'
    solr_parser = subparsers.add_parser('search', help=help_text)
    def run(args):
        if env.DEBUG:
            print(args)
        solr_parser.print_help()
    solr_parser.set_defaults(func=run)
    solr_sub = solr_parser.add_subparsers(title='Search Commands')
    filtercache.build(solr_sub)
    queryscore.build(solr_sub)
