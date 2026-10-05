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

"""pysper droppedmessages module"""

import re
from collections import defaultdict
from datetime import timedelta

from pysper import env
from pysper import parser
from pysper.diag import find_logs, FileWithProgress
from pysper.util import extract_node_name
from pysper.dates import date_parse


DROPPED_MESSAGE_RE = re.compile(
    r"(?P<message_type>[A-Z][A-Z0-9_]*) messages were dropped"
    r".*?(?P<internal>\d+) internal and "
    r"(?P<cross_node>\d+) cross[\s-]*node",
    re.IGNORECASE,
)


NOISE_PATTERNS = [
    re.compile(r"\bConfig\.java:", re.I),
    re.compile(r"\bNode configuration\s*:", re.I),
    re.compile(r"\bDatabaseDescriptor\.java:", re.I),
    re.compile(r"\bStartupChecks\.java:", re.I),
]


EVIDENCE_PATTERNS = {
    "GC pressure": [
        re.compile(r"GCInspector.*(?:took|pause|stopped|blocked)", re.I),
        re.compile(r"Garbage collection.*(?:took|pause|stopped)", re.I),
        re.compile(r"\bFull GC\b", re.I),
    ],
    "Mutation/write backlog": [
        re.compile(
            r"MutationStage.*(?:pending|blocked|backlog|queue)",
            re.I,
        ),
        re.compile(
            r"MutationExecutor.*(?:pending|blocked|backlog|queue)",
            re.I,
        ),
    ],
    "Read-path pressure": [
        re.compile(
            r"ReadStage.*(?:pending|blocked|backlog|queue)",
            re.I,
        ),
        re.compile(
            r"(?:read|range).*timed out",
            re.I,
        ),
    ],
    "Commitlog pressure": [
        re.compile(
            r"commit.?log.*"
            r"(?:blocked|blocking|timeout|timed out|failed|failure)",
            re.I,
        ),
        re.compile(
            r"commit.?log.*(?:sync|flush).*"
            r"(?:slow|latency|took|waiting)",
            re.I,
        ),
    ],
    "Memtable/flush pressure": [
        re.compile(
            r"memtable.*(?:blocked|pressure|unable|waiting).*flush",
            re.I,
        ),
        re.compile(
            r"flush.*(?:blocked|backlog|unable|waiting)",
            re.I,
        ),
    ],
    "Compaction pressure": [
        re.compile(
            r"compaction.*(?:backlog|pressure|blocked|unable|failed)",
            re.I,
        ),
    ],
    "Internode network/messaging": [
        re.compile(
            r"(?:internode|messaging|OutboundTcpConnection).*"
            r"(?:timeout|timed out|failed|error|closed|reset)",
            re.I,
        ),
        re.compile(
            r"(?:connection|channel).*"
            r"(?:reset by peer|refused|timed out|broken pipe)",
            re.I,
        ),
        re.compile(
            r"failed to send.*(?:message|mutation)",
            re.I,
        ),
    ],
    "Oversized mutation": [
        re.compile(r"\bOversized mutation\b", re.I),
        re.compile(
            r"\bMutation of .*? bytes is too large\b",
            re.I,
        ),
    ],
    "Request timeout/overload": [
        re.compile(r"\bWriteTimeoutException\b", re.I),
        re.compile(r"\bReadTimeoutException\b", re.I),
        re.compile(r"\bRequestTimeoutException\b", re.I),
        re.compile(r"\bOverloadedException\b", re.I),
    ],
}


WRITE_TYPES = {
    "MUTATION",
    "COUNTER_MUTATION",
}


READ_TYPES = {
    "READ",
    "RANGE_SLICE",
}


class DroppedMessages:
    """Analyze Cassandra/DSE dropped messages."""

    def __init__(
        self,
        diag_dir,
        files=None,
        message_type=None,
        command_name="sperf core droppedmessages",
        start=None,
        end=None,
        window_minutes=20,
        syslog_prefix="system.log",
    ):
        self.diag_dir = diag_dir
        self.files = files

        self.message_type = (
            message_type.upper()
            if message_type
            else None
        )

        self.command_name = command_name
        self.window_minutes = window_minutes
        self.syslog_prefix = syslog_prefix

        self.start = None
        self.end = None

        if start:
            self.start = date_parse(start)

        if end:
            self.end = date_parse(end)

        self.events = []
        self.drops = []
        self.analyzed = False

    def _is_noise(self, line):
        """Return True for configuration/startup noise."""

        return any(
            pattern.search(line)
            for pattern in NOISE_PATTERNS
        )

    def _parse_drop(self, line):
        """Parse a dropped-message log line."""

        match = DROPPED_MESSAGE_RE.search(line)

        if not match:
            return None

        message_type = match.group(
            "message_type"
        ).upper()

        if (
            self.message_type
            and message_type != self.message_type
        ):
            return None

        internal = int(
            match.group("internal")
        )

        cross_node = int(
            match.group("cross_node")
        )

        return {
            "message_type": message_type,
            "internal": internal,
            "cross_node": cross_node,
            "total": internal + cross_node,
        }

    def _wanted_evidence(self, message_type):
        """Return evidence categories relevant to message type."""

        common = {
            "GC pressure",
            "Internode network/messaging",
            "Request timeout/overload",
        }

        if message_type in WRITE_TYPES:
            return common | {
                "Mutation/write backlog",
                "Commitlog pressure",
                "Memtable/flush pressure",
                "Oversized mutation",
            }

        if message_type in READ_TYPES:
            return common | {
                "Read-path pressure",
                "Compaction pressure",
            }

        return common

    def _find_evidence(self, incident):
        """Find possible symptoms around an incident."""

        window = timedelta(
            minutes=self.window_minutes
        )

        start = incident["start"] - window
        end = incident["end"] + window

        wanted = self._wanted_evidence(
            incident["message_type"]
        )

        evidence = defaultdict(list)

        for event in self.events:

            # Evidence must come from the affected node.
            if event["node"] != incident["node"]:
                continue

            if event["date"] < start:
                continue

            if event["date"] > end:
                continue

            line = event["line"]

            if self._is_noise(line):
                continue

            for name, patterns in EVIDENCE_PATTERNS.items():

                if name not in wanted:
                    continue

                if any(
                    pattern.search(line)
                    for pattern in patterns
                ):
                    evidence[name].append(event)

        return evidence

    @staticmethod
    def _event_line(event):
        """
        Convert a sperf parsed event into searchable text.

        parser.read_system_log() separates the source file and message
        into different dictionary fields. Reconstruct enough of the
        original log content for evidence matching.
        """

        source_file = event.get("source_file")
        source_line = event.get("source_line")
        message = event.get("message")

        if source_file and message:
            if source_line is not None:
                return "%s:%s - %s" % (
                    source_file,
                    source_line,
                    message,
                )

            return "%s - %s" % (
                source_file,
                message,
            )

        if message:
            return str(message)

        for key in (
            "line",
            "msg",
            "text",
            "raw",
        ):
            value = event.get(key)

            if value:
                return str(value)

        return str(event)

    def analyze(self):
        """Analyze system.log files."""

        if self.analyzed:
            return

        if self.files:
            target = self.files

        elif self.diag_dir:
            target = find_logs(
                self.diag_dir,
                file_to_find=self.syslog_prefix,
            )

        else:
            raise Exception(
                "no diag dir and no files specified"
            )

        for filename in target:

            nodename = extract_node_name(
                filename,
                ignore_missing_nodes=True,
            )

            if env.DEBUG:
                print("parsing", filename)

            with FileWithProgress(filename) as log:

                for event in parser.read_system_log(log):

                    event_date = event.get("date")

                    if not event_date:
                        continue

                    #
                    # IMPORTANT:
                    #
                    # We keep events outside --start/--end only when
                    # needed for the +/- evidence window.
                    #
                    # This allows:
                    #
                    #   -st 08:00 -et 09:00 -w 20
                    #
                    # to correlate evidence from 07:40 through 09:20,
                    # while dropped-message incidents themselves remain
                    # restricted to 08:00 through 09:00.
                    #

                    evidence_start = None
                    evidence_end = None

                    if self.start:
                        evidence_start = (
                            self.start
                            - timedelta(
                                minutes=self.window_minutes
                            )
                        )

                    if self.end:
                        evidence_end = (
                            self.end
                            + timedelta(
                                minutes=self.window_minutes
                            )
                        )

                    if (
                        evidence_start
                        and event_date < evidence_start
                    ):
                        continue

                    if (
                        evidence_end
                        and event_date > evidence_end
                    ):
                        continue

                    line = self._event_line(event)

                    parsed_event = {
                        "date": event_date,
                        "node": nodename,
                        "line": line,
                        "file": filename,
                    }

                    self.events.append(
                        parsed_event
                    )

                    #
                    # Drop incidents themselves must obey the exact
                    # --start / --end requested by the user.
                    #

                    if (
                        self.start
                        and event_date < self.start
                    ):
                        continue

                    if (
                        self.end
                        and event_date > self.end
                    ):
                        continue

                    drop = self._parse_drop(line)

                    if not drop:
                        continue

                    drop.update(
                        {
                            "date": event_date,
                            "node": nodename,
                            "line": line,
                            "file": filename,
                        }
                    )

                    self.drops.append(drop)

        self.analyzed = True

    @staticmethod
    def _build_incident(
        node,
        message_type,
        drops,
    ):
        """Build one incident."""

        return {
            "node": node,
            "message_type": message_type,
            "start": drops[0]["date"],
            "end": drops[-1]["date"],
            "drop_events": len(drops),
            "internal": sum(
                drop["internal"]
                for drop in drops
            ),
            "cross_node": sum(
                drop["cross_node"]
                for drop in drops
            ),
            "total": sum(
                drop["total"]
                for drop in drops
            ),
            "drops": drops,
        }

    def _group_incidents(self):
        """Group drops by node, type and time."""

        grouped = defaultdict(list)

        for drop in self.drops:

            key = (
                drop["node"],
                drop["message_type"],
            )

            grouped[key].append(drop)

        incidents = []

        incident_gap = timedelta(
            minutes=5
        )

        for (
            node,
            message_type,
        ), drops in grouped.items():

            drops.sort(
                key=lambda item: item["date"]
            )

            current = []

            for drop in drops:

                if not current:
                    current = [drop]
                    continue

                gap = (
                    drop["date"]
                    - current[-1]["date"]
                )

                if gap <= incident_gap:
                    current.append(drop)

                else:
                    incidents.append(
                        self._build_incident(
                            node,
                            message_type,
                            current,
                        )
                    )

                    current = [drop]

            if current:
                incidents.append(
                    self._build_incident(
                        node,
                        message_type,
                        current,
                    )
                )

        return incidents

    def print_summary(self):
        """Print dropped-message analysis."""

        self.analyze()

        incidents = self._group_incidents()

        print("=" * 72)
        print(
            "CASSANDRA/DSE DROPPED MESSAGE ANALYSIS"
        )
        print("=" * 72)

        print(
            "Message type       : %s"
            % (
                self.message_type
                if self.message_type
                else "ALL"
            )
        )

        print(
            "Evidence window    : +/- %d minutes"
            % self.window_minutes
        )

        total_dropped = sum(
            incident["total"]
            for incident in incidents
        )

        print(
            "Dropped messages   : %d"
            % total_dropped
        )

        print(
            "Incidents found    : %d"
            % len(incidents)
        )

        if not incidents:

            print()

            print(
                "No dropped messages were found "
                "for the requested criteria."
            )

            return

        #
        # Top means highest dropped-message count.
        # It does NOT mean first five chronologically.
        #

        incidents.sort(
            key=lambda incident: incident["total"],
            reverse=True,
        )

        displayed = incidents[:5]

        if len(incidents) > 5:

            print(
                "Incidents shown    : Top 5 by "
                "dropped-message count"
            )

        else:

            print(
                "Incidents shown    : %d"
                % len(displayed)
            )

        print()

        for number, incident in enumerate(
            displayed,
            start=1,
        ):

            print("-" * 72)

            print(
                "INCIDENT %d"
                % number
            )

            print("-" * 72)

            print(
                "Message type       : %s"
                % incident["message_type"]
            )

            print(
                "Affected node      : %s"
                % incident["node"]
            )

            print(
                "Dropped messages   : %d"
                % incident["total"]
            )

            print(
                "  Internal         : %d"
                % incident["internal"]
            )

            print(
                "  Cross-node       : %d"
                % incident["cross_node"]
            )

            print(
                "Drop log events    : %d"
                % incident["drop_events"]
            )

            print(
                "Drop period        : %s -> %s"
                % (
                    incident["start"],
                    incident["end"],
                )
            )

            evidence = self._find_evidence(
                incident
            )

            print()

            print(
                "Possible evidence / suspects:"
            )

            if not evidence:

                print(
                    "  No relevant runtime symptom "
                    "was found in the provided "
                    "analysis window."
                )

            else:

                for name, events in evidence.items():

                    print(
                        "  %s: %d event(s)"
                        % (
                            name,
                            len(events),
                        )
                    )

                    #
                    # Keep output concise.
                    #

                    for event in events[:3]:

                        print(
                            "    %s %s"
                            % (
                                event["date"],
                                event["line"],
                            )
                        )

            print()