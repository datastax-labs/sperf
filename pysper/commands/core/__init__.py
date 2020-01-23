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
