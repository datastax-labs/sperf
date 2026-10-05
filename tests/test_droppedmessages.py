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

"""Tests for dropped message analysis."""

from types import SimpleNamespace

import pytest

from pysper.commands.core import droppedmessages


@pytest.fixture
def diag_dir(tmp_path):
    """Create a minimal Cassandra diagnostic directory."""

    node_dir = tmp_path / "nodes" / "10.0.0.1" / "logs" / "cassandra"
    node_dir.mkdir(parents=True)

    system_log = node_dir / "system.log"

    system_log.write_text(
        "\n".join(
            [
                (
                    "INFO [ScheduledTasks:1] "
                    "2026-08-04 08:10:00,000 "
                    "DroppedMessages.java:157 - "
                    "MUTATION messages were dropped "
                    "in the last 5 s: "
                    "0 internal and 100 cross node"
                ),
                (
                    "INFO [ScheduledTasks:1] "
                    "2026-08-04 08:20:00,000 "
                    "DroppedMessages.java:157 - "
                    "READ messages were dropped "
                    "in the last 5 s: "
                    "10 internal and 20 cross node"
                ),
                (
                    "INFO [ScheduledTasks:1] "
                    "2026-08-04 08:30:00,000 "
                    "DroppedMessages.java:157 - "
                    "RANGE_SLICE messages were dropped "
                    "in the last 5 s: "
                    "5 internal and 15 cross node"
                ),
            ]
        )
        + "\n"
    )

    return str(tmp_path)


def make_args(diag_dir, **kwargs):
    """Build command arguments using droppedmessages defaults."""

    args = {
        "diag_dir": diag_dir,
        "files": None,
        "type": "all",
        "start": None,
        "end": None,
        "window": 20,
        "system_log_prefix": "system.log",
    }

    args.update(kwargs)

    return SimpleNamespace(**args)


def test_all_message_types(diag_dir, capsys):
    """Default behavior should report all dropped-message types."""

    droppedmessages.run(make_args(diag_dir))

    output = capsys.readouterr().out

    assert "Message type       : ALL" in output
    assert "MUTATION" in output
    assert "READ" in output
    assert "RANGE_SLICE" in output

    # 100 + 30 + 20
    assert "Dropped messages   : 150" in output
    assert "Incidents found    : 3" in output


def test_mutation_filter(diag_dir, capsys):
    """--type MUTATION should exclude other message types."""

    droppedmessages.run(
        make_args(
            diag_dir,
            type="MUTATION",
        )
    )

    output = capsys.readouterr().out

    assert "Message type       : MUTATION" in output
    assert "Dropped messages   : 100" in output

    assert "Message type       : READ" not in output
    assert "Message type       : RANGE_SLICE" not in output


def test_read_filter(diag_dir, capsys):
    """--type READ should report only READ drops."""

    droppedmessages.run(
        make_args(
            diag_dir,
            type="READ",
        )
    )

    output = capsys.readouterr().out

    assert "Message type       : READ" in output
    assert "Dropped messages   : 30" in output

    assert "Message type       : MUTATION" not in output
    assert "Message type       : RANGE_SLICE" not in output


def test_actual_drop_count(diag_dir, capsys):
    """Internal and cross-node counts should be added together."""

    droppedmessages.run(
        make_args(
            diag_dir,
            type="READ",
        )
    )

    output = capsys.readouterr().out

    # READ has:
    #   10 internal
    #   20 cross-node
    #   = 30 total

    assert "Dropped messages   : 30" in output
    assert "  Internal         : 10" in output
    assert "  Cross-node       : 20" in output


def test_start_time_filter(diag_dir, capsys):
    """Events before --start should not be included as incidents."""

    droppedmessages.run(
        make_args(
            diag_dir,
            start="2026-08-04 08:15:00,000",
        )
    )

    output = capsys.readouterr().out

    # MUTATION at 08:10 is before --start.
    assert "Message type       : MUTATION" not in output

    assert "Message type       : READ" in output
    assert "Message type       : RANGE_SLICE" in output

    # READ = 30
    # RANGE_SLICE = 20
    assert "Dropped messages   : 50" in output
    assert "Incidents found    : 2" in output


def test_end_time_filter(diag_dir, capsys):
    """Events after --end should not be included as incidents."""

    droppedmessages.run(
        make_args(
            diag_dir,
            end="2026-08-04 08:25:00,000",
        )
    )

    output = capsys.readouterr().out

    assert "Message type       : MUTATION" in output
    assert "Message type       : READ" in output

    # RANGE_SLICE at 08:30 is after --end.
    assert "Message type       : RANGE_SLICE" not in output

    # MUTATION = 100
    # READ = 30
    assert "Dropped messages   : 130" in output
    assert "Incidents found    : 2" in output


def test_unknown_message_type_is_allowed(tmp_path, capsys):
    """Analyzer should not hard-code Cassandra message types."""

    node_dir = tmp_path / "nodes" / "10.0.0.1" / "logs" / "cassandra"
    node_dir.mkdir(parents=True)

    (node_dir / "system.log").write_text(
        (
            "INFO [ScheduledTasks:1] "
            "2026-08-04 08:10:00,000 "
            "DroppedMessages.java:157 - "
            "SOME_NEW_TYPE messages were dropped "
            "in the last 5 s: "
            "1 internal and 9 cross node\n"
        )
    )

    droppedmessages.run(
        make_args(
            str(tmp_path),
            type="SOME_NEW_TYPE",
        )
    )

    output = capsys.readouterr().out

    assert "Message type       : SOME_NEW_TYPE" in output
    assert "Dropped messages   : 10" in output
    assert "  Internal         : 1" in output
    assert "  Cross-node       : 9" in output


def test_no_false_positive_from_configuration(
    tmp_path,
    capsys,
):
    """Configuration strings must not be runtime evidence."""

    node_dir = tmp_path / "nodes" / "10.0.0.1" / "logs" / "cassandra"
    node_dir.mkdir(parents=True)

    (node_dir / "system.log").write_text(
        "\n".join(
            [
                (
                    "INFO [main] "
                    "2026-08-04 08:09:00,000 "
                    "Config.java:714 - "
                    "Node configuration:"
                    "[commitlog_sync=periodic, "
                    "max_mutation_size_in_kb=16384]"
                ),
                (
                    "INFO [ScheduledTasks:1] "
                    "2026-08-04 08:10:00,000 "
                    "DroppedMessages.java:157 - "
                    "MUTATION messages were dropped "
                    "in the last 5 s: "
                    "0 internal and 100 cross node"
                ),
            ]
        )
        + "\n"
    )

    droppedmessages.run(
        make_args(
            str(tmp_path),
            type="MUTATION",
        )
    )

    output = capsys.readouterr().out

    assert "Dropped messages   : 100" in output

    assert "Oversized mutation:" not in output
    assert "Commitlog pressure:" not in output

    assert (
        "No relevant runtime symptom was found " "in the provided analysis window."
    ) in output


def test_no_symptom_found(tmp_path, capsys):
    """Report should be clean when no related runtime symptom exists."""

    node_dir = tmp_path / "nodes" / "10.0.0.1" / "logs" / "cassandra"
    node_dir.mkdir(parents=True)

    (node_dir / "system.log").write_text(
        (
            "INFO [ScheduledTasks:1] "
            "2026-08-04 08:10:00,000 "
            "DroppedMessages.java:157 - "
            "MUTATION messages were dropped "
            "in the last 5 s: "
            "0 internal and 500 cross node\n"
        )
    )

    droppedmessages.run(
        make_args(
            str(tmp_path),
            type="MUTATION",
        )
    )

    output = capsys.readouterr().out

    assert "Dropped messages   : 500" in output

    assert (
        "No relevant runtime symptom was found " "in the provided analysis window."
    ) in output


def test_top_five_incidents(tmp_path, capsys):
    """Show the five incidents with the largest drop counts."""

    node_dir = tmp_path / "nodes" / "10.0.0.1" / "logs" / "cassandra"
    node_dir.mkdir(parents=True)

    counts = [
        100,
        900,
        300,
        700,
        200,
        800,
        400,
    ]

    lines = []

    # Keep incidents >5 minutes apart so they are
    # not grouped together.
    for index, count in enumerate(counts):

        minute = index * 10

        lines.append(
            (
                "INFO [ScheduledTasks:1] "
                "2026-08-04 %02d:%02d:00,000 "
                "DroppedMessages.java:157 - "
                "MUTATION messages were dropped "
                "in the last 5 s: "
                "0 internal and %d cross node"
            )
            % (
                8 + minute // 60,
                minute % 60,
                count,
            )
        )

    (node_dir / "system.log").write_text("\n".join(lines) + "\n")

    droppedmessages.run(
        make_args(
            str(tmp_path),
            type="MUTATION",
        )
    )

    output = capsys.readouterr().out

    assert "Incidents found    : 7" in output

    assert ("Incidents shown    : Top 5 by " "dropped-message count") in output

    # The five largest incidents are:
    #
    # 900
    # 800
    # 700
    # 400
    # 300
    #
    # Verify they are displayed in descending order.

    expected = [
        "Dropped messages   : 900",
        "Dropped messages   : 800",
        "Dropped messages   : 700",
        "Dropped messages   : 400",
        "Dropped messages   : 300",
    ]

    positions = [output.find(value) for value in expected]

    assert all(position != -1 for position in positions)

    assert positions == sorted(positions)

    # The smaller incidents must not be displayed
    # as incident totals.
    #
    # Do not search simply for "100"/"200" because
    # the overall report total may contain those digits.

    assert "Dropped messages   : 100\n" not in output
    assert "Dropped messages   : 200\n" not in output


def test_five_or_fewer_incidents_show_all(
    tmp_path,
    capsys,
):
    """When <=5 incidents exist, all incidents should be displayed."""

    node_dir = tmp_path / "nodes" / "10.0.0.1" / "logs" / "cassandra"
    node_dir.mkdir(parents=True)

    counts = [
        100,
        200,
        300,
    ]

    lines = []

    for index, count in enumerate(counts):

        lines.append(
            (
                "INFO [ScheduledTasks:1] "
                "2026-08-04 08:%02d:00,000 "
                "DroppedMessages.java:157 - "
                "MUTATION messages were dropped "
                "in the last 5 s: "
                "0 internal and %d cross node"
            )
            % (
                index * 10,
                count,
            )
        )

    (node_dir / "system.log").write_text("\n".join(lines) + "\n")

    droppedmessages.run(
        make_args(
            str(tmp_path),
            type="MUTATION",
        )
    )

    output = capsys.readouterr().out

    assert "Incidents found    : 3" in output
    assert "Incidents shown    : 3" in output

    assert "Dropped messages   : 100" in output
    assert "Dropped messages   : 200" in output
    assert "Dropped messages   : 300" in output


def test_window_argument(diag_dir, capsys):
    """The configured +/- analysis window should be accepted."""

    droppedmessages.run(
        make_args(
            diag_dir,
            type="MUTATION",
            window=10,
        )
    )

    output = capsys.readouterr().out

    assert "Evidence window    : +/- 10 minutes" in output


def test_evidence_window_extends_before_start(
    tmp_path,
    capsys,
):
    """Evidence before --start should correlate within --window."""

    node_dir = tmp_path / "nodes" / "10.0.0.1" / "logs" / "cassandra"
    node_dir.mkdir(parents=True)

    (node_dir / "system.log").write_text(
        "\n".join(
            [
                (
                    "WARN [GossipTasks:1] "
                    "2026-08-04 07:50:00,000 "
                    "GCInspector.java:283 - "
                    "G1 Young Generation GC in 1064ms"
                ),
                (
                    "INFO [ScheduledTasks:1] "
                    "2026-08-04 08:05:00,000 "
                    "DroppedMessages.java:157 - "
                    "MUTATION messages were dropped "
                    "in the last 5 s: "
                    "0 internal and 100 cross node"
                ),
            ]
        )
        + "\n"
    )

    droppedmessages.run(
        make_args(
            str(tmp_path),
            type="MUTATION",
            start="2026-08-04 08:00:00,000",
            end="2026-08-04 09:00:00,000",
            window=20,
        )
    )

    output = capsys.readouterr().out

    assert "Dropped messages   : 100" in output
    assert "GC pressure: 1 event(s)" in output


def test_evidence_window_extends_after_end(
    tmp_path,
    capsys,
):
    """Evidence after --end should correlate within --window."""

    node_dir = tmp_path / "nodes" / "10.0.0.1" / "logs" / "cassandra"
    node_dir.mkdir(parents=True)

    (node_dir / "system.log").write_text(
        "\n".join(
            [
                (
                    "INFO [ScheduledTasks:1] "
                    "2026-08-04 08:55:00,000 "
                    "DroppedMessages.java:157 - "
                    "MUTATION messages were dropped "
                    "in the last 5 s: "
                    "0 internal and 100 cross node"
                ),
                (
                    "WARN [GossipTasks:1] "
                    "2026-08-04 09:10:00,000 "
                    "GCInspector.java:283 - "
                    "GC pause took 1000ms"
                ),
            ]
        )
        + "\n"
    )

    droppedmessages.run(
        make_args(
            str(tmp_path),
            type="MUTATION",
            start="2026-08-04 08:00:00,000",
            end="2026-08-04 09:00:00,000",
            window=20,
        )
    )

    output = capsys.readouterr().out

    assert "Dropped messages   : 100" in output
    assert "GC pressure: 1 event(s)" in output


def test_evidence_outside_window_is_ignored(
    tmp_path,
    capsys,
):
    """Runtime evidence outside +/- window must not correlate."""

    node_dir = tmp_path / "nodes" / "10.0.0.1" / "logs" / "cassandra"
    node_dir.mkdir(parents=True)

    (node_dir / "system.log").write_text(
        "\n".join(
            [
                (
                    "WARN [GossipTasks:1] "
                    "2026-08-04 07:30:00,000 "
                    "GCInspector.java:283 - "
                    "GC pause took 1000ms"
                ),
                (
                    "INFO [ScheduledTasks:1] "
                    "2026-08-04 08:05:00,000 "
                    "DroppedMessages.java:157 - "
                    "MUTATION messages were dropped "
                    "in the last 5 s: "
                    "0 internal and 100 cross node"
                ),
            ]
        )
        + "\n"
    )

    droppedmessages.run(
        make_args(
            str(tmp_path),
            type="MUTATION",
            start="2026-08-04 08:00:00,000",
            end="2026-08-04 09:00:00,000",
            window=20,
        )
    )

    output = capsys.readouterr().out

    assert "Dropped messages   : 100" in output
    assert "GC pressure:" not in output

    assert (
        "No relevant runtime symptom was found " "in the provided analysis window."
    ) in output


def test_evidence_from_other_node_is_ignored(
    tmp_path,
    capsys,
):
    """Evidence from another node must not correlate."""

    node_a = tmp_path / "nodes" / "10.0.0.1" / "logs" / "cassandra"

    node_b = tmp_path / "nodes" / "10.0.0.2" / "logs" / "cassandra"

    node_a.mkdir(parents=True)
    node_b.mkdir(parents=True)

    (node_a / "system.log").write_text(
        (
            "INFO [ScheduledTasks:1] "
            "2026-08-04 08:10:00,000 "
            "DroppedMessages.java:157 - "
            "MUTATION messages were dropped "
            "in the last 5 s: "
            "0 internal and 100 cross node\n"
        )
    )

    (node_b / "system.log").write_text(
        (
            "WARN [GossipTasks:1] "
            "2026-08-04 08:09:00,000 "
            "GCInspector.java:283 - "
            "GC pause took 1000ms\n"
        )
    )

    droppedmessages.run(
        make_args(
            str(tmp_path),
            type="MUTATION",
        )
    )

    output = capsys.readouterr().out

    assert "Dropped messages   : 100" in output
    assert "GC pressure:" not in output

    assert (
        "No relevant runtime symptom was found " "in the provided analysis window."
    ) in output


def test_continuation_line_is_used_for_evidence(
    tmp_path,
    capsys,
):
    """Exception continuation lines should be available for evidence matching."""

    node_dir = tmp_path / "nodes" / "10.0.0.1" / "logs" / "cassandra"
    node_dir.mkdir(parents=True)

    (node_dir / "system.log").write_text(
        "\n".join(
            [
                (
                    "WARN [PO-thread-3] "
                    "2026-08-04 08:04:00,000 "
                    "NoSpamLogger.java:98 - "
                    "Lease LWT query failed"
                ),
                (
                    "org.apache.cassandra.exceptions."
                    "WriteTimeoutException: CAS timed out due to contention"
                ),
                (
                    "INFO [ScheduledTasks:1] "
                    "2026-08-04 08:05:00,000 "
                    "DroppedMessages.java:157 - "
                    "MUTATION messages were dropped "
                    "in the last 5 s: "
                    "0 internal and 100 cross node"
                ),
            ]
        )
        + "\n"
    )

    droppedmessages.run(
        make_args(
            str(tmp_path),
            type="MUTATION",
            window=20,
        )
    )

    output = capsys.readouterr().out

    assert "Dropped messages   : 100" in output
    assert "Request timeout/overload: 1 event(s)" in output
