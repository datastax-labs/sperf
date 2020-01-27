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

"""test the recs module"""
import types
from pysper import recs


def test_high_pending_write_remote():
    """verify StageAnalyzer makes recs on high pending writes"""
    analyzer = recs.Engine()
    stage = recs.Stage(
        name="TPC/all/WRITE_REMOTE",
        pending=10001,
        active=0,
        local_backpressure=0,
        completed=0,
        blocked=0,
        all_time_blocked=0,
        )
    reason, rec = analyzer.analyze_stage(stage)
    assert rec == "lower memtable_cleanup_threshold in cassandra.yaml"
    assert reason == "pending remote writes over 10000"
    stage.pending = 9999
    reason, rec = analyzer.analyze_stage(stage)
    assert not rec
    assert not reason

def test_high_pending_write_local():
    """verify StageAnalyzer makes recs on high pending local writes"""
    analyzer = recs.Engine()
    stage = recs.Stage(
        name="TPC/all/WRITE_LOCAL",
        pending=10001,
        active=0,
        local_backpressure=0,
        completed=0,
        blocked=0,
        all_time_blocked=0,
        )
    reason, rec = analyzer.analyze_stage(stage)
    assert rec == "lower memtable_cleanup_threshold in cassandra.yaml"
    assert reason == "pending local writes over 10000"
    stage.pending = 9999
    reason, rec = analyzer.analyze_stage(stage)
    assert not rec
    assert not reason

def test_high_pending_mutations():
    """verify StageAnalyzer makes recs on high pending local writes"""
    analyzer = recs.Engine()
    stage = recs.Stage(
        name="MutationStage",
        pending=10001,
        active=0,
        local_backpressure=0,
        completed=0,
        blocked=0,
        all_time_blocked=0,
        )
    reason, rec = analyzer.analyze_stage(stage)
    assert rec == "lower memtable_cleanup_threshold in cassandra.yaml"
    assert reason == "mutations pending over 10000"
    stage.pending = 9999
    reason, rec = analyzer.analyze_stage(stage)
    assert not rec
    assert not reason

def test_tpc_backpressure():
    """verify StageAnalyzer makes recs on any backpressure"""
    analyzer = recs.Engine()
    stage = recs.Stage(
        name="TPC/2",
        pending=1,
        active=0,
        local_backpressure=1,
        completed=0,
        blocked=0,
        all_time_blocked=0,
        )
    reason, rec = analyzer.analyze_stage(stage)
    assert rec == "raise or set tpc_concurrent_requests_limit in " + \
                            "cassandra.yaml (default is 128), if CPU is underutilized."
    assert reason == "local backpressure is present"
    stage.pending = 0
    stage.local_backpressure = 0
    reason, rec = analyzer.analyze_stage(stage)
    assert not rec
    assert not reason

def test_full_memtable():
    """verify StageAnalyzer """
    analyzer = recs.Engine()
    stage = recs.Stage(
        name="TPC/all/WRITE_MEMTABLE_FULL",
        pending=0,
        active=1,
        local_backpressure=0,
        completed=0,
        blocked=0,
        all_time_blocked=0,
        )
    reason, rec = analyzer.analyze_stage(stage)
    assert rec == "lower memtable_cleanup_threshold in cassandra.yaml"
    assert reason == "full memtable"
    stage.active = 0
    reason, rec = analyzer.analyze_stage(stage)
    assert not rec
    assert not reason

def test_full_memtable_completed():
    """verify full memtable historically completed"""
    analyzer = recs.Engine()
    stage = recs.Stage(
        name="TPC/all/WRITE_MEMTABLE_FULL",
        pending=0,
        active=0,
        local_backpressure=0,
        completed=1,
        blocked=0,
        all_time_blocked=0,
        )
    reason, rec = analyzer.analyze_stage(stage)
    assert rec == "lower memtable_cleanup_threshold in cassandra.yaml"
    assert reason == "full memtable stages previously completed is too high"
    stage.completed = 0
    reason, rec = analyzer.analyze_stage(stage)
    assert not rec
    assert not reason

def test_compactions_behind():
    """verify compactions analysis"""
    analyzer = recs.Engine()
    stage = recs.Stage(
        name="CompactionManger",
        pending=101,
        active=0,
        local_backpressure=0,
        completed=0,
        blocked=0,
        all_time_blocked=0,
        )
    reason, rec = analyzer.analyze_stage(stage)
    assert rec == "raise compaction_throughput_in_mb in cassandra.yaml"
    assert reason == "more than 100 compactions behind"
    stage.pending = 0
    reason, rec = analyzer.analyze_stage(stage)
    assert not rec
    assert not reason

def test_memtable_flush_writer_pending():
    """verify flush writer pending"""
    analyzer = recs.Engine()
    stage = recs.Stage(
        name="MemtableFlushWriter",
        pending=6,
        active=0,
        local_backpressure=0,
        completed=0,
        blocked=0,
        all_time_blocked=0,
        )
    reason, rec = analyzer.analyze_stage(stage)
    assert rec == "raise memtable_flush_writers in cassandra.yaml"
    assert reason == "memtable flush writers pending over 5"
    stage.pending = 0
    reason, rec = analyzer.analyze_stage(stage)
    assert not rec
    assert not reason

def test_memtable_flush_writer_blocked():
    """verify flush writer blocked"""
    analyzer = recs.Engine()
    stage = recs.Stage(
        name="MemtableFlushWriter",
        pending=0,
        active=0,
        local_backpressure=0,
        completed=0,
        blocked=1,
        all_time_blocked=0,
        )
    reason, rec = analyzer.analyze_stage(stage)
    assert rec == "lower memtable_cleanup_threshold in cassandra.yaml"
    assert reason == "memtable flush writers blocked greater than zero"
    stage.blocked = 0
    reason, rec = analyzer.analyze_stage(stage)
    assert not rec
    assert not reason

def test_ntr_blocked():
    """verify ntr blocked"""
    analyzer = recs.Engine()
    stage = recs.Stage(
        name="Native-Transport-Requests",
        pending=0,
        active=0,
        local_backpressure=0,
        completed=0,
        blocked=11,
        all_time_blocked=0,
        )
    reason, rec = analyzer.analyze_stage(stage)
    assert rec == "raise or set -Dcassandra.max_queued_native_transport_requests= " + \
                            "(valid range is 1024-8192)"
    assert reason == "blocked NTR over 10"
    stage.blocked = 0
    reason, rec = analyzer.analyze_stage(stage)
    assert not rec
    assert not reason

def test_ntr_all_time_blocked():
    """verify ntr blocked"""
    analyzer = recs.Engine()
    stage = recs.Stage(
        name="Native-Transport-Requests",
        pending=0,
        active=0,
        local_backpressure=0,
        completed=0,
        blocked=0,
        all_time_blocked=101,
        )
    reason, rec = analyzer.analyze_stage(stage)
    assert rec == "raise or set -Dcassandra.max_queued_native_transport_requests= " + \
                            "(valid range is 1024-8192)"
    assert reason == "more than 100 blocked NTR all time"
    stage.all_time_blocked = 0
    reason, rec = analyzer.analyze_stage(stage)
    assert not rec
    assert not reason

def test_filter_cache_analysis_frequent_evictions():
    """when filter cache eviction freq is sooner than ever 20 seconds recommend raising limits"""
    stats = types.SimpleNamespace()
    stats.avg_evict_freq = 19.9
    stats.avg_evict_duration = 10
    stats.last_evict_item_limit = 32000
    stats.perc_item_limit = 0.95
    reason, rec = recs.analyze_filter_cache_stats(stats)
    assert reason == "Filter cache evictions are happening too frequently."
    assert rec == "Raise filter cache item limit from 32000 to 256000 via -Dsolr.solrfiltercache.maxSize."

def test_filter_cache_analysis_long_duration_evictions():
    """when filter cache eviction duration is longer than 1 second recommend raising limits"""
    stats = types.SimpleNamespace()
    stats.avg_evict_freq = 60.0
    stats.avg_evict_duration = 1001
    stats.last_evict_item_limit = 256000
    stats.perc_item_limit = 0.95
    reason, rec = recs.analyze_filter_cache_stats(stats)
    assert reason == "Filter cache eviction duration is too long."
    assert rec == "Lower filter cache item limit from 256000 to 32000 via -Dsolr.solrfiltercache.maxSize."

def test_filter_cache_analysis_frequent_long_evictions():
    """when filter cache eviction duration is longer than 1 second recommend raising limits"""
    stats = types.SimpleNamespace()
    stats.avg_evict_freq = 10.0
    stats.avg_evict_duration = 60001
    stats.last_evict_item_limit = 256000
    stats.perc_item_limit = 0.95
    reason, rec = recs.analyze_filter_cache_stats(stats)
    assert reason == "Filter cache evictions are happening too frequently and too slowly."
    assert rec == "Make more FQ queries uncached. " + \
            "Example: change \"fq\":\"status:DELETED\" to \"fq\":\"{!cached=false}status:DELETED\"."

def test_limit_eviction_limit_already_reached():
    """already as low as one can go"""
    stats = types.SimpleNamespace()
    stats.avg_evict_freq = 100.0
    stats.avg_evict_duration = 1244.0
    stats.last_evict_item_limit = 31000
    stats.perc_item_limit = 0.95
    reason, rec = recs.analyze_filter_cache_stats(stats)
    assert reason == "Filter cache eviction duration long but limit is already too low."
    assert rec == "Make more FQ queries uncached. " + \
            "Example: change \"fq\":\"status:DELETED\" to \"fq\":\"{!cached=false}status:DELETED\"."

def test_filter_cache_analysis_zero_set():
    """when filter cache eviction duration is longer than 1 second recommend raising limits"""
    stats = types.SimpleNamespace()
    stats.avg_evict_freq = 0.0
    stats.avg_evict_duration = 0.0
    stats.perc_item_limit = 0.0
    reason, rec = recs.analyze_filter_cache_stats(stats)
    assert not reason
    assert not rec

def test_filter_cache_analysis_none_set():
    """when filter cache eviction duration is longer than 1 second recommend raising limits"""
    stats = types.SimpleNamespace()
    reason, rec = recs.analyze_filter_cache_stats(stats)
    assert not reason
    assert not rec
