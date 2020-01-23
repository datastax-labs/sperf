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
