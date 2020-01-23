"""validates the sperf commands are wired up correctly"""
from pysper.commands import sperf

def test_sperf_global_flags():
    """testing global flags are wired up"""
    parser = sperf.build_parser()
    args = parser.parse_args(["--debug", "--progress"])
    assert hasattr(args, "debug")
    assert hasattr(args, "progress")

def test_sperf_global_short_flags():
    """tests the global short flag"""
    parser = sperf.build_parser()
    args = parser.parse_args(["-v", "-p"])
    assert hasattr(args, "debug")
    assert hasattr(args, "progress")

def test_sperf_will_break_if_incorrect_comamnd_is_used():
    """this is here so we can rely on the parser tests
    for subcommands tests being accurate"""
    parser = sperf.build_parser()
    success = False
    try:
        parser.parse_args(["nevergonnabereal"])
    except SystemExit as e:
        success = True
        assert str(e) == "2"
    assert success

def test_core_diag_wired():
    """verify cassread is connected"""
    parser = sperf.build_parser()
    args = parser.parse_args(["core", "diag"])
    assert hasattr(args, "func")

def test_search_filtercache_wired():
    """verify filtercache is connected"""
    parser = sperf.build_parser()
    args = parser.parse_args(["search", "filtercache"])
    assert hasattr(args, "func")


def test_jarcheck_wired():
    """verify jarcheck is connected"""
    parser = sperf.build_parser()
    args = parser.parse_args(["core", "jarcheck"])
    assert hasattr(args, "func")

def test_schema_wired():
    """verify schema is connected"""
    parser = sperf.build_parser()
    args = parser.parse_args(["core", "schema"])
    assert hasattr(args, "func")

def test_slowquery_wired():
    """verify slowquery is connected"""
    parser = sperf.build_parser()
    args = parser.parse_args(["core", "slowquery"])
    assert hasattr(args, "func")

def test_solrqueryagg_wired():
    """verify solrqueryagg is connected"""
    parser = sperf.build_parser()
    args = parser.parse_args(["search", "queryscore"])
    assert hasattr(args, "func")

def test_sysbottle_wired():
    """verify sysbottle is connected"""
    parser = sperf.build_parser()
    args = parser.parse_args(["sysbottle", "iostat.txt"])
    assert hasattr(args, "func")
