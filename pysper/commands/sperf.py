"""main sperf parent command"""
import argparse
from pysper import env, VERSION
from pysper.commands import core, search, sysbottle, flags, ttop, sperf_default

def _build_sperf_cmd():
    """main entry point command, returns subparsers to add more commands too"""
    parser = argparse.ArgumentParser(description='Sperf provides a number of useful ' + \
            'reports from the diagtarball, iostat and the nodes themselves.',
                                     formatter_class=flags.LineWrapRawTextHelpFormatter)
    parser.add_argument('-p', '--progress', dest="progress", action='store_true',
                        help='shows file progress to show how long it takes to process each file')
    parser.add_argument('-v', '--debug', dest="debug", action='store_true',
                        help='shows debug output. ' + \
                                'Useful for bug reports and diagnosing issues with sperf')
    sperf_default.build(parser)
    return parser, parser.add_subparsers(title='Commands')

def build_parser():
    """build the parser that wires up the subcommands and their flags"""
    parser, subparsers = _build_sperf_cmd()
    core.build(subparsers)
    search.build(subparsers)
    sysbottle.build(subparsers)
    ttop.build(subparsers)
    return parser

def run():
    """run is the entry point that selects the subcommand to run"""
    parser = build_parser()
    args = parser.parse_args()
    if args.progress:
        env.PROGRESS = args.progress
    if args.debug:
        env.DEBUG = args.debug
    if hasattr(args, 'func'):
        try:
            args.func(args)
        except Exception as ex:  # pylint: disable=broad-except
            if env.DEBUG:
                raise ex
            print(str(ex))
            print("")
            print("To show strack trace use the -v flag. For example: 'sperf -v cassread'")
    else:
        print("sperf version %s" % VERSION)
        print()
        sperf_default.run(args)
    #for formatting
    print("\n")
