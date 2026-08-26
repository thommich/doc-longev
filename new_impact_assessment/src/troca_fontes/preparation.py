"""Data preparation: join new-source features, rescore, assign GH.

Encapsulates the notebooks' shared prep steps so extraction outputs become a
single evaluation frame ready for the analyses.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

from .config import ModelConfig
from .feature_resolution import _load_clf, model_feature_names


# ``auto_gh.get_gh`` lives at the repo root; make it importable when running
# from within the package.
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

NEW_SCORE_COL = "score_mdl_new_src"
NEW_GH_COL = "GH_new_src"
STE_SUFFIX = "_ste"


def lower_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.lower() for c in df.columns]
    return df


def dedup_population(
    df: pd.DataFrame, subset: Sequence[str], order_by: Sequence[str]
) -> pd.DataFrame:
    """Deduplicate keeping worst-performing row per key (notebook logic)."""

    ascending = [True] * len(subset) + [False] * len(order_by)
    return (
        df.sort_values(list(subset) + list(order_by), ascending=ascending)
        .drop_duplicates(subset=list(subset), keep="first")
    )


def build_eval_frame(
    flat: pd.DataFrame,
    new_features: pd.DataFrame,
    *,
    model: ModelConfig,
    substituted: Sequence[str],
    join_cols: Sequence[str],
    target: pd.DataFrame | None = None,
    target_col: str | None = None,
    segmentation_col: str | None = None,
    ste_suffix: str = STE_SUFFIX,
) -> pd.DataFrame:
    """Assemble the evaluation frame.

    Steps (mirroring the notebooks):
    1. Preserve old-source features under their model names and left-merge the
       new-source versions under the ``_ste`` suffix.
    2. Keep both versions for drift and feature-migration analyses; use only the
       new-source versions when rescoring.
    3. Left-merge the target/contract table if provided.
    4. Rescore with the model pickle and assign the new GH.
    5. Derive ``ctrt_itau`` from target availability.
    """

    from auto_gh import get_gh  # repo-root helper

    flat = lower_columns(flat)
    new_features = lower_columns(new_features)
    if target is not None:
        target = lower_columns(target)
    join_cols = [c.lower() for c in join_cols]
    substituted = [c.lower() for c in substituted]
    segmentation_col = segmentation_col.lower() if segmentation_col else None

    # ensure join keys share dtype (pk_datref_xx is a date-like string/int)
    for col in join_cols:
        if col in flat.columns and col in new_features.columns:
            if flat[col].dtype != new_features[col].dtype:
                new_features[col] = new_features[col].astype(flat[col].dtype)

    missing_old = [c for c in substituted if c not in flat.columns]
    missing_new = [c for c in substituted if c not in new_features.columns]
    if missing_old or missing_new:
        details = []
        if missing_old:
            details.append(f"old source missing {missing_old}")
        if missing_new:
            details.append(f"new source missing {missing_new}")
        raise KeyError("Cannot compare substituted features: " + "; ".join(details))

    keep_new = join_cols + list(substituted)
    has_new_segmentation = bool(
        segmentation_col and segmentation_col in new_features.columns
    )
    if has_new_segmentation:
        keep_new.append(segmentation_col)
    new_features = new_features[keep_new].copy()

    # New-source values get a suffix; the unsuffixed model columns remain the
    # old-source values. This is the convention expected by analyses.py.
    new_features = new_features.rename(
        columns={col: f"{col}{ste_suffix}" for col in substituted}
    )

    # The migration's segmentation describes the new source and is therefore
    # authoritative if a same-named legacy column happens to exist in flat.
    if has_new_segmentation and segmentation_col in flat.columns:
        flat = flat.drop(columns=[segmentation_col])
    eval_df = flat.merge(new_features, on=join_cols, how="left")

    if target is not None:
        drop = [
            c for c in target.columns if c in eval_df.columns and c not in join_cols
        ]
        eval_df = eval_df.merge(
            target.drop(columns=drop), on=join_cols, how="left"
        )

    # rescore + GH
    feature_order = model_feature_names(model)
    clf = _load_clf(model.pkl_path)
    scoring_frame = eval_df[feature_order].copy()
    for col in substituted:
        scoring_frame[col] = eval_df[f"{col}{ste_suffix}"]
    eval_df[NEW_SCORE_COL] = clf.predict_proba(scoring_frame)[:, 1]
    eval_df[NEW_GH_COL] = get_gh(
        eval_df, NEW_SCORE_COL, list(model.cutpoints_gh)
    )

    if target_col and target_col in eval_df.columns:
        eval_df["ctrt_itau"] = np.where(eval_df[target_col].isna(), 0, 1)
    return eval_df
