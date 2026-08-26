from __future__ import annotations

import numpy as np
import pandas as pd

from troca_fontes.analyses import (
    MISSING_BUCKET,
    feature_migration_matrices,
    segment_labels,
    sentinel_bucket_label,
)


def test_segment_labels_are_discovered_when_values_are_not_configured():
    frame = pd.DataFrame({"channel": ["Branch", "App", None, "Branch"]})

    assert segment_labels(frame, "channel") == (
        "TOTAL",
        "App",
        "Branch",
        "NULL",
    )


def test_no_segmentation_produces_total_only():
    assert segment_labels(pd.DataFrame({"x": [1]}), None) == ("TOTAL",)


def test_feature_matrix_counts_sentinels_deciles_and_missing():
    frame = pd.DataFrame(
        {
            "feature_ft": [-9, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, np.nan],
            "feature_ft_ste": [9, -3, 0, 2, 1, 4, 3, 6, 5, 8, 7, np.nan, 10],
        }
    )

    result = feature_migration_matrices(frame, features=["feature_ft"])[
        "feature_ft"
    ]

    assert result.matrix.to_numpy().sum() == len(frame)
    assert result.matrix.loc[sentinel_bucket_label(-9)].sum() == 1
    assert result.matrix.loc[sentinel_bucket_label(-1)].sum() == 1
    assert sentinel_bucket_label(-3) in result.matrix.columns
    assert sentinel_bucket_label(-3) not in result.matrix.index
    assert result.matrix.loc[MISSING_BUCKET].sum() == 1
    assert result.matrix[MISSING_BUCKET].sum() == 1
    assert len(result.old_edges) == 11
    assert len(result.new_edges) == 11


def test_repeated_values_are_not_arbitrarily_split_across_deciles():
    frame = pd.DataFrame({"x": [0] * 20, "x_ste": [0] * 20})
    result = feature_migration_matrices(frame, features=["x"])["x"]

    assert result.matrix.loc["D01", "D01"] == 20
    assert result.matrix.loc["D02":"D10"].to_numpy().sum() == 0
