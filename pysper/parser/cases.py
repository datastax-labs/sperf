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

# pylint: disable=line-too-long
""" case rules for various messages """
from pysper.parser.rules import case, rule, capture, convert, update, percent, nodeconfig, jvm_args

def gc_rules():
    """ rules to capture gc """
    return (case('GCInspector'),

            rule(
                capture(r'Heap is (?P<percent_full>[0-9.]*) full.*'),
                convert(percent, 'percent_full'),
                update(event_product='cassandra', event_category='garbage_collection', event_type='heap_full')),

            rule(
                capture(r'GC for (?P<gc_type>[A-Za-z]*): (?P<duration>[0-9]*) ms for (?P<collections>[0-9]*) collections, (?P<used>[0-9]*) used; max is (?P<max>[0-9]*)'),
                convert(int, 'duration', 'collections', 'used', 'max'),
                update(event_product='cassandra', event_category='garbage_collection', event_type='pause')),

            rule(
                capture(r'(?P<gc_type>[A-Za-z]*) GC in (?P<duration>[0-9]*)ms. (( CMS)? Old Gen: (?P<oldgen_before>[0-9]*) -> (?P<oldgen_after>[0-9]*);)?( Code Cache: (?P<codecache_before>[0-9]*) -> (?P<codecache_after>[0-9]*);)?( Compressed Class Space: (?P<compressed_class_before>[0-9]*) -> (?P<compressed_class_after>[0-9]*);)?( CMS Perm Gen: (?P<permgen_before>[0-9]*) -> (?P<permgen_after>[0-9]*);)?( Metaspace: (?P<metaspace_before>[0-9]*) -> (?P<metaspace_after>[0-9]*);)?( Par Eden Space: (?P<eden_before>[0-9]*) -> (?P<eden_after>[0-9]*);)?( Par Survivor Space: (?P<survivor_before>[0-9]*) -> (?P<survivor_after>[0-9]*))?'),
                convert(int, 'duration', 'oldgen_before', 'oldgen_after', 'permgen_before', 'permgen_after', 'codecache_before', 'codecache_after', 'compressed_class_before', 'compressed_class_after', 'metaspace_before', 'metaspace_after', 'eden_before', 'eden_after', 'survivor_before', 'survivor_after'),
                update(event_product='cassandra', event_category='garbage_collection', event_type='pause')),

            rule(
                capture(r'(?P<gc_type>.+) Generation GC in (?P<duration>[0-9]+)ms.  (Compressed Class Space: (?P<compressed_class_before>[0-9]+) -> (?P<compressed_class_after>[0-9]+);)?.((.+) Eden Space: (?P<eden_before>[0-9]+) -> (?P<eden_after>[0-9]+);)?.((.+) Old Gen: (?P<oldgen_before>[0-9]+) -> (?P<oldgen_after>[0-9]+);)?.((.+) Survivor Space: (?P<survivor_before>[0-9]+) -> (?P<survivor_after>[0-9]+);)?.(Metaspace: (?P<metaspace_before>[0-9]+) -> (?P<metaspace_after>[0-9]+))?'),
                convert(int, 'duration', 'oldgen_before', 'oldgen_after', 'permgen_before', 'permgen_after', 'compressed_class_before', 'compressed_class_after', 'metaspace_before', 'metaspace_after', 'eden_before', 'eden_after', 'survivor_before', 'survivor_after'),
                update(event_product='cassandra', event_category='garbage_collection', event_type='pause')),
            )

def solr_rules():
    """ rules to capture solr """
    return (case('SolrFilterCache'),
            rule(
                capture(r'Filter cache org.apache.solr.search.SolrFilterCache\$(?P<id>\S+) has reached (?P<entries>[0-9]+) entries of a maximum of (?P<maximum>[0-9]+). Evicting oldest entries...'),
                convert(int, 'entries', 'maximum'),
                update(event_product='solr', event_category='filter_cache', event_type='eviction_items')),
            rule(
                capture(r"...eviction completed in (?P<duration>[0-9]+) milliseconds. Filter cache org.apache.solr.search.SolrFilterCache\$(?P<id>\S+) usage is now (?P<usage>[0-9]+) (?P<usage_unit>\w+) across (?P<entries>[0-9]+) entries."),
                convert(int, 'duration', 'entries', 'usage'),
                update(event_product='solr', event_category='filter_cache', event_type='eviction_items_duration')),

            rule(
                capture(r"Filter cache org.apache.solr.search.SolrFilterCache\$(?P<id>\S+) has reached (?P<usage>[0-9]+) (?P<usage_unit>\w+) bytes of off-heap memory usage, the maximum is (?P<maximum>[0-9]+) (?P<maximum_unit>\w+). Evicting oldest entries..."),
                convert(int, 'maximum', 'usage'),
                update(event_product='solr', event_category='filter_cache', event_type='eviction_bytes')),

            rule(
                capture(r"...eviction completed in (?P<duration>[0-9]+) milliseconds. Filter cache org.apache.solr.search.SolrFilterCache\$(?P<id>\S+) usage is now (?P<usage>[0-9]+) across (?P<entries>[0-9]+) entries."),
                convert(int, 'duration', 'entries', 'usage'),
                update(event_product='solr', event_category='filter_cache', event_type='eviction_bytes_duration')),
            case('QueryComponent'),
            rule(
                capture(r'process: (?P<query>.*$)'),
                update(event_product='solr', event_category='query_component', event_type='query_logs')),
            )
def daemon_rules():
    """ rules to capture from daemon """
    return (
        case('StorageService'),
        rule(
            #StorageService.java:607 - Cassandra version: 3.0.12.1656
            capture(r'Cassandra version: (?P<cassandra_version>.*)$'),
            update(event_product='cassandra', event_category='startup', event_type='server_version')),
        case('DseDaemon'),
        rule(
            capture(r'DSE version: (?P<version>.*)$'),
            update(event_product='dse', event_category='startup', event_type='server_version')),
        rule(
            #DseDaemon.java:463 - Solr version: 6.0.1.0.2224
            capture(r'Solr version: (?P<solr_version>.*)$'),
            update(event_product='dse', event_category='startup', event_type='server_version')),
        rule(
            #Spark version: 2.0.2.17
            capture(r'Spark version: (?P<spark_version>.*)$'),
            update(event_product='dse', event_category='startup', event_type='server_version')),
        rule(
            #Spark Cassandra Connector version: 2.0.7
            capture(r'Spark Cassandra Connector version: (?P<spark_connector_version>.*)$'),
            update(event_product='dse', event_category='startup', event_type='server_version')),
        rule(
            #DSE Spark Connector version: 6.0.6
            capture(r'DSE Spark Connector version: (?P<dse_spark_connector_version>.*)$'),
            update(event_product='dse', event_category='startup', event_type='server_version')),
        case('CassandraDaemon'),
        rule(
            capture(r'JVM Arguments: \[(?P<jvm_args>.*)\]'),
            convert(jvm_args, 'jvm_args'),
            update(event_product='cassandra', event_category='node_config', event_type='jvm_args')),
        rule(
            capture(r'Classpath: (?P<classpath>.*)'),
            update(event_product='cassandra', event_category='startup', event_type='classpath')),
        )

def cfs_rules():
    """ rules to capture from ColumnFamilyStore """
    return (case('ColumnFamilyStore'),

            rule(
                capture(
                    r'Enqueuing flush of Memtable-(?P<table>[^@]*)@(?P<hash_code>[0-9]*)\((?P<serialized_bytes>[0-9]*)/(?P<live_bytes>[0-9]*) serialized/live bytes, (?P<ops>[0-9]*) ops\)',
                    r'Enqueuing flush of (?P<table>[^:]*): (?P<on_heap_bytes>[0-9]*) \((?P<on_heap_limit>[0-9]*)%\) on-heap, (?P<off_heap_bytes>[0-9]*) \((?P<off_heap_limit>[0-9]*)%\) off-heap'),
                convert(int, 'hash_code', 'serialized_bytes', 'live_bytes', 'ops', 'on_heap_bytes', 'off_heap_bytes', 'on_heap_limit', 'off_heap_limit'),
                update(event_product='cassandra', event_category='memtable', event_type='enqueue_flush')),

            rule(
                capture(r"Flushing largest CFS\(Keyspace='(?P<keyspace>[^']*)', ColumnFamily='(?P<table>[^']*)'\) to free up room. Used total: (?P<used_on_heap>\d+\.\d+)/(?P<used_off_heap>\d+\.\d+), live: (?P<live_on_heap>\d+\.\d+)/(?P<live_off_heap>\d+\.\d+), flushing: (?P<flushing_on_heap>\d+\.\d+)/(?P<flushing_off_heap>\d+\.\d+), this: (?P<this_on_heap>\d+\.\d+)/(?P<this_off_heap>\d+\.\d+)"),
                convert(float, 'used_on_heap', 'used_off_heap', 'live_on_heap', 'live_off_heap', 'flushing_on_heap', 'flushing_off_heap', 'this_on_heap', 'this_off_heap'),
                update(event_product='cassandra', event_category='memtable', event_type='flush_largest')),

            rule(
                capture(
                    r"Flushing SecondaryIndex (?P<index_type>[^{]*)\{(?P<index_metadata>[^}]*)\}",
                    r"Flushing SecondaryIndex (?P<index_class>[^@]*)@(?P<index_hash>.*)"),
                update(event_product='cassandra', event_category='secondary_index', event_type='flush')),
            )

def memtable_rules():
    """ rules to capture from memtable/cfs """
    return (case('Memtable', 'ColumnFamilyStore'),

            rule(
                capture(
                    r'Writing Memtable-(?P<table>[^@]*)@(?P<hash_code>[0-9]*)\(((?P<serialized_bytes>[0-9]*)|(?P<serialized_kb>[0-9.]*)KiB|(?P<serialized_mb>[0-9.]*)MiB) serialized bytes, (?P<ops>[0-9]*) ops, (?P<on_heap_limit>[0-9]*)%/(?P<off_heap_limit>[0-9]*)% of on/off-heap limit\)',
                    r'Writing Memtable-(?P<table>[^@]*)@(?P<hash_code>[0-9]*)\((?P<serialized_bytes>[0-9]*)/(?P<live_bytes>[0-9]*) serialized/live bytes, (?P<ops>[0-9]*) ops\)'),
                convert(int, 'hash_code', 'serialized_bytes', 'live_bytes', 'ops', 'on_heap_limit', 'off_heap_limit'),
                convert(float, 'serialized_kb'),
                update(event_product='cassandra', event_category='memtable', event_type='begin_flush')),

            rule(
                capture(
                    r'Completed flushing (?P<filename>[^ ]*) \(((?P<file_size_mb>[0-9.]*)MiB|(?P<file_size_kb>[0-9.]*)KiB|(?P<file_size_bytes>[0-9]*) bytes)\) for commitlog position ReplayPosition\(segmentId=(?P<segment_id>[0-9]*), position=(?P<position>[0-9]*)\)',
                    r'Completed flushing; nothing needed to be retained.  Commitlog position was ReplayPosition\(segmentId=(?P<segment_id>[0-9]*), position=(?P<position>[0-9]*)\)'),
                convert(int, 'file_size_bytes', 'segment_id', 'position'),
                convert(float, 'file_size_kb'),
                update(event_product='cassandra', event_category='memtable', event_type='end_flush')),

            rule(
                capture(r"CFS\(Keyspace='(?P<keyspace>[^']*)', ColumnFamily='(?P<table>[^']*)'\) liveRatio is (?P<live_ratio>[0-9.]*) \(just-counted was (?P<just_counted>[0-9.]*)\).  calculation took (?P<duration>[0-9]*)ms for (?P<cells>[0-9]*) (columns|cells)"),
                convert(float, 'live_ratio', 'just_counted'),
                convert(int, 'duration', 'cells'),
                update(event_product='cassandra', event_category='memtable', event_type='live_ratio_estimate')),

            rule(
                capture('setting live ratio to maximum of (?P<max_sane_ratio>[0-9.]*) instead of (?P<live_ratio_estimate>[0-9.]*)'),
                convert(float, 'max_sane_ratio', 'estimated_ratio'),
                update(event_product='cassandra', event_category='memtable', event_type='live_ratio_max')),
            )

def status_rules():
    """ rules to capture from statuslogger """
    return (case('StatusLogger'),

            rule(
                capture(r'Pool Name +Active +Pending \(w/Backpressure\) +Delayed +Completed +Blocked +All Time Blocked$'),
                update(event_product='cassandra', event_category='status', event_type='threadpool_header', rule_type='new')),

            rule(
                capture(r'Pool Name +Active +Pending( +Completed)? +Blocked( +All Time Blocked)?'),
                update(event_product='cassandra', event_category='status', event_type='threadpool_header', rule_type='old')),

            rule(
                capture(r'(?P<pool_name>[A-Za-z0-9_/#]+) +((?P<active>[0-9]+)|n/a) +(?P<pending>[0-9]+) +\(((?P<backpressure>[0-9]+)|N/A)\) +((?P<delayed>[0-9]+)|N/A) +(?P<completed>[0-9]+) +((?P<blocked>[0-9]+)|N/A) +(?P<all_time_blocked>[0-9]+)$'),
                convert(int, 'active', 'pending', 'backpressure', 'delayed', 'completed', 'blocked', 'all_time_blocked'),
                update(event_product='cassandra', event_category='status', event_type='threadpool_status', rule_type='new')),

            rule(
                capture(r'(?P<pool_name>[A-Za-z_-]+) +((?P<active>[0-9]+)|n/a) +(?P<pending>[0-9]+)(/(?P<pending_responses>[0-9]+))?( +(?P<completed>[0-9]+) +(?P<blocked>[0-9]+) +(?P<all_time_blocked>[0-9]+))$'),
                convert(int, 'active', 'pending', 'pending_responses', 'completed', 'blocked', 'all_time_blocked'),
                update(event_product='cassandra', event_category='status', event_type='threadpool_status', rule_type='old')),

            rule(
                capture(r'(?P<pool_name>[A-Za-z0-9_/#]+) +((?P<active>[0-9]+)|n/a) +(?P<pending>[0-9]+)(/(?P<backpressure>[0-9]+))?$'),
                convert(int, 'active', 'pending', 'backpressure'),
                update(event_product='cassandra', event_category='status', event_type='threadpool_status', rule_type='new')),

            rule(
                capture(r'Cache Type +Size +Capacity +KeysToSave(Provider)?'),
                update(event_product='cassandra', event_category='status', event_type='cache_header')),

            rule(
                capture(r'(?P<cache_type>[A-Za-z]*Cache(?! Type)) *(?P<size>[0-9]*) *(?P<capacity>[0-9]*) *(?P<keys_to_save>[^ ]*) *(?P<provider>[A-Za-z_.$]*)'),
                convert(int, 'size', 'capacity'),
                update(event_product='cassandra', event_category='status', event_type='cache_status')),

            rule(
                capture(r'ColumnFamily +Memtable ops,data'),
                update(event_product='cassandra', event_category='status', event_type='memtable_header')),

            rule(
                capture(r'(?P<keyspace>[^.]*)\.(?P<table>[^ ]*) +(?P<ops>[0-9]*),(?P<data>[0-9]*)'),
                convert(int, 'ops', 'data'),
                update(event_product='cassandra', event_category='status', event_type='memtable_status')),
            )

def config_rules():
    """ rules to capture configs """
    return (case('Config'),
            #"Node configuration:[aggregated_request_timeout_in_ms=120000; allocate_tokens_for_keyspace=null; allocate_tokens_for_local_replication_factor=3; write_request_timeout_in_ms=2000]
            rule(
                capture(r'Node configuration:\[(?P<node_configuration>.*)\]'),
                convert(nodeconfig, 'node_configuration'),
                update(event_product='cassandra', event_category='node_config', event_type='node_configuration')),

            case('DseConfig'),

            rule(
                #This machine appears to have 1 thread per CPU core.
                capture(r'This machine appears to have (?P<threads_per_core>[0-9.]*) thread\w? per CPU core.'),
                convert(int, 'threads_per_core'),
                update(event_product='cassandra', event_category='node_config', event_type='cores')),
            rule(
                #This instance appears to have 2 threads per CPU core and 16 total CPU threads.
                #This instance appears to have 1 thread per CPU core and 8 total CPU threads.
                capture(r'This instance appears to have (?P<threads_per_core>[0-9.]*) thread\w? per CPU core and (?P<cpu_cores>[0-9.]*) total CPU threads.'),
                convert(int, 'threads_per_core', 'cpu_cores'),
                update(event_product='cassandra', event_category='node_config', event_type='cores')),
            )

def dd_rules():
    """ rules to capture from database descriptor """
    return (case('DatabaseDescriptor'),
            #6.x disk access mode
            rule(
                #auto mode
                #DiskAccessMode is standard, indexAccessMode is standard, commitlogAccessMode is standard
                capture(r"DiskAccessMode is (?P<logged_disk_access_mode>[A-Za-z]*), indexAccessMode is (?P<logged_index_access_mode>[A-Za-z]*), commitlogAccessMode is (?P<logged_commit_log_access_mode>[A-Za-z]*)"),
                update(event_product='cassandra', event_category='node_config', event_type='disk_access')),
            #4.8 to 5.1 disk access mode
            rule(
                #auto mode
                #DiskAccessMode 'auto' determined to be mmap, indexAccessMode is mmap
                capture(r"DiskAccessMode 'auto' determined to be (?P<logged_disk_access_mode>[A-Za-z]*), indexAccessMode is (?P<logged_index_access_mode>[A-Za-z]*)"),
                update(event_product='cassandra', event_category='node_config', event_type='disk_access')),
            #non-auto mode
            rule(
                #DatabaseDescriptor.java:326 - DiskAccessMode is standard, indexAccessMode is mmap
                capture(r"DiskAccessMode is (?P<logged_disk_access_mode>[A-Za-z]*), indexAccessMode is (?P<logged_index_access_mode>[A-Za-z]*)"),
                update(event_product='cassandra', event_category='node_config', event_type='disk_access')),
            )
