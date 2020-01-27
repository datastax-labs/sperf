# sperf diagnostic tooling

sperf is a command line tool that can analyze diag tarballs, log files and iostat output to diagnose performance problems with DSE.

* sperf  - Default command that generates a simple tarball summary and recommendations for next step.
* sperf [core bgrep](docs/commands/core/bgrep.md) - search for custom regex and bucketize results
* sperf [core diag](docs/commands/core/diag.md) - Generates a diagtarball report. DSE 5.0-6.7 and Cassandra 2.1-3.11.x
* sperf [core gc](docs/commands/core/gc.md) - Show gc info DSE 5.0-6.7 and Cassandra 2.1-3.11.x
* sperf [core jarcheck](docs/commands/core/jarcheck.md) - Checks jar versions in output.logs. Supports tarballs and files. DSE 5.0-6.7
* sperf [core schema](docs/commands/core/schema.md) - Analyze schema for summary. DSE 5.0-6.7
* sperf [core slowquery](docs/commands/core/slowquery.md) - Generates a report of slow queries in debug log. DSE 6.0-6.7
* sperf [core statuslogger](docs/commands/core/statuslogger.md) - Provides analysis of StatusLogger log lines. DSE 5.0-6.7 Cassandra 2.1-3.11.x
* sperf [search filtercache](docs/commands/search/filtercache.md) - Generates a report of filter cache evictions. DSE Search 5.1-6.7
* sperf [search queryscore](docs/commands/search/queryscore.md) - Tries to summarize queries in the debug log based on score that attempts to estimate the relative potential cost of queries. DSE Search 5.1-6.7
* sperf [sysbottle](docs/commands/sysbottle.md) - sysbottle provides analysis of an iostat file. Supports iostat files generated via `iostat -x -c -d -t`
* sperf [ttop](docs/commands/ttop.md) - Analyze ttop files

## Getting started

1. Download binary install for your platform in the [releases](https://github.com/riptano/sperf/releases) section. Because we use [Pyinstaller](https://www.pyinstaller.org) no Python environment is required (or utilized).
2. Navigate to tarball directory (should see a [`nodes`](https://docs.datastax.com/en/opscenter/6.7/opsc/online_help/diagnosticTarball.html#tarballNodesFiles) folder) and run `sperf`. The output will give you a simple health check and provide some recommendations for next steps.

### For high CPU issues

* capture a ttop: `nodetool sjk ttop -ri 1s > my_test.ttop` ctrl+c when done (at least a minute of data during a high CPU event)
* run `sperf ttop my_test.ttop` to analyze CPU behavior

### For GC issues

* `sperf core gc` 
* `sperf core statuslogger`
* capture a ttop: `nodetool sjk ttop -ri 1s > my_test.ttop` ctrl+c when done (at least a minute of data during a high CPU event)
* `sperf ttop -a my_test.ttop`

### For Cassandra or DSE Core latency issues

* `sperf core gc`
* `sperf core statuslogger` 
* capture an iostat (`iostat -x -c -d -t 1 600`) on a node or two and run `sperf sysbottle`

### For Solr timeout issues

* `sperf search filtercache`
* turn on query logging for Solr and run `sperf search queryscore`
* `sperf bgrep "SolrException: Query response timeout"` to see how frequently and when shard router timeouts are happening.

### Note

To see each command's available flags, documentation and examples just add the -h flag to each command. For more information see the [generated docs](docs/commands/)

## FAQ

* Do I need to install Python? Nope! Just download the binary for your platform.
* Which tool do I use first? `sperf` run from a diag directory is a good starting point.
* What's the command I use for iostat and `sperf sysbottle`? `iostat -x -d -c -t 1 600`
* What about Python 3.8 support? Python 3.8 works fine with sperf, but we cannot yet generate binaries for 3.8 until this issue is closed: https://github.com/pyinstaller/pyinstaller/issues/4311

# Development

## Contributing

1. Make sure you have Python 3.7.x. If not then look at https://github.com/pyenv/pyenv
2. run `git clone git@github.com:riptano/sperf.git`
3. run `cd sperf/pysper`
4. run `python3 -m venv ./venv'
5. run `source ./venv/bin/activate'
6. run `pip install -r requirements.txt` to install dependencies
7. run `./scripts/sperf -h` and you should see the help for sperf
8. run `pip install pylint`

## Testing and validation

1. run `scripts/test`
2. run `scripts/lint`
