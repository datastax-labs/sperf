""" parser for systemlog returning gc messages only """
from pysper.parser.rules import switch, update_message, mkcapture
from pysper.parser.captures import system_capture_rule
from pysper.parser.cases import gc_rules

capture_message = switch((gc_rules()))
capture_line = mkcapture(system_capture_rule, update_message(capture_message))
