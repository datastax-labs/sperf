# Sperf the magical diagnostic tool for DataStax Enterprise and Apache Cassandra™

## Install

[Binaries here](https://github.com/DataStax-Toolkit/sperf/releases) or if you use [Hombrew](https://brew.sh) `brew tap rsds143/rsds && brew install sperf`

## What can it do

Lots of things, you can run it as a high level tool to find the basic problems and get some easy recommendations or you can use it in a targeted fashion to find specific problems.

* [General Recommendations](#general-recommendations)
* [High CPU Usage](#high-cpu-usage)
* [Configuration Differences Between Nodes](#configuration-differences-between-nodes)
* [Diagnose High GC](#diagnose-high-gc)
* [Identify those pesky SOLR queries that cause problems in DSE Search](#identify-those-pesky-solr-queries-that-cause-problems)

[All the tools and their functions are listed below](#all-the-tools)

### General Recommendations

* [download diagnostic tarball from cluster](https://github.com/DataStax-Toolkit/diagnostic-collection) and extract it
* navigate into tarball folder `cd my_extracted_tarball`
* run `sperf` exmaple output:

```sh
sperf version 0.6.4

................................
nodes                               3                                                    
dse version(s) (startup logs)       { 6.7.7 }                                            
cassandra version(s) (startup logs) { DSE private fork }                                 
solr version(s) (startup logs)      { 6.0.1.2.2647 }                                     
spark version(s) (startup logs)     { 2.2.3.9 }                                          
worst gc pause (system logs)        800.00 ms (10.101.35.71)                             
worst read latency (cfstats)        6.11 ms (system_schema.keyspaces 10.101.35.102)      
worst write latency (cfstats)       4.72 ms (system_schema.dropped_columns 10.101.35.102)
worst tombstones query (cfstats)    319 (system_distributed.nodesync_status 10.101.35.71)
worst live cells query (cfstats)    447 (system_schema.columns 10.101.35.71)             
largest table (cfstats)             my_solr.my_table (133.46 mb 10.101.35.102)           
busiest table reads (cfstats)       my_solr.my_table (99.78% of reads)                   
busiest table writes (cfstats)      my_solr.my_table (95.80% of writes)                  
largest partition (cfstats)         28.83 kb system.size_estimates (10.101.35.71)        

errors parsing
--------------
No parsing errors

recommendations
---------------
* There were 16 incidents of GC over 500ms. Run `sperf core gc` for more analysis.
```

[back to table of contents](#What-can-it-do)

### For Apache Cassandra™ or DSE Core latency issues

* [download diagnostic tarball from cluster](https://github.com/DataStax-Toolkit/diagnostic-collection) and extract it
* navigate into tarball folder `cd my_extracted_tarball`
* `sperf core gc` example output:

```sh
gcinspector version 0.6.4

. <300ms + 301-500ms ! >500ms
------------------------------
2020-01-10 16:28:37 236 ...............+++........++.....+.+...+++.++.+.+......+.....+.!!+!.!++!+..++.+.!..+.!++++.!.++++.+.+++..+!!.......!..+.+....+.....++.+...+.+.++.+.+!!++.+.+.!++.+.+...+.+..+.+.+.+..+++....++..+++....+..++.+++.+!+..+.+.+.+!......+++....+

busiest period: 2020-01-10 16:28:37 (75041ms)


GC pauses  max        p99        p75        p50        p25        min        
           ---        ---        ---        ---        ---        ---        
ms         800        729        358        282        243        201        

Worst pauses in ms:
[800, 735, 729]

Collections by type
--------------------
* G1 Young: 236
```

* `sperf core statuslogger` example output:

```sh
............sperf core statuslogger version: 0.6.4

Summary (22,054 lines)
Summary (444 skipped lines)

dse versions: {'6.7.7'}
cassandra versions: {'DSE Private Fork'}
first log time: 2020-01-10 15:27:58.554000+00:00
last log time: 2020-01-10 17:21:13.549000+00:00
duration: 1.89 hours
total stages analyzed: 2
total nodes analyzed: 3

GC pauses  max        p99        p75        p50        p25        min        
           ---        ---        ---        ---        ---        ---        
ms         800        729        358        282        243        201        
total GC events: 236

busiest tables by ops across all nodes
------------------------------
* 10.101.35.102: OpsCenter.rollups60: 66,464 ops / 3.38 mb data

busiest table by data across all nodes
------------------------------
* 10.101.35.102: my_solr.my_table: 37,132 ops / 9.37 mb data

busiest stages across all nodes
------------------------------
* CompactionExecutor active:   1  (10.101.35.102)  
* TPC/0/WRITE_REMOTE active:   1  (10.101.35.102)  
* CompactionExecutor pending:  1  (10.101.35.102)  

busiest stages in PENDING
------------------------------
10.101.35.102:
       CompactionExecutor:  1
```

* capture an iostat (`iostat -x -c -d -t 1 600`) on a node or two and run `sperf sysbottle`

```sh
sysbottle version 0.6.4


* total records: 10
* total bottleneck time: 60.00% (cpu bound, io bound, or both)
* cpu+system+nice+steal time > 50.00%: 30.00%
* iowait time > 5.00%: 30.00%
* start 2019-06-06 11:44:01
* end 2019-06-06 11:44:10
* log time: 10.0s
* interval: 100.0s
* nvme0n1 time at queue depth >= 1.00: 20.00%

            max      p99      p75     p50     p25     min     
            ---      ---      ---     ---     ---     ---     
cpu         92.64    92.64    91.63   6.34    2.50    1.63    
iowait      90.13    90.13    90.00   0.13    0.13    0.12    

            max      p99      p75     p50     p25     min     
            ---      ---      ---     ---     ---     ---     
nvme0n1                                                       
- r_await:  0.70     0.70     0.00    0.00    0.00    0.00    
- w_await:  1200.00  1200.00  9.00    8.00    8.00    0.84    
- aqu-sz:   90.00    90.00    0.24    0.01    0.01    0.01    

recommendations
---------------
* tune for less CPU usage
* decrease activity on nvme0n1
* tune for less IO
```

[back to table of contents](#what-can-it-do)

### High CPU Usage

* capture a ttop: `nodetool sjk ttop -ri 1s > my_test.ttop` ctrl+c when done (at least a minute of data during a high CPU event)
* run `sperf ttop my_test.ttop` to analyze CPU behavior

```sh
ttop version 0.6.4

2020-01-09 16:08:06                      Threads    CPU%       Total: 28.06%
================================================================================
ParkedThreadsMonitor                     4          23.52      -----------------
RMI TCP Connection(2)                    4          2.9        --        
CoreThread                               20         1.2        -         
DseGossipStateUpdater                    4          0.1                  
ScheduledTasks                           4          0.08                 
NodeHealthPlugin-Scheduler-thread        4          0.06                 
OptionalTasks                            4          0.05                 
JMX server connection timeout 425        4          0.04                 
ContainerBackgroundProcessor[StandardEngine[Solr]] 4          0.02                 
PO-thread                                4          0.02                 
GossipTasks                              4          0.01                 
AsyncAppender-Worker-ASYNCDEBUGLOG       4          0.01                 
LeasePlugin                              4          0.01                 
NonPeriodicTasks                         4          0.01                 
RxSchedulerPurge                         4          0.01                 
internode-messaging RemoteMessageServer acceptor 4          0.0                  

2020-01-09 16:08:16                      Threads    CPU%       Total: 25.84%
================================================================================
ParkedThreadsMonitor                     4          22.73      ------------------
RMI TCP Connection(2)                    4          1.97       --        
CoreThread                               28         0.91       -         
ScheduledTasks                           4          0.08                 
OptionalTasks                            4          0.03                 
JMX server connection timeout 425        4          0.03                 
GossipTasks                              4          0.01                 
ContainerBackgroundProcessor[StandardEngine[Solr]] 4          0.01                 
LeasePlugin                              4          0.01                 
BatchlogTasks                            4          0.01                 
RxSchedulerPurge                         4          0.01                 
AsyncFileHandlerWriter                   4          0.0                  
internode-messaging RemoteMessageServer acceptor 4          0.0                  
PERIODIC-COMMIT-LOG-SYNCER               4          0.0                  

2020-01-09 16:08:26                      Threads    CPU%       Total: 27.13%
================================================================================
ParkedThreadsMonitor                     4          24.33      ------------------
RMI TCP Connection(2)                    4          1.7        -         
CoreThread                               28         0.89       -         
ScheduledTasks                           4          0.07                 
OptionalTasks                            4          0.03                 
JMX server connection timeout 425        4          0.02                 
GossipTasks                              4          0.01                 
LeasePlugin                              4          0.01                 
ContainerBackgroundProcessor[StandardEngine[Solr]] 4          0.01                 
BatchlogTasks                            4          0.01                 
RxSchedulerPurge                         4          0.0                  
internode-messaging RemoteMessageServer acceptor 4          0.0                  
AsyncFileHandlerWriter                   4          0.0                  
http-bio                                 4          0.0                  

2020-01-09 16:08:36                      Threads    CPU%       Total: 27.3%
================================================================================
ParkedThreadsMonitor                     4          23.89      ------------------
RMI TCP Connection(2)                    4          2.0        -         
CoreThread                               28         1.2        -         
ScheduledTasks                           4          0.09                 
OptionalTasks                            4          0.04                 
JMX server connection timeout 425        4          0.03                 
GossipTasks                              4          0.01                 
LeasePlugin                              4          0.01                 
ContainerBackgroundProcessor[StandardEngine[Solr]] 4          0.01                 
BatchlogTasks                            4          0.01                 
PO-thread                                4          0.01                 
RMI TCP Connection(idle)                 4          0.01                 
RxSchedulerPurge                         4          0.0                  
AsyncFileHandlerWriter                   4          0.0                  

2020-01-09 16:08:46                      Threads    CPU%       Total: 25.38%
================================================================================
ParkedThreadsMonitor                     4          22.74      ------------------
RMI TCP Connection(2)                    4          1.53       -         
CoreThread                               28         0.91       -         
ScheduledTasks                           4          0.08                 
OptionalTasks                            4          0.03                 
JMX server connection timeout 425        4          0.02                 
ContainerBackgroundProcessor[StandardEngine[Solr]] 4          0.01                 
GossipTasks                              4          0.01                 
LeasePlugin                              4          0.01                 
BatchlogTasks                            4          0.01                 
RxSchedulerPurge                         4          0.01                 
AsyncFileHandlerWriter                   4          0.0                  
internode-messaging RemoteMessageServer acceptor 4          0.0                  
http-bio                                 4          0.0              
```
[back to table of contents](#what-can-it-do)

### Configuration Differences Between Nodes

* [download diagnostic tarball from cluster](https://github.com/DataStax-Toolkit/diagnostic-collection) and extract it
* navigate into tarball folder `cd my_extracted_tarball`
* run `sperf core diag` example output:

```sh
sperf core diag version: 0.6.4

....................
configuration #1
----------------
nodes count                   2
cass drive(s) read ahead      N/A
dse version                   6.7.7
cassandra version             N/A
solr version                  6.0.1.2.2647
spark version                 2.2.3.9
spark connector version       N/A
disk access mode              standard
disk optimization             ssd
memtable cleanup threshold    default
flush writers                 default
compaction throughput         16 mb
concurrent compactors         default
memtable size (heap)          default
memtable size (offheap)       default
memtable allocation type      offheap_objects
file cache size               default
heap size                     3759M
gc                            G1GC
total ram                     15 gb
total cpu cores (real)        8
threads per core              1
worst gc pause                800.00 ms (10.101.35.71)
worst write latency (all)     4.22 ms (system_schema.dropped_columns 10.101.35.71)
worst read latency (all)      2.88 ms (system.local 10.101.35.71)
worst tombstones query (all)  319 (system_distributed.nodesync_status 10.101.35.71)
worst live cells query (all)  447 (system_schema.columns 10.101.35.71)
largest table                 my_solr.my_table (133.32 mb 10.101.35.71)
busiest table reads           my_solr.my_table (99.76% of reads)
busiest table writes          my_solr.my_table (96.18% of writes)
worst partition in            system.size_estimates (10.101.35.71)
* max partition size          28.83 kb
* mean partition size         8.10 kb
* min partition size          2.25 kb

nodes
-----
10.101.35.71, 10.101.33.205


config diff from common:
* listen_interface: eth0

configuration #2
----------------
nodes count                   1
cass drive(s) read ahead      N/A
dse version                   6.7.7
cassandra version             N/A
solr version                  6.0.1.2.2647
spark version                 2.2.3.9
spark connector version       N/A
disk access mode              standard
disk optimization             ssd
memtable cleanup threshold    default
flush writers                 default
compaction throughput         16 mb
concurrent compactors         default
memtable size (heap)          default
memtable size (offheap)       default
memtable allocation type      offheap_objects
file cache size               default
heap size                     3759M
gc                            G1GC
total ram                     15 gb
total cpu cores (real)        8
threads per core              1
worst gc pause                258.00 ms (10.101.35.102)
worst write latency (all)     4.72 ms (system_schema.dropped_columns 10.101.35.102)
worst read latency (all)      6.11 ms (system_schema.keyspaces 10.101.35.102)
worst tombstones query (all)  7 (OpsCenter.events 10.101.35.102)
worst live cells query (all)  447 (system_schema.columns 10.101.35.102)
largest table                 my_solr.my_table (133.46 mb 10.101.35.102)
busiest table reads           my_solr.my_table (99.81% of reads)
busiest table writes          my_solr.my_table (95.04% of writes)
worst partition in            system_schema.columns (10.101.35.102)
* max partition size          9.66 kb
* mean partition size         2.16 kb
* min partition size          180 bytes

nodes
-----
10.101.35.102


config diff from common:
* listen_interface: default

parser warnings
---------------
no warnings
```

[back to table of contents](#what-can-it-do)

### Diagnose High GC

* [download diagnostic tarball from cluster](https://github.com/DataStax-Toolkit/diagnostic-collection) and extract it
* navigate into tarball folder `cd my_extracted_tarball`
* `sperf core gc` (example above)
* `sperf core statuslogger` (example above)
* capture a ttop: `nodetool sjk ttop -ri 1s > my_test.ttop` ctrl+c when done (at least a minute of data during a high CPU event)
* `sperf ttop -a my_test.ttop` example output:

```sh

ttop version 0.6.4

2020-01-09 16:08:06                      Threads    Alloc/s    Total: 3.38 mb
================================================================================
CoreThread                               20         2.14 mb    -------------
RMI TCP Connection(2)                    4          1.14 mb    -------   
DseGossipStateUpdater                    4          38.00 kb             
ScheduledTasks                           4          24.00 kb             
NodeHealthPlugin-Scheduler-thread        4          19.00 kb             
ContainerBackgroundProcessor[StandardEngine[Solr]] 4          6.01 kb              
JMX server connection timeout 425        4          4.18 kb              
PO-thread                                4          2.47 kb              
AsyncAppender-Worker-ASYNCDEBUGLOG       4          1.90 kb              
LeasePlugin                              4          1.38 kb              
NonPeriodicTasks                         4          1.07 kb              
GossipTasks                              4          841 bytes            
RxSchedulerPurge                         4          710 bytes            
OptionalTasks                            4          323 bytes            
ParkedThreadsMonitor                     4          317 bytes            
internode-messaging RemoteMessageServer acceptor 4          0 byte               

2020-01-09 16:08:16                      Threads    Alloc/s    Total: 3.23 mb
================================================================================
CoreThread                               28         2.14 mb    -------------
RMI TCP Connection(2)                    4          1.05 mb    -------   
ScheduledTasks                           4          24.00 kb             
ContainerBackgroundProcessor[StandardEngine[Solr]] 4          4.15 kb              
JMX server connection timeout 425        4          4.09 kb              
BatchlogTasks                            4          1.54 kb              
LeasePlugin                              4          1.48 kb              
GossipTasks                              4          910 bytes            
RxSchedulerPurge                         4          641 bytes            
ParkedThreadsMonitor                     4          321 bytes            
OptionalTasks                            4          319 bytes            
PERIODIC-COMMIT-LOG-SYNCER               4          135 bytes            
AsyncFileHandlerWriter                   4          32 bytes             
internode-messaging RemoteMessageServer acceptor 4          0 byte               

2020-01-09 16:08:26                      Threads    Alloc/s    Total: 3.17 mb
================================================================================
CoreThread                               28         2.08 mb    -------------
RMI TCP Connection(2)                    4          1.06 mb    -------   
ScheduledTasks                           4          24.00 kb             
JMX server connection timeout 425        4          4.12 kb              
ContainerBackgroundProcessor[StandardEngine[Solr]] 4          3.26 kb              
BatchlogTasks                            4          1.56 kb              
LeasePlugin                              4          1.50 kb              
GossipTasks                              4          918 bytes            
RxSchedulerPurge                         4          583 bytes            
ParkedThreadsMonitor                     4          318 bytes            
OptionalTasks                            4          299 bytes            
http-bio                                 4          57 bytes             
AsyncFileHandlerWriter                   4          32 bytes             
internode-messaging RemoteMessageServer acceptor 4          0 byte               

2020-01-09 16:08:36                      Threads    Alloc/s    Total: 3.22 mb
================================================================================
CoreThread                               28         2.14 mb    -------------
RMI TCP Connection(2)                    4          1.04 mb    ------    
ScheduledTasks                           4          24.00 kb             
JMX server connection timeout 425        4          4.08 kb              
ContainerBackgroundProcessor[StandardEngine[Solr]] 4          3.08 kb              
BatchlogTasks                            4          1.47 kb              
LeasePlugin                              4          1.41 kb              
PO-thread                                4          1.27 kb              
GossipTasks                              4          866 bytes            
RxSchedulerPurge                         4          672 bytes            
OptionalTasks                            4          325 bytes            
ParkedThreadsMonitor                     4          321 bytes            
RMI TCP Connection(idle)                 4          190 bytes            
AsyncFileHandlerWriter                   4          30 bytes             

2020-01-09 16:08:46                      Threads    Alloc/s    Total: 3.24 mb
================================================================================
CoreThread                               28         2.15 mb    -------------
RMI TCP Connection(2)                    4          1.05 mb    ------    
ScheduledTasks                           4          24.00 kb             
ContainerBackgroundProcessor[StandardEngine[Solr]] 4          4.18 kb              
JMX server connection timeout 425        4          4.08 kb              
BatchlogTasks                            4          1.55 kb              
LeasePlugin                              4          1.49 kb              
GossipTasks                              4          916 bytes            
RxSchedulerPurge                         4          646 bytes            
ParkedThreadsMonitor                     4          317 bytes            
OptionalTasks                            4          305 bytes            
http-bio                                 4          57 bytes             
AsyncFileHandlerWriter                   4          32 bytes             
internode-messaging RemoteMessageServer acceptor 4          0 byte   
```

[back to table of contents](#what-can-it-do)

### Identify those pesky SOLR queries that cause problems

* [download diagnostic tarball from cluster](https://github.com/DataStax-Toolkit/diagnostic-collection) and extract it
* navigate into tarball folder `cd my_extracted_tarball`
* `sperf core bgrep "SolrException: Query response timeout"` to see how frequently and when shard router timeouts are happening.
* `sperf search filtercache`
* turn on query logging for Solr and run `sperf search queryscore`

[back to table of contents](#what-can-it-do)

## All the tools

* sperf  - Default command that generates a simple tarball summary and recommendations for next step.
* sperf [core bgrep](commands#sperf-core-bgrep) - search for custom regex and bucketize results
* sperf [core diag](commands#sperf-core-diag) - Generates a diagtarball report. DSE 5.0-6.7 and Cassandra 2.1-3.11.x
* sperf [core gc](commands#sperf-core-gc) - Show gc info DSE 5.0-6.7 and Cassandra 2.1-3.11.x
* sperf [core jarcheck](commands#sperf-core-jarcheck) - Checks jar versions in output.logs. Supports tarballs and files. DSE 5.0-6.7
* sperf [core schema](commands#sperf-core-schema) - Analyze schema for summary. DSE 5.0-6.8
* sperf [core slowquery](commands#sperf-core-slowquery) - Generates a report of slow queries in debug log. DSE 6.0-6.7
* sperf [core statuslogger](commands#sperf-core-statuslogger) - Provides analysis of StatusLogger log lines. DSE 5.0-6.8 Cassandra 2.1-3.11.x
* sperf [search filtercache](commands#sperf-search-filtercache) - Generates a report of filter cache evictions. DSE Search 5.1-6.7
* sperf [search queryscore](commands#sperf-search-queryscore) - Tries to summarize queries in the debug log based on score that attempts to estimate the relative potential cost of queries. DSE Search 5.1-6.7
* sperf [sysbottle](commands#sperf-sysbottle) - sysbottle provides analysis of an iostat file. Supports iostat files generated via `iostat -x -c -d -t`
* sperf [ttop](commands#sperf-ttop) - Analyze ttop files

### Note

To see each command's available flags, documentation and examples just add the -h flag to each command. For more information see the [generated docs](commands.html)


## Developing

Check out the [contributing page](contrib.html)
