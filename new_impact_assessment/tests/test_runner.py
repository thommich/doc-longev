from __future__ import annotations

import pandas as pd

from troca_fontes.config import (
    ExperimentConfig,
    ModelConfig,
    PopulationSpec,
    SegmentationSpec,
    TableRef,
)
from troca_fontes.preparation import NEW_GH_COL, NEW_SCORE_COL
from troca_fontes.runner import _analyse_reference


def test_feature_matrices_are_created_per_population_and_segment():
    model = ModelConfig(
        name="model",
        display_name="Model",
        pkl_path="unused.pkl",
        flat_table=TableRef(engine="teradata", name="db.flat"),
        id_cols=("id",),
        cutpoints_gh=(0.0, 1.0),
        populations=(PopulationSpec("all", "All"),),
    )
    experiment = ExperimentConfig(
        name="experiment",
        model="model",
        migrations=("source",),
        report_sheet="Report",
        references=(),
        populations=("all",),
        analyses=("score_gh_match", "feature_migration_matrix"),
    )
    frame = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "channel": ["APP", "BRANCH", "APP"],
            "x": [0, 1, -1],
            "x_ste": [1, -1, 0],
            "score": [0.1, 0.2, 0.3],
            NEW_SCORE_COL: [0.2, 0.1, 0.3],
            "gh": [1, 2, 3],
            NEW_GH_COL: [2, 1, 3],
        }
    )

    result = _analyse_reference(
        frame,
        model=model,
        experiment=experiment,
        include_target=False,
        features=["x"],
        importances={"x": 1.0},
        segmentation=SegmentationSpec(
            "CHANNEL", values=("APP", "BRANCH"), include_null=False
        ),
    )

    assert result["segments"] == ("TOTAL", "APP", "BRANCH")
    assert result["feature_migration"]["all"]["APP"]["x"].matrix.to_numpy().sum() == 2
    assert result["feature_migration"]["all"]["BRANCH"]["x"].matrix.to_numpy().sum() == 1

