import json

import research_leakproof as leakproof
from research_leakproof.demo import make_report
from research_leakproof.finding import Severity


def test_report_json_roundtrips():
    r = leakproof.audit(metrics={"pearson_r": 0.6})
    data = json.loads(r.to_json())
    assert "counts" in data and "findings" in data
    assert data["findings"][0]["check"] == "metric_honesty"


def test_report_failed_respects_threshold():
    r = leakproof.audit(metrics={"pearson_r": 0.6})  # a warn, no error
    assert r.failed(Severity.ERROR) is False
    assert r.failed(Severity.WARN) is True


def test_integrity_block_lists_each_check():
    r = leakproof.audit(groups_train=[1], groups_test=[2], metrics={"pearson_r": 0.6, "r2": 0.2,
                                                                    "baseline_r2": 0.1})
    block = r.integrity_block()
    assert "group_leakage" in block and "metric_honesty" in block
    assert "PASS" in block


def test_suppress_downgrades_named_check():
    r = leakproof.audit(groups_train=[1, 2], groups_test=[2, 3], suppress=["group_leakage"])
    f = next(x for x in r.findings if x.check == "group_leakage")
    assert f.severity == Severity.INFO
    assert "suppressed" in f.title.lower()


def test_demo_surfaces_the_planted_problems():
    r = make_report()
    by_check = {f.check: f.severity for f in r.findings}
    assert by_check["split_leakage"] == Severity.ERROR
    assert by_check["group_leakage"] == Severity.ERROR
    assert by_check["shape_collapse"] == Severity.ERROR
    assert by_check["effective_n"] == Severity.WARN
    assert by_check["temporal_leakage"] == Severity.WARN
    assert by_check["metric_honesty"] == Severity.WARN
    assert by_check["power"] == Severity.WARN
    assert by_check["multiple_comparisons"] == Severity.WARN
    assert r.failed() is True
