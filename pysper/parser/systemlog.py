""" parser for dse system.log """
from pysper.parser.rules import switch, mkcapture, update_message
from pysper.parser.cases import gc_rules, memtable_rules, solr_rules, cfs_rules, daemon_rules, status_rules
from pysper.parser.captures import system_capture_rule

# pylint: disable=too-many-function-args
capture_message = switch((
    *daemon_rules(),
    *status_rules(),
    *gc_rules(),
    *memtable_rules(),
    *cfs_rules(),
    *solr_rules(),
))

capture_line = mkcapture(system_capture_rule, update_message(capture_message))
