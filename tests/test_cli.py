def test_help():
    from subprocess import run
    result = run(["starGen", "--help"])
    assert result.returncode == 0
