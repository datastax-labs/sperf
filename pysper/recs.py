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

"""the recommendation engine for sperf"""
from enum import Enum
import sys

class Stage:
    """stage dataclass"""
    #pylint: disable=too-many-arguments
    def __init__(self, name="", active=0, pending=0,
                 local_backpressure=0, completed=0, blocked=0,
                 all_time_blocked=0):
        self.name = name
        self.active = active
        self.pending = pending
        self.local_backpressure = local_backpressure
        self.completed = completed
        self.blocked = blocked
        self.all_time_blocked = all_time_blocked

class Engine:
    """stage analyzer will make recommendations on stages based on
    the type of stage and it's stats"""
    def __init__(self):
        self.memtable_lower_rec = "lower memtable_cleanup_threshold in cassandra.yaml"
        self.flush_writer_raise_rec = "raise memtable_flush_writers in cassandra.yaml"
        self.compaction_throughput_raise_rec = "raise compaction_throughput_in_mb in cassandra.yaml"
        self.ntr_queue_raise_rec = "raise or set -Dcassandra.max_queued_native_transport_requests= " + \
                "(valid range is 1024-8192)"
        self.tpc_cores_raise_rec = "raise or set tpc_concurrent_requests_limit in " + \
                "cassandra.yaml (default is 128), if CPU is underutilized."
        self.engine = {
            "TPC/all/WRITE_REMOTE": self._write_remote,
            "TPC/all/WRITE_LOCAL": self._write_local,
            "TPC/all/WRITE_MEMTABLE_FULL": self._memtable_full,
            "CompactionManger": self._compaction,
            "Native-Transport-Requests": self._ntr,
            "MemtableFlushWriter": self._memtable_flush_writer,
            "MutationStage": self._mutation,
        }

    def _write_remote(self, stage):
        if stage.pending > 10000:
            return "pending remote writes over 10000", self.memtable_lower_rec
        return (None, None)

    def _write_local(self, stage):
        if stage.pending > 10000:
            return "pending local writes over 10000", self.memtable_lower_rec
        return None, None

    def _memtable_full(self, stage):
        if stage.active > 0:
            return "full memtable", self.memtable_lower_rec
        if stage.completed > 0:
            reason = "full memtable stages previously completed is too high"
            return  reason, self.memtable_lower_rec
        return None, None

    def _compaction(self, stage):
        if stage.pending > 100:
            reason = "more than 100 compactions behind"
            return reason, self.compaction_throughput_raise_rec
        return None, None

    def _ntr(self, stage):
        if stage.blocked > 10:
            return "blocked NTR over 10", self.ntr_queue_raise_rec
        if stage.all_time_blocked > 100:
            reason = "more than 100 blocked NTR all time"
            return reason, self.ntr_queue_raise_rec
        return None, None

    def _memtable_flush_writer(self, stage):
        if stage.pending > 5:
            reason = "memtable flush writers pending over 5"
            return reason, self.flush_writer_raise_rec
        if stage.blocked > 0:
            reason = "memtable flush writers blocked greater than zero"
            return reason, self.memtable_lower_rec
        return None, None

    def _mutation(self, stage):
        if stage.pending > 10000:
            return "mutations pending over 10000", self.memtable_lower_rec
        return None, None

    def analyze_stage(self, stage):
        """analyzes a stage and returns recommendations based on the stage details"""
        reason = None
        rec = None
        if stage.name not in self.engine:
            if stage.local_backpressure > 0:
                reason = "local backpressure is present"
                return reason, self.tpc_cores_raise_rec
        else:
            rule = self.engine[stage.name]
            reason, rec = rule(stage)
        return reason, rec

def _calculate_eviction_state(node):
    """pick the ideal recommendation for a given node"""
    freq = getattr(node, "avg_evict_freq", sys.float_info.max)
    dur = getattr(node, "avg_evict_duration", 0)
    ratio = getattr(node, "perc_item_limit", 0.0)
    too_frequent = 0.01 < freq < 20.00
    too_slow = dur > 1000
    reason = None
    if dur == 0: # duration guards againt all the case of no evictions
        reason = EvictionReason.NONE
    elif ratio < 0.10:
        reason = EvictionReason.BYTE
    elif ratio > 0.90:
        reason = EvictionReason.ITEM
    else:
        reason = EvictionReason.MIXED
    return too_frequent, too_slow, reason

class EvictionReason(Enum):
    """eviction reason for filter cache statistics"""
    NONE = 1
    MIXED = 2
    ITEM = 3
    BYTE = 4

def analyze_filter_cache_stats(node):
    """look at filter cache statistics and generate recommendations"""
    step = 8
    min_limit = 32000
    last_evict_item_limit = getattr(node, "last_evict_item_limit", 0)
    too_low = last_evict_item_limit <= min_limit
    too_frequent, too_slow, eviction_reason = _calculate_eviction_state(node)
    if eviction_reason == EvictionReason.NONE:
        #means no evictions
        return None, None
    if too_frequent and too_slow:
        reason = "Filter cache evictions are happening too frequently and too slowly."
        rec = "Make more FQ queries uncached. " + \
            "Example: change \"fq\":\"status:DELETED\" to \"fq\":\"{!cached=false}status:DELETED\"."
        return reason, rec
    if too_frequent:
        reason = "Filter cache evictions are happening too frequently."
        if eviction_reason == EvictionReason.ITEM:
            rec = "Raise filter cache item limit from %i to %i via -Dsolr.solrfiltercache.maxSize." \
                % (last_evict_item_limit, min(256000, last_evict_item_limit * step))
        elif eviction_reason == EvictionReason.BYTE:
            rec = "Raise filtercache lowWaterMarkMB and highWaterMarkMB on solr cores. " + \
                  "Consult documentation for your DSE version."
        else:
            rec = "Raise filter cache byte limit from %i to %i via -Dsolr.solrfiltercache.maxSize "  \
                % (last_evict_item_limit, min(256000, last_evict_item_limit * step)) + \
                    "AND raise filtercache lowWaterMarkMB and highWaterMarkMB " + \
                    "on solr cores. Consult documentation for your DSE version."
        return reason, rec
    if too_slow and too_low:
        reason = "Filter cache eviction duration long but limit is already too low."
        rec = "Make more FQ queries uncached. " + \
            "Example: change \"fq\":\"status:DELETED\" to \"fq\":\"{!cached=false}status:DELETED\"."
        return reason, rec
    if too_slow:
        reason = "Filter cache eviction duration is too long."
        if eviction_reason == EvictionReason.ITEM:
            rec = "Lower filter cache item limit from %i to %i via -Dsolr.solrfiltercache.maxSize." \
                % (last_evict_item_limit, max(min_limit, last_evict_item_limit / step))
        elif eviction_reason == EvictionReason.BYTE:
            rec = "Lower filtercache lowWaterMarkMB and highWaterMarkMB on solr cores. " + \
                  "Consult documentation for your DSE version."
        else:
            rec = "Lower filter cache byte limit from %i to %i via -Dsolr.solrfiltercache.maxSize "  \
                % (last_evict_item_limit, max(min_limit, last_evict_item_limit / step)) + \
                   "AND lower filtercache lowWaterMarkMB and highWaterMarkMB on " + \
                   "solr cores. Consult documentation for your DSE version."
        return reason, rec
    return None, None
