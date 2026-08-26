"""Derive which model features a migration substitutes, and their importances.

The user's "derive automatically" rule: given the model's feature list (from the
pickled classifier's ``feature_names_in_``) and a migration's ``feature_suffix``
(or an explicit ``feature_names`` list), the substituted features are those that
match. This tells extraction which columns to pull from the new source and tells
the analyses which columns to reconcile.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Sequence

import pandas as pd

from .config import MigrationConfig, ModelConfig


# Repo root, so relative pkl paths in config resolve regardless of cwd.
_REPO_ROOT = Path(__file__).resolve().parents[3]


@lru_cache(maxsize=None)
def _load_clf(pkl_path: str):
    from joblib import load

    path = Path(pkl_path)
    if not path.is_absolute():
        path = _REPO_ROOT / path
    return load(path)


def model_feature_names(model: ModelConfig) -> list[str]:
    """Lowercased scoring feature names, in the order the model expects."""

    clf = _load_clf(model.pkl_path)
    return [c.lower() for c in clf.feature_names_in_]


def feature_importances(model: ModelConfig) -> pd.Series:
    """Normalized (sum-to-one) importances indexed by lowercased feature name."""

    clf = _load_clf(model.pkl_path)
    imp = pd.Series(
        clf.feature_importances_,
        index=[c.lower() for c in clf.feature_names_in_],
        dtype=float,
    )
    total = imp.sum()
    return imp / total if total else imp


def substituted_features(
    model: ModelConfig,
    migration: MigrationConfig,
    available_cols: Sequence[str] | None = None,
) -> list[str]:
    """Features of ``model`` that ``migration`` re-sources.

    When ``feature_names`` is given it is used verbatim; otherwise every model
    feature whose name contains ``feature_suffix`` is selected. If
    ``available_cols`` is provided, the result is restricted to those columns
    (lowercased), matching the notebook's ``[c for c in df if '_ft' in c]``.
    """

    if migration.feature_names:
        feats = [f.lower() for f in migration.feature_names]
    else:
        suffix = migration.feature_suffix.lower()
        feats = [f for f in model_feature_names(model) if suffix in f]

    if available_cols is not None:
        avail = {c.lower() for c in available_cols}
        feats = [f for f in feats if f in avail]
    return feats


@dataclass(frozen=True)
class ResolvedMigration:
    """Everything the pipeline needs to run one (model, migration)."""

    migration: MigrationConfig
    features: tuple[str, ...]  # substituted feature names (old source == flat table)


def resolve(
    model: ModelConfig,
    migrations: Sequence[MigrationConfig],
    available_cols: Sequence[str] | None = None,
) -> list[ResolvedMigration]:
    return [
        ResolvedMigration(
            migration=m,
            features=tuple(substituted_features(model, m, available_cols)),
        )
        for m in migrations
    ]


def all_substituted_features(
    resolved: Sequence[ResolvedMigration],
) -> list[str]:
    """Union of substituted features across migrations, order-preserving."""

    seen: dict[str, None] = {}
    for r in resolved:
        for f in r.features:
            seen.setdefault(f, None)
    return list(seen)
