"""Registry of runtime checks, run in this order."""

from . import (
    effective_n,
    group_leakage,
    metric_honesty,
    multiple_comparisons,
    power,
    shape_collapse,
    split_leakage,
    temporal_leakage,
)

RUNTIME_CHECKS = [
    split_leakage,
    group_leakage,
    temporal_leakage,
    effective_n,
    shape_collapse,
    metric_honesty,
    power,
    multiple_comparisons,
]

__all__ = ["RUNTIME_CHECKS"]
