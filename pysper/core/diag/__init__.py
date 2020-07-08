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

"""information collection and report writing for the cassread tool"""
from pysper.core.diag import reporter, node_env, table_stats, config_diff, read_ahead
from pysper import diag, util

def generate_report(parsed):
    """reads the parsed parameters and converts them into a well formatted report string"""
    report = []
    configs = parsed.get('configs')
    if not configs:
        return "No node data found\nLooked in '%s'" % parsed.get('diag_dir')
    for idx, config in enumerate(configs):
        report.append("")
        title = "configuration #%s" % str(idx + 1)
        report.append(title)
        report.append("-" * len(title))
        reporter.write_config(report, config)
    if "warnings" in parsed:
        warnings = parsed["warnings"]
        report.append("")
        report.append("parser warnings")
        report.append("---------------")
        if warnings:
            for warning in warnings:
                report.append("* %s" % warning)
        else:
            report.append("no warnings")
    report.append("")
    return "\n".join(report)

def warn_missing(node_configs, file_list, warnings, text):
    """log to warnings file"""
    if not file_list:
        warnings.append("%s: all nodes" % text)
        return
    nodes = node_configs.keys()
    nodes_files = [util.extract_node_name(f) for f in file_list]
    nodes_missing = [n for n in nodes if n not in nodes_files]
    if nodes_missing:
        warnings.append("%s: %s" % (text, ", ".join(nodes_missing)))

def _group_uniq(node_configs):
    #group the configurations together
    unique_configs = config_diff.group_configurations(node_configs)
    for config in unique_configs:
        config["nodes_list"] = sorted(config["nodes_list"], reverse=True)
    return unique_configs

def parse_diag(args, transform=_group_uniq):
    """
    parses the following files to generate a report object:
    - all system.log (GC pause times)
    - all output.log (configuration at runtime from last reboot)
    - all cfsats files (table stats)
    -- node_info.json (drive configuration)
    -- all blockdev_report (read ahead)
    """
    #find output logs
    node_configs = node_env.initialize_node_configs(args.diag_dir)
    output_logs = diag.find_logs(args.diag_dir, args.output_log_prefix)
    #find system.logs
    system_logs = diag.find_logs(args.diag_dir, args.system_log_prefix)
    warnings = node_env.find_config_in_logs(node_configs, output_logs, system_logs)
    warn_missing(node_configs, output_logs, warnings, "missing output logs")
    warn_missing(node_configs, system_logs, warnings, "missing system logs")
    #find block dev
    node_info_list = diag.find_logs(args.diag_dir, args.node_info_prefix)
    if node_info_list:
        #only set block_dev_results if we find a single node_info.json
        with diag.FileWithProgress(node_info_list[0]) as node_info_json:
            #read all the block dev reports
            if node_info_json.error:
                warnings.append("unable to read node_info.json with error: '%s'" % node_info_json.error)
            block_dev_reports = diag.find_logs(args.diag_dir, args.block_dev_prefix)
            warn_missing(node_configs, block_dev_reports, warnings, "missing blockdev_reports")
            cass_drive_ra = read_ahead.get_cass_drive_read_ahead(node_info_json, block_dev_reports)
            read_ahead.add_block_dev_to_config(cass_drive_ra, node_configs)
    else:
        warnings.append("unable to read '%s'" % args.node_info_prefix)
    transformed_configs = transform(node_configs)
    for warn in node_env.add_gc_to_configs(transformed_configs, system_logs):
        warnings.append(warn)
    #add cfstats if present
    cfstats_files = diag.find_logs(args.diag_dir, args.cfstats_prefix)
    warn_missing(node_configs, cfstats_files, warnings, "missing cfstats")
    for warn in table_stats.add_stats_to_config(transformed_configs, cfstats_files):
        warnings.append(warn)
    return {
        "diag_dir": args.diag_dir,
        "warnings": warnings,
        "original_configs": node_configs,
        "configs": transformed_configs,
        "system_logs": system_logs,
        }
