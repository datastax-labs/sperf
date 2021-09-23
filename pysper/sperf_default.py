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
"""sperf default command run when you type `sperf`"""
from collections import OrderedDict
from dataclasses import dataclass

from pysper import humanize
from pysper.core.diag import parse_diag
from pysper import diag
from pysper import parser, util
from pysper.core.diag.reporter import (
    format_gc,
    format_table_stat,
    format_table_stat_float,
    format_largest_table,
    format_busiest_table,
    format_partition_bytes,
    simple_format,
    format_table_loc,
    format_disk_access_mode,
)


@dataclass
class StatusLoggerCounter:
    delayed: int = 0
    pending: int = 0
    blocked: int = 0


def parse(args):
    """read diag tarball"""
    res = parse_diag(args, lambda n: [calculate(n)])
    # use debug logs for statuslogger output on 5.1.17+, 6.0.10+, 6.7.5+ and 6.8+
    debug_logs = diag.find_logs(args.diag_dir, args.debug_log_prefix)
    parsed = OrderedDict()
    parsed["diag_dir"] = args.diag_dir
    parsed["warnings"] = res.get("warnings")
    parsed["configs"] = res.get("original_configs")
    parsed["summary"] = res.get("configs")[0]
    parsed["rec_logs"] = res.get("system_logs") + debug_logs
    return parsed


def calculate(node_config):
    """aggregate parsed information for the report"""
    summary = OrderedDict()
    summary["nodes"] = OrderedDict()
    summary["versions"] = set()
    summary["cassandra_versions"] = set()
    summary["spark_versions"] = set()
    summary["solr_versions"] = set()
    summary["workloads"] = OrderedDict()
    summary["nodes_list"] = []
    for node, config in node_config.items():
        if config.get("version"):
            summary["versions"].add(config.get("version"))
        if config.get("cassandra_version"):
            summary["cassandra_versions"].add(config.get("cassandra_version"))
        else:
            version = config.get("version")
            if version and version.startswith("6"):
                summary["cassandra_versions"].add("DSE private fork")
        if config.get("solr_version"):
            summary["solr_versions"].add(config.get("solr_version"))
        if config.get("spark_version"):
            summary["spark_versions"].add(config.get("spark_version"))
        summary["nodes_list"].append(node)
    summary["nodes"] = len(summary["nodes_list"])
    summary["nodes_list"] = sorted(summary["nodes_list"], reverse=True)
    return summary


def _recs_on_stages(
    recommendations: list,
    gc_over_500: int,
    counter: StatusLoggerCounter,
):
    if gc_over_500 > 0:
        recommendations.append(
            {
                "issue": "There were %i incidents of GC over 500ms" % gc_over_500,
                "rec": "Run `sperf core gc` for more analysis",
            }
        )
    if counter.delayed > 0:
        recommendations.append(
            {
                "issue": "There were %i incidents of local backpressure"
                % counter.delayed,
                "rec": "Run `sperf core statuslogger` for more analysis",
            }
        )
    if counter.blocked > 0:
        recommendations.append(
            {
                "issue": "There were %i incidents of signficantly blocked stages"
                % counter.blocked,
                "rec": "Run `sperf core statuslogger` for more analysis",
            }
        )
    if counter.pending > 0:
        recommendations.append(
            {
                "issue": "There were %i incidents of signficantly pending stages"
                % counter.pending,
                "rec": "Run `sperf core statuslogger` for more analysis",
            }
        )


def _recs_on_configs(recommendations, configs):
    recs_by_issue = OrderedDict()
    for node, config in configs.items():
        disk_access = format_disk_access_mode(config)
        cassandra_version = config.get("cassandra_version")
        cass_major_version = None
        cass_minor_version = None
        if cassandra_version:
            tokens = cassandra_version.split(".")
            cass_major_version = int(tokens[0])
            cass_minor_version = int(tokens[1])
        if cassandra_version and disk_access == "mmap":
            if cass_major_version == 3 or (
                cass_major_version == 2 and cass_minor_version == 2
            ):
                issue = (
                    "Disk access mode mmap causes problems with "
                    + "performance on version %s of Cassandra. (SUPPORT-753)"
                    % cassandra_version
                )
                issue = (
                    issue
                    + " https://support.datastax.com/hc/en-us/articles/360027838911"
                )
                if issue not in recs_by_issue:
                    recs_by_issue[issue] = {
                        "issue": issue,
                        "rec": "Set disk_access_mode: mmap_index_only in cassandra.yaml",
                        "nodes": [node],
                    }
                else:
                    recs_by_issue[issue]["nodes"].append(node)
        dse_version = config.get("version")
        dse_major_version = None
        if dse_version:
            tokens = dse_version.split(".")
            dse_major_version = int(tokens[0])
        if dse_version and disk_access != "standard":
            if dse_major_version > 5:
                issue = (
                    "Disk acess mode %s causes problems " % disk_access
                    + "with performance on version %s of DSE. (SUPPORT-752)"
                    % dse_version
                )
                issue = (
                    issue
                    + " https://support.datastax.com/hc/en-us/articles/360028294671"
                )
                if issue not in recs_by_issue:
                    recs_by_issue[issue] = {
                        "issue": issue,
                        "rec": "set disk_access_mode: standard in cassandra.yaml",
                        "nodes": [node],
                    }
                else:
                    recs_by_issue[issue]["nodes"].append(node)
    total_nodes = len(configs)
    for rec in recs_by_issue.values():
        if len(rec.get("nodes")) == total_nodes:
            rec["nodes"] = ["all"]
        recommendations.append(rec)


def _status_logger_counter(event, counter):
    if "delayed" in event and event["delayed"]:
        val = event["delayed"]
        if val > 0:
            counter.delayed += 1
    if "pending" in event and event["pending"]:
        val = event["pending"]
        if val > 100:
            counter.pending += 1
    if "blocked" in event and event["blocked"]:
        val = event["blocked"]
        if val > 10:
            counter.blocked += 1


def generate_recommendations(parsed):
    """generate recommendations off the parsed data"""
    gc_over_500 = 0
    counter = StatusLoggerCounter()
    solr_index_backoff = OrderedDict()
    solr_index_restore = OrderedDict()
    drops_remote_only = 0
    drop_sums = 0
    drop_types = set()
    event_filter = diag.UniqEventPerNodeFilter()
    for rec_log in parsed["rec_logs"]:
        node = util.extract_node_name(rec_log)
        event_filter.set_node(node)
        with diag.FileWithProgress(rec_log) as rec_log_file:
            if rec_log_file.error:
                parsed["warnings"].append(
                    "%s failed with error %s" % (rec_log, rec_log_file.error)
                )
            else:
                statuslogger_fixer = diag.UnknownStatusLoggerWriter()
                events = parser.read_system_log(rec_log_file)
                for event in [e for e in events if not event_filter.is_duplicate(e)]:
                    statuslogger_fixer.check(event)
                    if event.get("event_type") == "unknown":
                        continue
                    if (
                        event.get("event_type") == "pause"
                        and event.get("event_category") == "garbage_collection"
                    ):
                        if event.get("duration") > 500:
                            gc_over_500 += 1
                    elif event.get("event_category") == "indexing":
                        core_name = event.get("core_name")
                        d = event.get("date")
                        if event.get("event_type") == "increase_soft_commit":
                            if core_name in solr_index_backoff:
                                solr_index_backoff[core_name]["count"] += 1
                                solr_index_backoff[core_name]["dates"].append(d)
                            else:
                                solr_index_backoff[core_name] = {
                                    "count": 1,
                                    "dates": [event.get("date")],
                                }
                        elif event.get("event_type") == "restore_soft_commit":
                            if core_name in solr_index_restore:
                                solr_index_restore[core_name]["count"] += 1
                                solr_index_restore[core_name]["dates"].append(d)
                            else:
                                solr_index_restore[core_name] = {
                                    "count": 1,
                                    "dates": [event.get("date")],
                                }
                    if event.get("event_type") == "drops":
                        local = event.get("localCount")
                        remote = event.get("remoteCount")
                        drop_type = event.get("messageType")
                        drop_types.add(drop_type)
                        drop_sums += (local + remote)
                        if remote > 0 and local == 0:
                            drops_remote_only += 1
                        
                    _status_logger_counter(event, counter)
    recommendations = []
    _recs_on_stages(recommendations, gc_over_500, counter)
    _recs_on_configs(recommendations, parsed["configs"])
    _recs_on_solr(recommendations, solr_index_backoff, solr_index_restore)
    _recs_on_drops(recommendations, drops_remote_only, drop_types, drop_sums)
    #_recs_on_zero_copy(recommendations, zero_copy_errors)
    #_recs_on_rejects(recommendations, rejected)
    #_recs_on_bp(recommendations, bp)
    #_recs_on_core_balance(recommendations, core_balance)
    return recommendations

def _recs_on_drops(recommendations, drops_remote_only, drop_types, drop_sums):
    """sums up the drops"""
    if drops_remote_only > 0:
        recommendations.append(
                    {
                    "issue": "There were %i incidents of remote only drops indicating issues with other nodes, the network or TPC balance"
                    % drops_remote_only,
                    "rec": "If this is DSE 6.0.x-6.8.4 upgrade to 6.8.latest https://datastax.jira.com/browse/DB-4683 (DSE 6.0.x-6.8.4 affected). Otherwise check for network issues or offline nodes",
                    }
                )
    if drop_sums > 0:
        recommendations.append(
                    {
                    "issue": "There were dropped mutations present of the following types: %s for a total of %i drops"
                    % (", ".join(drop_types), drop_sums),
                    "rec": "Run sperf core statuslogger and look for high pending stages for those messages types",
                    }
                )
def _recs_on_solr(recommendations, solr_index_backoff, solr_index_restore):
    """sees if we have auto soft commit increases and restores and makes recommendations accordingly"""
    if len(solr_index_backoff) > 0 :
        for core in solr_index_backoff.keys():
            data = solr_index_backoff[core]
            dates_str = ", ".join(list(map(lambda a:a.strftime("%Y-%m-%d %H:%M:%S"), data["dates"])))
            if core in solr_index_restore:
                recommendations.append(
                    {
                    "issue": "There were %i incidents of indexing not be able to keep up for core %s at the following times: %s"
                    % (data["count"], core, dates_str),
                    "rec": "Consider raising auto soft commit to 60000 for core '%s' to avoid dropped mutations and timeouts"
                    % core,
                    }
                )
            else:
                recommendations.append(
                    {
                    "issue": "There were %i incidents of indexing not be able to keep up for core %s at the following times: %s. There is nothing in the log indicating restore to the configured auto soft commit."
                    % (data["count"], dates_str, core),
                    "rec": "Strongly consider raising auto soft commit for core '%s' to avoid dropped mutations and timeouts. This core never restores to the configured value, so there is no benefit to keeping it where it is at"
                    % core,
                    }
                )

def generate_report(parsed, recommendations):
    """generates report from calculated data"""
    calculated = parsed.get("summary")
    # allows nodes to be tabbed out for a block look
    table = []
    table.append(["nodes", simple_format(calculated.get("nodes"))])
    table.append(
        ["dse version(s) (startup logs)", format_list(calculated.get("versions", []))]
    )
    table.append(
        [
            "cassandra version(s) (startup logs)",
            format_list(calculated.get("cassandra_versions", [])),
        ]
    )
    table.append(
        [
            "solr version(s) (startup logs)",
            format_list(calculated.get("solr_versions", [])),
        ]
    )
    table.append(
        [
            "spark version(s) (startup logs)",
            format_list(calculated.get("spark_versions", [])),
        ]
    )
    table.append(["worst gc pause (system logs)", format_gc(calculated)])
    table.append(
        [
            "worst read latency (cfstats)",
            format_table_stat_float(
                calculated.get("worst_read_latency"), val_suffix="ms"
            ),
        ]
    )
    table.append(
        [
            "worst write latency (cfstats)",
            format_table_stat_float(
                calculated.get("worst_write_latency"), val_suffix="ms"
            ),
        ]
    )
    table.append(
        [
            "worst tombstones query (cfstats)",
            format_table_stat(calculated.get("worst_tombstone")),
        ]
    )
    table.append(
        [
            "worst live cells query (cfstats)",
            format_table_stat(calculated.get("worst_live_cells")),
        ]
    )
    table.append(["largest table (cfstats)", format_largest_table(calculated)])
    table.append(
        [
            "busiest table reads (cfstats)",
            format_busiest_table(calculated.get("busiest_table_reads"), "reads"),
        ]
    )
    table.append(
        [
            "busiest table writes (cfstats)",
            format_busiest_table(calculated.get("busiest_table_writes"), "writes"),
        ]
    )
    table.append(
        [
            "largest partition (cfstats)",
            format_partition_bytes(calculated.get("worst_part_size"), 2)
            + " "
            + format_table_loc(calculated.get("worst_part_size")),
        ]
    )
    humanize.pad_table(table)
    report = [""]
    for row in table:
        report.append(" ".join(row))

    report.append("")
    report.append("errors parsing")
    report.append("--------------")
    if parsed.get("warnings"):
        for warning in parsed.get("warnings"):
            report.append("* %s" % warning)
    else:
        report.append("No parsing errors")
    # "* random error is here"
    report.append("")
    report.append("recommendations")
    report.append("---------------")
    # recs here
    if recommendations:
        for rec in recommendations:
            rec_str = "* %s." % rec.get("issue")
            if rec.get("rec"):
                rec_str = rec_str + " %s." % rec.get("rec")
            report.append(rec_str)
            if rec.get("nodes"):
                # allows nodes to be tabbed out for a block look
                nodes_fmtd = humanize.format_list(
                    rec.get("nodes"), newline="\n" + " " * 18
                )
                report.append("  nodes affected: %s" % nodes_fmtd)
                report.append("  --")
    else:
        report.append("No recommendations")
    return "\n".join(report)


def format_map(m):
    """pleasing output for dc name and node count"""
    keys = sorted(m)
    items = []
    for key in keys:
        count = m[key]
        items.append("%s: %s" % (key, count))
    if not m:
        return "N/A"
    return "{ %s }" % ", ".join(items)


def format_list(to_format):
    """pleasing output for dc name and node count"""
    if not to_format:
        return "N/A"
    return "{ %s }" % ", ".join(to_format)


def run(args):
    """launch point for sperf default command"""
    parsed = parse(args)
    recommendations = generate_recommendations(parsed)
    print(generate_report(parsed, recommendations))
