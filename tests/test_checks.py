import numpy as np

import research_leakproof as leakproof
from research_leakproof.finding import Severity


def sev(report, check):
    for f in report.findings:
        if f.check == check:
            return f.severity
    return None


def test_split_leakage_fires_on_shared_rows():
    train = np.arange(20).reshape(10, 2)
    test = np.vstack([np.arange(100, 110).reshape(5, 2), train[:2]])  # two rows copied from train
    r = leakproof.audit(X_train=train, X_test=test)
    assert sev(r, "split_leakage") == Severity.ERROR


def test_split_leakage_clean():
    train = np.arange(20).reshape(10, 2)
    test = np.arange(100, 120).reshape(10, 2)
    r = leakproof.audit(X_train=train, X_test=test)
    assert sev(r, "split_leakage") == Severity.OK


def test_group_leakage_fires_on_overlap():
    r = leakproof.audit(groups_train=[1, 1, 2, 3], groups_test=[3, 4, 5])  # group 3 in both
    assert sev(r, "group_leakage") == Severity.ERROR


def test_group_leakage_clean():
    r = leakproof.audit(groups_train=[1, 2, 3], groups_test=[4, 5, 6])
    assert sev(r, "group_leakage") == Severity.OK


def test_temporal_leakage_fires_on_overlap():
    r = leakproof.audit(time_train=np.arange(0, 100), time_test=np.arange(90, 140))
    assert sev(r, "temporal_leakage") == Severity.WARN


def test_temporal_leakage_clean():
    r = leakproof.audit(time_train=np.arange(0, 100), time_test=np.arange(100, 140))
    assert sev(r, "temporal_leakage") == Severity.OK


def test_effective_n_fires_on_repeated_groups():
    groups = np.repeat(np.arange(10), 20)  # 200 rows, 10 units -> 20x inflation
    r = leakproof.audit(groups=groups)
    assert sev(r, "effective_n") == Severity.WARN
    f = next(x for x in r.findings if x.check == "effective_n")
    assert f.evidence["inflation_factor"] >= 2


def test_effective_n_clean():
    r = leakproof.audit(groups=np.arange(50))
    assert sev(r, "effective_n") == Severity.OK


def test_shape_collapse_fires_when_only_unit_means_predicted():
    rng = np.random.default_rng(1)
    n_units, t = 25, 8
    unit_mean = rng.normal(size=n_units)
    units = np.repeat(np.arange(n_units), t)
    shape = np.sin(np.linspace(0, 3.14, t))
    targets = unit_mean[units] + 0.6 * np.tile(shape, n_units)
    predictions = unit_mean[units]  # no within-unit signal
    r = leakproof.audit(predictions=predictions, targets=targets, units=units)
    assert sev(r, "shape_collapse") == Severity.ERROR


def test_shape_collapse_clean_when_within_unit_tracked():
    rng = np.random.default_rng(2)
    n_units, t = 25, 8
    unit_mean = rng.normal(size=n_units)
    units = np.repeat(np.arange(n_units), t)
    shape = np.sin(np.linspace(0, 3.14, t))
    targets = unit_mean[units] + 0.6 * np.tile(shape, n_units)
    predictions = targets + 0.05 * rng.normal(size=targets.size)  # tracks within-unit shape
    r = leakproof.audit(predictions=predictions, targets=targets, units=units)
    assert sev(r, "shape_collapse") == Severity.OK


def test_metric_honesty_warns_on_correlation_only():
    r = leakproof.audit(metrics={"pearson_r": 0.6})
    assert sev(r, "metric_honesty") == Severity.WARN


def test_metric_honesty_ok_with_error_and_baseline():
    r = leakproof.audit(metrics={"pearson_r": 0.6, "r2": 0.3, "baseline_r2": 0.1})
    assert sev(r, "metric_honesty") == Severity.OK


def test_metric_honesty_info_without_baseline():
    r = leakproof.audit(metrics={"r2": 0.3, "mse": 0.5})
    assert sev(r, "metric_honesty") == Severity.INFO


def test_power_warns_when_underpowered():
    r = leakproof.audit(n_test=42, effect_size=0.1)
    assert sev(r, "power") == Severity.WARN


def test_power_ok_with_large_n():
    r = leakproof.audit(n_test=2000, effect_size=0.5)
    assert sev(r, "power") == Severity.OK


def test_power_reports_floor_without_claimed_effect():
    r = leakproof.audit(n_test=82)
    f = next(x for x in r.findings if x.check == "power")
    assert f.severity == Severity.INFO
    assert 0.0 < f.evidence["min_detectable_r"] < 1.0


def test_multiple_comparisons_warns_when_uncorrected():
    r = leakproof.audit(n_comparisons=10, corrected=False)
    assert sev(r, "multiple_comparisons") == Severity.WARN


def test_multiple_comparisons_ok_when_corrected():
    r = leakproof.audit(n_comparisons=10, corrected=True)
    assert sev(r, "multiple_comparisons") == Severity.OK


def test_checks_are_skipped_without_inputs():
    r = leakproof.audit(metrics={"pearson_r": 0.6, "r2": 0.3, "baseline_r2": 0.1})
    assert {f.check for f in r.findings} == {"metric_honesty"}


def test_unknown_kwarg_raises():
    import pytest
    with pytest.raises(TypeError):
        leakproof.audit(not_a_real_arg=1)
