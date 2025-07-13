CHANGES = """
sperf 0.6.18
------------
* node histogram statuslogger was fixed (broken in 0.6.15) as part of cassandra version detection added

sperf 0.6.17
------------
* ttop was aggregating threads entirely incorrectly and double counting

sperf 0.6.16
------------
* tombstone warnings for 6.0.x are not parsed correctly

sperf 0.6.15
------------
* added detection for indexing backoff with auto soft commit
* added detection for tombstone scan warnings and errors
* added detection for drops and making recommendations around them
* added detection for zero copy bloom filter warnings
* added detection for tpc core imbalance
* added detection for network backpressure rejections
* added detection for tpc backpressure being enabled
* deprecated all commands except sperf command moving all functionality into the primary sperf command

sperf 0.6.14
------------
* sperf was not parsing new byte eviction format as of in sperf filtercache as
of DSE 5.1.17, 6.0.10, 6.7.5 and 6.8.0
* new makefile for build dependencies
* updated changelog to be accurate
* sperf version outputs changelog and version
* removed support and testing for Python 3.6
* sperf script will now bomb if python 3.7 or greater is not installed

sperf 0.6.13
------------
* slow query parsing was not actually parsing query timeouts
* slow query parser was never parsing past the first query.
* recommendations were getting blocked in the default sperf tool and we never got backpressure information

sperf 0.6.12
------------
* statuslogger now behaves better with unparseable logs

sperf 0.6.11
------------
* reported version was wrong

sperf 0.6.10
------------
* fixed ttop negative allocation rate

sperf 0.6.9
------------
* added ability to do bgrep per node
* removed stale node_name util
* filter cache time series
* get full directory instead of .
* ttop handles more files now

sperf 0.6.8
-----------
* sperf now links to public support topics for mmap recommendation

sperf 0.6.7
-----------
* ttop can not handle gb rate allocations

sperf 0.6.6
-----------
* Add timeformat help messages
* Allow for more permissive date parsing

sperf 0.6.5
-----------
* formatting improvement for ttop report
* file not found was being swallowed in schema command when file was being
passed directly
* custom encoding support with -fe flag to read files of any encoding in the
list for your respective python version (example for 3.7 is here
https://docs.python.org/3.7/library/codecs.html#standard-encodings)
* removed tox and pylint from ci and dev setup
* using black and flake8 in ci and dev setup
* fixed several file leaks in ttop, bgrep, jarcheck
* lots of formatting changes

sperf 0.6.4
-----------
* binary files are now longer matched when reading diags, this should allow all those pesky zips to be skipped
* `sperf core statuslogger` now reads debug.logs as well as system.logs by
default. Added additional testing to validate there is no double counting.
* DSE 6.8 `sperf core statuslogger` support
* DSE 6.8 additional testing for `sperf core diag`, `sperf core schema`,
`sperf core slowquery` and the default `sperf` command
* `sperf core statuslogger` now defaults to showing all stages to give a more
full explanation of what is going on by default. Most people didn't know the 'all stages' flag existed
and this is largely to force people to narrow their search intentionally. The initial experience maybe overwhelming, but this will make it more likely people will catch outliers
and therefore problems in clusters.

sperf 0.6.3
-----------
hotfix for v0.6.2 with the following changes

* added in missing -e flag to enable eu format
* fixed default sperf commands handling of exceptions
* file progress by default, this should help with default experience
* bunch of lint fixes that were hidden before by a missing package file

sperf 0.6.2
-----------
* removed all 3rd party dependencies except for development time (pytest, pyinstaller, tox, etc) this results in a much smaller
production binary and is much faster to launch. It is now nearly as small as the go binary for more platforms.
* date parsing is now less magic and one must choose the dates format to parse now. If parsing EU format (month and day are reversed of US)
then pass the '' flag to the command line. This allows more accurate log parsing as it is now impossible to guess the wrong format for some logs
and the correct format for others, making a fake timeline of the logs. This also speeds up runtime performance substantially.
* date parsing is now much faster because we removed the use of datetime.strptime which was the adding a nearly 80% increase in runtime in some cases.
* Improvements to release process to work with more versions of linux and Windows. Mac is still unfortunately compiled on Catalina so OS X 10.12 and older
will not work. However with the improvements to the binary releases it is easier to run sperf from source.
* Not using tar to create zips anymore but 7zip as it is more compatible with more zip utilities.

sperf 0.6.1
-----------
* new releases for windows, linux and Mac
* now more gracefully handle empty data
* python 3.5 to 3.8 support
* schema report now tells you which schema file it read to get it's information as well as failing to read the file if none is present.

sperf 0.6.0
-----------
* initial open source release
"""
