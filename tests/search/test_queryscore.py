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

""" tests the queryscore module """
# pylint: disable=line-too-long
from pysper.search.queryscore import get_title, get_bad_query_summary, get_queries_above_threshold, \
        QueryParams, Parsed, generate_report

def test_get_title():
    """happy path"""
    assert get_title(True, 5) == "top 5 uniquely bad\n------------------\n"

def test_get_bad_query_summary():
    """happy path"""
    bad_queries = [str(x) for x in range(5)]
    assert  get_bad_query_summary(bad_queries, 100) == "\nsuspect queries totals: 5/100 - 5.00%\n"

def test_get_queries_above_threshold():
    """happy path"""
    score_threshold = 1
    bad = get_queries_above_threshold(_add_queries(), score_threshold)
    assert len(bad) == 2

def _add_queries():
    q1 = QueryParams(raw=["q=*:*", "facet=true", "facet.pivot=abc", "f.abc.facet.limit=-1", "facet.limit=-1"],
                     query="q=*:*&facet=true&facet.pivot=abc&f.abc.facet.limit=-1&facet.limit=-1",
                     rows=1,
                     stats_active=False,
                     facet_active=True,
                     pivot_facets=['abc'],
                     field_facet_limits=[-1],
                     global_facet_limit=-1,
                    )
    q2 = QueryParams(raw=["q=*:*", "stats=true"],
                     query="q=*:*&stats=true",
                     rows=1,
                     stats_active=True,
                     facet_active=False,
                     pivot_facets=[],
                     field_facet_limits=[100],
                     global_facet_limit=100,
                    )
    q3 = QueryParams(raw=["q=*:*"],
                     query="q=*:*",
                     rows=1,
                     stats_active=False,
                     facet_active=False,
                     pivot_facets=[],
                     field_facet_limits=[100],
                     global_facet_limit=100,
                    )
    queries = [q1, q2, q3]
    return queries

def test_generate_report():
    """happy path"""
    queries = _add_queries()
    parsed = Parsed(\
            queries=queries,
            top_n_worst=5,
            unique_reasons=False,
            score_threshold=1,
            )
    report = generate_report(parsed)
    assert report == """top 5 worst
-----------
#1.
score: 4
reason(s): (2) unlimited facets, (2) pivot facet
query
-----
q=*:*,
facet=true,
facet.pivot=abc,
f.abc.facet.limit=-1,
facet.limit=-1,
------------------
#2.
score: 1
reason(s): (1) stats query
query
-----
q=*:*,
stats=true,
------------------

suspect queries totals: 2/3 - 66.67%
"""
