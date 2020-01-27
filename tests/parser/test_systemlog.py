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

"""validates the low level parsing of systemlog"""
# pylint: disable=line-too-long
from pysper.parser import systemlog

def test_filtercache_parsing():
    """happy path"""
    lines = [
        "INFO  [RemoteMessageServer query worker - 81] 2020-01-21 11:34:33,033  SolrFilterCache.java:340 - Filter cache org.apache.solr.search.SolrFilterCache$1@7c723229 has reached 8000000 entries of a maximum of 8000000. Evicting oldest entries...",
        "ERROR [RemoteMessageServer query worker - 18] 2020-01-21 11:34:34,475  MessageServer.java:277 - Failed to process request:",
        "INFO  [RemoteMessageServer query worker - 81] 2020-01-21 11:34:35,448  SolrFilterCache.java:356 - ...eviction completed in 1304 milliseconds. Filter cache org.apache.solr.search.SolrFilterCache$1@7c723229 usage is now 32441266 bytes across 4000000 entries.",
        "INFO  [LocalMessageServer query worker - 77] 2020-01-21 12:24:23,912  SolrFilterCache.java:340 - Filter cache org.apache.solr.search.SolrFilterCache$1@324b2c16 has reached 3999974 entries of a maximum of 8000000. Evicting oldest entries...",
        "INFO  [LocalMessageServer query worker - 77] 2020-01-21 12:24:23,912  SolrFilterCache.java:356 - ...eviction completed in 0 milliseconds. Filter cache org.apache.solr.search.SolrFilterCache$1@324b2c16 usage is now 32005744 bytes across 3999962 entries.",
        "INFO  [RemoteMessageServer query worker - 41] 2020-01-21 12:47:26,942  SolrFilterCache.java:311 - Filter cache org.apache.solr.search.SolrFilterCache$6@5af917a4 has reached 16 GB bytes of off-heap memory usage, the maximum is 16 GB. Evicting oldest entries...",
        "INFO  [RemoteMessageServer query worker - 41] 2020-01-21 12:47:26,950  SolrFilterCache.java:328 - ...eviction completed in 9 milliseconds. Filter cache org.apache.solr.search.SolrFilterCache$6@5af917a4 usage is now 114781220 across 159 entries.",
    ]
    events = []
    for line in lines:
        event = systemlog.capture_line(line)
        events.append(event)
    assert len(events) == 7
    assert events[0]['maximum'] == 8000000
    assert events[0]['entries'] == 8000000
    assert events[0]['id'] == '1@7c723229'
    assert events[1]['event_type'] == 'unknown'
    assert events[2]['entries'] == 4000000
    assert events[2]['duration'] == 1304
    assert events[2]['usage'] == 32441266
    assert events[2]['usage_unit'] == 'bytes'
    assert events[2]['id'] == '1@7c723229'
    assert events[3]['entries'] == 3999974 
    assert events[3]['maximum'] == 8000000
    assert events[3]['id'] == '1@324b2c16'
    assert events[4]['entries'] == 3999962
    assert events[4]['duration'] == 0
    assert events[4]['usage'] == 32005744
    assert events[4]['usage_unit'] == 'bytes'
    assert events[4]['id'] == '1@324b2c16'
    assert events[5]['usage'] == 16
    assert events[5]['usage_unit'] == 'GB'
    assert events[5]['maximum'] == 16
    assert events[5]['maximum_unit'] == 'GB'
    assert events[5]['id'] == '6@5af917a4'
    assert events[6]['duration'] == 9
    assert events[6]['usage'] == 114781220
    assert events[6]['entries'] == 159
    assert events[6]['id'] == '6@5af917a4'

