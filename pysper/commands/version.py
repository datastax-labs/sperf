"""simple version output"""
import sys
from pysper import VERSION
from pysper.commands import flags

def build(subparsers):
    """setups the version command"""
    version_parser = subparsers.add_parser('version', help='list the version of sperf',
                                           formatter_class=flags.LineWrapRawTextHelpFormatter)
    version_parser.set_defaults(func=lambda _: print("sperf %s-%s", VERSION, sys.version))
