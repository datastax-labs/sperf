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
