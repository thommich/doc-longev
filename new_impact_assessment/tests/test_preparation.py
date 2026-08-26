from __future__ import annotations

import sys
from types import SimpleNamespace

import numpy as np
import pandas as pd

from troca_fontes import preparation
from troca_fontes.config import ModelConfig, TableRef


class _Classifier:
    def predict_proba(self, frame):
        probability = frame["feature_ft"].to_numpy(dtype=float) / 100.0
        return np.column_stack([1.0 - probability, probability])


def test_eval_frame_preserves_old_and_new_values_and_scores_with_new(monkeypatch):
    monkeypatch.setattr(
        preparation, "model_feature_names", lambda model: ["feature_ft", "other"]
    )
    monkeypatch.setattr(preparation, "_load_clf", lambda path: _Classifier())
    monkeypatch.setitem(
        sys.modules,
        "auto_gh",
        SimpleNamespace(
            get_gh=lambda frame, score_col, cutpoints: (
                frame[score_col] >= 0.15
            ).astype(int)
        ),
    )
    model = ModelConfig(
        name="model",
        display_name="Model",
        pkl_path="unused.pkl",
        flat_table=TableRef(engine="teradata", name="db.flat"),
        id_cols=("id",),
        cutpoints_gh=(0.0, 1.0),
    )
    flat = pd.DataFrame(
        {
            "id": [1, 2],
            "feature_ft": [1.0, 2.0],
            "other": [5.0, 6.0],
            "score": [0.01, 0.02],
            "gh": [0, 0],
            "channel": ["legacy", "legacy"],
        }
    )
    new = pd.DataFrame(
        {"id": [1, 2], "feature_ft": [10.0, 20.0], "channel": ["App", "Branch"]}
    )

    result = preparation.build_eval_frame(
        flat,
        new,
        model=model,
        substituted=["feature_ft"],
        join_cols=["id"],
        segmentation_col="channel",
    )

    assert result["feature_ft"].tolist() == [1.0, 2.0]
    assert result["feature_ft_ste"].tolist() == [10.0, 20.0]
    assert result[preparation.NEW_SCORE_COL].tolist() == [0.1, 0.2]
    assert result["channel"].tolist() == ["App", "Branch"]

