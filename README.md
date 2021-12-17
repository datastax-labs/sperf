# sperf diagnostic tooling

[User documentation](https://datastax-labs.github.io/sperf/)

![Python application](https://github.com/datastax-labs/sperf/workflows/Python%20application/badge.svg)

`sperf` is a command line tool that can analyze clusters and hardware performance to help diagnose performance problems with [DataStax Enterprise](https://www.datastax.com/products/datastax-enterprise) and [Apache Cassandra™](http://cassandra.apache.org/). Originally an internal only project is has been opened sourced under the [Apache 2.0 license](https://www.apache.org/licenses/LICENSE-2.0.html) and a new public repository was created.

# Development

Find the docs on [How to Contribute here](https://datastax-labs.github.io/sperf/contrib.html)

# Contributors to closed source sperf

* Brandon Williams (driftx) - rewrite from Go to Python, primary author of gc, statuslogger, sysbottle, jarcheck, bgrep, ttop, and slowquery
* Ryan Svihla (foundev) - original project author, Apache Solr™ tooling, diag and default command
* Nate Sanders (Nate75Sanders) - 1 commit but it was a good bug fix

# License

&copy; DataStax, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

----

DataStax is a registered trademark of DataStax, Inc. and its subsidiaries in the United States 
and/or other countries.

Apache Cassandra, Apache, Tomcat, Lucene, Solr, Hadoop, Spark, TinkerPop, and Cassandra are 
trademarks of the [Apache Software Foundation](http://www.apache.org/) or its subsidiaries in
Canada, the United States and/or other countries. 
