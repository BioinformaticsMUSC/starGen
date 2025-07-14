import os
import tempfile

from starGen.qc import parse_star_log

def create_fake_log(path, sample_name="sample1"):
    content = """\
                          Number of input reads |	1000000
                   Uniquely mapped reads number |	850000
                        Uniquely mapped reads % |	85.00%
"""
    log_path = os.path.join(path, f"{sample_name}.Log.final.out")
    with open(log_path, "w") as f:
        f.write(content)

    return log_path

def test_parse_star_log_returns_expected_metrics():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = create_fake_log(tmpdir, "mysample")

        summary = parse_star_log(log_file)

        assert isinstance(summary, dict)
        assert summary["sample"] == "mysample"
        assert summary["uniquely_mapped_reads"] == 850000
        assert summary["uniquely_mapped_percent"] == 85.00
