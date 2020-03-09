# Copyright 2020 DataStax, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""formats the output of the cassread parsed data"""
from pysper import humanize, env

#used for report formatting
NA = "N/A"

def simple_format(val):
    """formats the value as a string, it not present it will return N/A"""
    if not val:
        return NA
    return str(val)

def simple_format_float(val):
    """formats the float with 2 decimals, it not present it will return N/A"""
    if not val:
        return NA
    return "%.2f" % val

def append(report, key, value):
    """pads the key 29 spaces"""
    key_formatted = '{:<29}'.format(key)
    report.append("%s %s" % (key_formatted, value))

def write_config(report, config): #pylint: disable=too-many-statements
    """generates the configuration text"""
    append(report, "nodes count", simple_format(config.get("nodes")))
    append(report, "cass drive(s) read ahead", _format_read_ahead(config.get("cass_ra")))
    append(report, "dse version", simple_format(config.get("version")))
    append(report, "cassandra version", simple_format(config.get("cassandra_version")))
    append(report, "solr version", simple_format(config.get("solr_version")))
    append(report, "spark version", simple_format(config.get("spark_version")))
    append(report, "spark connector version", _format_spark_connector(config))
    append(report, "disk access mode", format_disk_access_mode(config))
    append(report, 'disk optimization', simple_format(config.get('disk_optimization_strategy')))
    append(report, "memtable cleanup threshold", \
            simple_format(config.get("memtable_cleanup_threshold")))
    append(report, "flush writers", _format_flush_writers(config.get("memtable_flush_writers")))
    append(report, "compaction throughput", \
        _format_compaction_throughput(config.get("compaction_throughput_mb_per_sec")))
    append(report, "concurrent compactors", simple_format(config.get("concurrent_compactors")))
    memtable_heap_size = config.get("memtable_heap_space_in_mb", config.get("memtable_space_in_mb"))
    append(report, "memtable size (heap)", simple_format(memtable_heap_size))
    append(report, "memtable size (offheap)", \
            simple_format(config.get("memtable_offheap_space_in_mb")))
    append(report, "memtable allocation type", \
            simple_format(config.get("memtable_allocation_type")))
    append(report, "file cache size", \
            simple_format(config.get("file_cache_size_in_mb")))
    append(report, "heap size", \
            simple_format(config.get("heap_size")))
    append(report, "gc", simple_format(config.get("gc")))
    append(report, "total ram", simple_format(config.get("ram_in_mb")))
    append(report, "total cpu cores (real)", _format_cores(config))
    append(report, "threads per core", \
            simple_format(config.get("threads_per_core")))
    append(report, "worst gc pause", format_gc(config))
    append(report, "worst write latency (all)", \
            format_table_stat_float(config.get("worst_write_latency"), val_suffix="ms"))
    append(report, "worst read latency (all)", \
            format_table_stat_float(config.get("worst_read_latency"), val_suffix="ms"))
    append(report, "worst tombstones query (all)", \
            format_table_stat(config.get("worst_tombstone")))
    append(report, "worst live cells query (all)", \
            format_table_stat(config.get("worst_live_cells")))
    append(report, "largest table", format_largest_table(config))
    append(report, "busiest table reads", format_busiest_table(config.get("busiest_table_reads"), "reads"))
    append(report, "busiest table writes", format_busiest_table(config.get("busiest_table_writes"), "writes"))
    append(report, "worst partition in", format_table_loc(config.get('worst_part_size')))
    append(report, "* max partition size", \
            format_partition_bytes(config.get('worst_part_size'), 2))
    append(report, "* mean partition size", \
            format_partition_bytes(config.get('worst_part_size'), 3))
    append(report, "* min partition size", \
            format_partition_bytes(config.get('worst_part_size'), 4))
    report.append("")
    report.append("nodes")
    report.append("-----")
    report.append(humanize.format_list(config.get("nodes_list"), wrap_every=5))
    report.append("")
    if config.get("diff"):
        conversions = {
            "ram_in_mb": "ram in mb",
            "cpu_cores": "cpu",
            "threads_per_core": "cpu threads",
            "cass_ra": "read ahead",
        }
        report.append("")
        report.append("config diff from common:")
        for diff in config.get("diff"):
            tokens = diff.split(":")
            if len(tokens) > 1:
                key = conversions.get(tokens[0], tokens[0])
                if key.startswith("-Xms"): # duplicates heap size
                    continue
                if key.startswith("-Xmx"): # duplicates heap size
                    continue
                if key == "read ahead":
                    value = _format_read_ahead(config.get("cass_ra"))
                else:
                    value = tokens[1]
                report.append("* %s: %s" % (key, value))

#Format helpers
def format_partition_bytes(stat, index):
    """writes out the bytes of the stat at index specified will return null if not present"""
    if not stat or not index or len(stat) < index+1:
        return NA
    val = stat[index]
    if not val:
        return NA
    return humanize.format_bytes(val)

def format_table_loc(info):
    """writes out the table and node it's on"""
    if not info or len(info) < 2:
        return NA
    table = info[0]
    node = info[1]
    if table and node:
        return "%s (%s)" % (table, node)
    return NA

def format_table_stat(stat, val_suffix=""):
    """display most value read in a human friendly
    format with the responsible table and node"""
    if not stat or len(stat) < 3:
        return NA
    val_suffix_str = ""
    if val_suffix:
        val_suffix_str = "%s " % val_suffix
    node = stat[0]
    table = stat[1]
    val = stat[2]
    if node and table and val:
        return "%s %s(%s %s)" % (humanize.format_num(val), val_suffix_str, table, node)
    return NA

def format_table_stat_float(stat, val_suffix=""):
    """display most value read in a human friendly
    format with the responsible table and node"""
    if not stat or len(stat) < 3:
        return NA
    val_suffix_str = ""
    if val_suffix:
        val_suffix_str = "%s " % val_suffix
    node = stat[0]
    table = stat[1]
    val = stat[2]
    if node and table and val:
        return "%s %s(%s %s)" % (humanize.format_num_float(val), val_suffix_str, table, node)
    return NA

def _format_spark_connector(config):
    scc = config.get("spark_connector_version")
    dse_scc = config.get("dse_spark_connector_version")
    if scc and not dse_scc:
        return "%s (OSS)" % scc
    if dse_scc and not scc:
        return "%s (DSE)" % dse_scc
    if scc and dse_scc:
        return "%s (OSS), %s (DSE)" % (scc, dse_scc)
    return NA

def _format_compaction_throughput(throughput):
    if not throughput:
        return NA
    return "%s mb" % throughput

def format_disk_access_mode(config):
    """provides disk access mode translation"""
    disk_access_mode = NA
    #we are ignoring commit_log_access_mode until we resolve sper38
    disk_mode = config.get("logged_disk_access_mode")
    index_mode = config.get("logged_index_access_mode")
    if env.DEBUG:
        print("DEBUG: raw disk access mode %s" % disk_mode)
        print("DEBUG: raw index access mode %s" % index_mode)
    if disk_mode == "mmap" and index_mode == "mmap":
        disk_access_mode = "mmap"
    elif disk_mode == "standard" and index_mode == "mmap":
        disk_access_mode = "mmap_index_only"
    elif disk_mode == "standard" and index_mode == "standard":
        disk_access_mode = "standard"
    return disk_access_mode

def _format_flush_writers(memtable_flush_writers):
    if str(memtable_flush_writers) == "0":
        return "default"
    return memtable_flush_writers

def format_busiest_table(busiest_table, mode):
    """outputs the busiest table in a pleasing format"""
    if not busiest_table or len(busiest_table) < 2:
        return NA
    table = busiest_table[0]
    busy_per = busiest_table[1]
    if table and busy_per:
        return "%s (%.2f%% of %s)" % (table, busy_per, mode)
    return NA

def format_largest_table(config):
    """outputs the biggest table in a pleasing format"""
    largest_table = config.get("largest_table")
    if not largest_table or len(largest_table) < 3:
        return NA
    node = largest_table[0]
    table = largest_table[1]
    max_table = largest_table[2]
    if table and max_table:
        max_table_fmt = humanize.format_bytes(max_table)
        return "%s (%s %s)" % (table, max_table_fmt, node)
    return NA

def format_gc(config):
    """outputs the gc in a pleasing format"""
    worst_gc = config.get("worst_gc")
    if not worst_gc or len(worst_gc) < 2:
        return NA
    node = worst_gc[1]
    if not node:
        return NA
    gc_in_ms = worst_gc[0]
    if not gc_in_ms:
        return NA
    return "%s (%s)" % (humanize.format_millis(gc_in_ms), node)

def _format_cores(config):
    cores = config.get("cpu_cores")
    threads = config.get("threads_per_core")
    if not cores or not threads:
        return NA
    return int(int(cores)/int(threads))

def _format_read_ahead(drive_map):
    if not drive_map:
        return NA
    result = []
    for ra_bytes in drive_map:
        result.append(humanize.format_bytes(ra_bytes))
    return ", ".join(result)
