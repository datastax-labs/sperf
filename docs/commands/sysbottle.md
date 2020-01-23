# sperf sysbottle

```
usage: sperf sysbottle [-h] [-c [CPU]] [-q [DISKQ]] [-d [DISKS]] [-i [IOWAIT]]
                       [-t [THROUGHPUT]]
                       file

positional arguments:
  file                  iostat file to generate report on

optional arguments:
  -h, --help            show this help message and exit
  -c [CPU], --cpu [CPU]
                        percentage cpu usage minus iowait% above this threshold is busy. Assumes hyperthreading is enabled (default 50)
  -q [DISKQ], --diskQ [DISKQ]
                        disk queue depth. above this threshold is considered busy. (default 1)
  -d [DISKS], --disks [DISKS]
                        comma separated list of disks to include in report, if no disks are provided then all found disks are included in report
  -i [IOWAIT], --iowait [IOWAIT]
                        percentage iowait above this threshold is marked as a busy disk (default 5)
  -t [THROUGHPUT], --throughput [THROUGHPUT]
                        percentage of total time where we consider a node 'busy' for bottleneck summary. Example by default (5.0%) if the CPU
                        and Disk are busy 5.0% of the total time measured then it is considered busy. (default 5)
```
