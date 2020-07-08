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

"""the solrqueryagg library"""
import math
from collections import namedtuple, defaultdict, OrderedDict
from operator import attrgetter
from pysper import diag, util, parser

#QueryParams raw detail for query
QueryParams = namedtuple('QueryParams', [ \
        'raw',
        'query',
        'rows',
        'stats_active',
        'facet_active',
        'pivot_facets',
        'field_facet_limits',
        'global_facet_limit',
        ])

#SolrQueryScores stores the query scores and their amount
SolrQueryScores = namedtuple('SolrQueryScores', ['score', 'reasons', 'query'])

Reason = namedtuple('Reason', ['text', 'score'])

#represents the result of parsed
Parsed = namedtuple("Parsed", "queries top_n_worst unique_reasons score_threshold")

def parse(args):
    """reads the args used in the command to determine what to parse
    and how to parse it. The returned object should be suitable for a report"""
    files = diag.find_files(args, args.log_prefix)
    queries = []
    for filename in files:
        with diag.FileWithProgress(filename) as log_file:
            events = parser.read_system_log(log_file)
            for event in events:
                if event.get('event_type', '') == 'query_logs' and \
                event.get('event_product', '') == 'solr' and \
                event.get('event_category', '') == 'query_component':
                    queries.append(parse_event(event))
    return Parsed(
        queries=queries,
        top_n_worst=args.top,
        unique_reasons=args.uniquereasons,
        score_threshold=args.scorethreshold,
        )

def parse_event(event):
    """parse the query"""
    query = event.get("query", '')
    rows = 0
    stats_active = False
    facet_active = False
    pivot_facets = []
    field_facet_limits = []
    global_facet_limit = 0
    raw = query.split("&")
    for param in raw:
        tokens = param.split("=")
        if len(tokens) != 2:
            continue
        arg = tokens[0]
        value = tokens[1]
        if arg == "rows":
            rows = int(value)
        elif arg == "facet.pivot":
            pivot_facets = value.split(",")
        elif arg == "facet.limit":
            global_facet_limit = int(value)
        elif arg.endswith("facet.limit"): #this is relyingon the previous line to not greedily match the global case too
            field_facet_limits.append(int(value))
        elif arg == "stats":
            stats_active = value == "true"
        elif arg == "facet":
            facet_active = value == "true"
    return QueryParams(
        raw=raw,
        query=query,
        rows=rows,
        pivot_facets=pivot_facets,
        stats_active=stats_active,
        facet_active=facet_active,
        field_facet_limits=field_facet_limits,
        global_facet_limit=global_facet_limit,
        )

def get_queries_above_threshold(queries, score_threshold):
    """finds all queries above the configured score threshold"""
    queries_above_threshold = []
    for q in queries:
        #score queries
        score, reasons = score_query(q)
        if score >= score_threshold:
            queries_above_threshold.append(SolrQueryScores(score, reasons, clean(q.raw)))
    return queries_above_threshold

def get_title(unique_reasons, top_n_worst):
    """generate the report title"""
    title_end = ""
    if unique_reasons:
        title_end = "uniquely bad"
    else:
        title_end = "worst"
    title = "top %i %s" % (top_n_worst, title_end)
    underline = util.write_underline(title)
    return "%s\n%s\n" % (title, underline)

def get_bad_query_summary(queries_above_threshold, total):
    """generates the bad query summary"""
    total_suspect = len(queries_above_threshold)
    percent = 0.0
    if total_suspect > 0:
        percent = (float(total_suspect) / float(total)) * float(100.0)
    return "\nsuspect queries totals: %i/%i - %.2f%%\n" % (total_suspect, total, percent)

def add_body(queries_above_threshold, unique_reasons, top_n_worst):
    """adds the report body"""
    builder = []
    visited_reasons = OrderedDict()
    count = 0
    for query_score in queries_above_threshold:
        reasons_array = []
        for reason, score in query_score.reasons.items():
            reasons_array.append(Reason(reason, score))
        sorted(reasons_array, key=attrgetter('score'))
        reason_string_array = []
        for reason in reasons_array:
            reason_string_array.append("(%i) %s" % (reason.score, reason.text))
        reason_string = ", ".join(reason_string_array)
        if unique_reasons:
            if reason_string in visited_reasons:
                continue
            visited_reasons[reason_string] = True
        count += 1
        if count > top_n_worst:
            break
        query_score_entry = "#%i.\nscore: %i\nreason(s): %s\nquery\n-----\n" % (
            count,
            query_score.score,
            reason_string,
            )
        builder.append(query_score_entry)
        for param in query_score.query:
            builder.append("%s,\n" % param)
        builder.append("------------------\n")
    return "".join(builder)

def generate_report(parsed):
    """takes a parsed object and converts in into text suitable for console output"""
    builder = []
    queries_above_threshold = get_queries_above_threshold(parsed.queries, parsed.score_threshold)
    total = len(parsed.queries)
    if total == 0:
        return "no queries found in log! Make sure you run the following before collecting a " + \
                "diag tarball:\n\n\tnodetool setlogginglevel org.apache.solr.handler.component.QueryComponent DEBUG\n\n"
    builder.append(get_title(parsed.unique_reasons, parsed.top_n_worst))
    sorted(queries_above_threshold, key=attrgetter("score"))
    builder.append(add_body(queries_above_threshold, parsed.unique_reasons, parsed.top_n_worst))
    builder.append(get_bad_query_summary(queries_above_threshold, total))
    return "".join(builder)

TOO_MANY_ROWS = 9999
UNLIMITED = -1

def _count_reason(reasons, key, count=1):
    if key not in reasons:
        reasons[key] = 0
    reasons[key] += count

def score_query(query):
    """gives the query a score based on the number of bad things going on"""
    reasons = OrderedDict()
    score = 0
    for limit in query.field_facet_limits:
        if limit == UNLIMITED:
            score += 1
            _count_reason(reasons, "unlimited facets")
        if query.global_facet_limit == UNLIMITED:
            score += 1
            _count_reason(reasons, "unlimited facets")
    pivot_depth = len(query.pivot_facets)
    if pivot_depth > 0:
        pivot_depth_score = math.exp(pivot_depth)
        score += pivot_depth_score
        _count_reason(reasons, "pivot facet", pivot_depth_score)
    if query.stats_active:
        score += 1
        _count_reason(reasons, "stats query")
    if query.rows > TOO_MANY_ROWS:
        modifier = round((float(query.rows) / float(TOO_MANY_ROWS)))
        score += modifier
        _count_reason(reasons,  "10k+ rows", modifier)
    return score, reasons

def clean(query_params):
    """clean removes all the shard stuff that's not useful for analysis and is usually present"""
    shard_limited = [\
        "ids",
        "NOW",
        "cl",
        "ForceShardHandler",
        "group.distributed.second",
        "group.distributed.first",
        "ShardRouter.SHARD_COORDINATOR_IP",
        "ShardRouter.VNODES_ENABLED",
        "ShardRouter.SHARD_COORDINATOR_ID",
        "version",
        "shard.url",
        "isShard",
        "distrib",
        "fsv",
        "shards.purpose",
        "wt",
        ]
    cleaned = []
    for t in query_params:
        tokens = t.split("=")
        found = False
        for c in shard_limited:
            if tokens[0] == c:
                found = True
                break

        if not found and tokens[0].startswith("group.topgroups."):
            #remove token range partes of queries
            if tokens[0] == "fq":
                #clean out token fqs and _parent fqs as they're nonsense
                value = tokens[1]
                if value == "-_parent_:F" or value.startswith("{!caching_lucene}(_token_long"):
                    continue
        cleaned.append(t)
    sorted(cleaned)
    return cleaned
