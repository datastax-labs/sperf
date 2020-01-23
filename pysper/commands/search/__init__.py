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
