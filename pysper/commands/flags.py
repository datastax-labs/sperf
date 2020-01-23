"""flags provides flag helpers for argparse"""
import argparse
import textwrap as _textwrap

def add_diagdir(parser):
    """since it's so common to have a diagdir flag for the tooling
    we've added it here to make it simpler to add"""
    parser.add_argument('-d', '--diagdir', dest="diag_dir", default='.',
                        help=' where the diag tarball directory is exported, '+ \
            'should be where the nodes folder is located (default ".")')

def add_files(parser):
    """since it's so common to have a files flag for the tooling
    we've added it here to make it simpler to add"""
    parser.add_argument('-f', '--files', dest="files",
                        help='comma separated file list to compare. Alternative to --diagdir')

def files_and_diag(parser):
    """addes --diag_dir and --files flags to a given parser"""
    add_files(parser)
    add_diagdir(parser)

class LineWrapRawTextHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """hard codes a 120 wide character word wrap"""
    def _split_lines(self, text, width):
        text = self._whitespace_matcher.sub(' ', text).strip()
        #ignore width parameter passed above and use our own
        wrap_width = 120
        return _textwrap.wrap(text, wrap_width)
