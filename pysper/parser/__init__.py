""" pysper parser top level. """
from pysper.parser import systemlog, outputlog, block_dev
from pysper import env

def read_system_log(lines, **extras):
    """read the system log, yields an iterable set of events of parsed logs"""
    return read_log(lines, systemlog.capture_line, **extras)

def read_output_log(lines, **extras):
    """read the output log, yields an iterable set of events of parsed logs"""
    return read_log(lines, outputlog.capture_line, **extras)

def read_block_dev(lines, **extras):
    """consumes a block dev report, yields an iterable set of events of parsed logs"""
    return read_log(lines, block_dev.capture_line, **extras)

def _default_capture(line):
    """does nothing interesting but will print out lines if debug is on"""
    if env.DEBUG:
        print(line)

def read_log(lines, capture_line_func=_default_capture, **extras):
    """ parses an iterable set of lines yielding events """
    fields = None
    for line in lines:
        next_fields = capture_line_func(line)
        if next_fields is not None:
            if fields is not None:
                fields.update(extras)
                yield fields
            fields = next_fields
    #need to do this one last time to clear out the last update to next_fields
    if fields is not None:
        yield fields
