"""Pure analysis functions for source-substitution impact assessment.

The recovered score, GH, Gini, and drift metrics retain the notebooks' formulas
(including the signed 1-p.p. rule and per-segment denominators). Dynamic
migration segmentation and feature-decile migration matrices extend that base.

Results are returned as plain nested dicts keyed by segment / feature so the
report layer can map them onto the dashboard grid without re-computation.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score


# Reserved analysis labels. Configured/observed segment values are inserted
# between TOTAL and NULL.
TOTAL_SEGMENT = "TOTAL"
NULL_SEGMENT = "NULL"
DEFAULT_SEGMENTS = (TOTAL_SEGMENT,)

SENTINEL_PREFIX = "SENTINEL"
MISSING_BUCKET = "MISSING"


def sentinel_bucket_label(value: float) -> str:
    """Stable display label for one distinct negative sentinel value."""

    return f"{SENTINEL_PREFIX} ({value:g})"


def segment_labels(
    df: pd.DataFrame,
    segmentation_col: str | None,
    *,
    configured_values: Sequence[Any] = (),
    include_null: bool = True,
) -> tuple[str, ...]:
    """Build a stable breakdown from configured or observed unique values."""

    if not segmentation_col:
        return DEFAULT_SEGMENTS
    if segmentation_col not in df.columns:
        raise KeyError(f"Segmentation column {segmentation_col!r} not found")

    if configured_values:
        values = [str(value) for value in configured_values]
    else:
        observed = df[segmentation_col].dropna().astype("string")
        observed = observed[observed.str.upper() != NULL_SEGMENT]
        values = sorted(observed.unique().tolist(), key=str.casefold)

    reserved = {TOTAL_SEGMENT, NULL_SEGMENT}
    collision = [value for value in values if value.upper() in reserved]
    if collision:
        raise ValueError(
            "Segmentation values collide with reserved labels TOTAL/NULL: "
            f"{collision}"
        )

    labels = [TOTAL_SEGMENT, *values]
    if include_null:
        labels.append(NULL_SEGMENT)
    return tuple(labels)


def _segment_mask(
    df: pd.DataFrame, segmentation_col: str | None, segment: str
) -> pd.Series:
    """Boolean mask selecting the rows belonging to ``segment``."""

    if segment == TOTAL_SEGMENT:
        return pd.Series(True, index=df.index)
    if not segmentation_col:
        return pd.Series(False, index=df.index)
    values = df[segmentation_col]
    if segment == NULL_SEGMENT:
        return values.isna() | (
            values.astype("string").str.upper() == NULL_SEGMENT
        )
    return values.astype("string").str.upper() == str(segment).upper()


def score_gh_match(
    df: pd.DataFrame,
    *,
    score_col: str,
    new_score_col: str,
    gh_col: str,
    new_gh_col: str,
    segmentation_col: str | None = None,
    segments: Sequence[str] | None = None,
    platform_col: str | None = None,
) -> dict[str, dict[str, float]]:
    """MATCH DE SCORE block: score/GH match rates + GH notch migration.

    - ``scores_6a``: share with score equal to the 6th decimal.
    - ``scores_1pp``: share with (new - old)/old < 0.01 (signed, per notebook).
    - ``gh_menos1``: share moving one GH notch down (new = old - 1).
    - ``gh_iguais``: share with unchanged GH.
    - ``gh_mais1``: share moving one GH notch up (new = old + 1).

    All rates use the segment row count as denominator.
    """

    segmentation_col = segmentation_col or platform_col
    segments = tuple(segments or segment_labels(df, segmentation_col))
    out: dict[str, dict[str, float]] = {}
    for seg in segments:
        d = df[_segment_mask(df, segmentation_col, seg)]
        n = len(d)
        if n == 0:
            out[seg] = {
                k: np.nan
                for k in (
                    "volume",
                    "scores_6a",
                    "scores_1pp",
                    "gh_menos1",
                    "gh_iguais",
                    "gh_mais1",
                )
            }
            continue
        gh_old = pd.to_numeric(d[gh_col], errors="coerce")
        gh_new = pd.to_numeric(d[new_gh_col], errors="coerce")
        delta = gh_new - gh_old
        out[seg] = {
            "volume": float(n),
            "scores_6a": (
                d[score_col].round(6) == d[new_score_col].round(6)
            ).sum()
            / n,
            "scores_1pp": (
                (d[new_score_col] - d[score_col]) / d[score_col] < 0.01
            ).sum()
            / n,
            "gh_menos1": (delta == -1).sum() / n,
            "gh_iguais": (gh_old == gh_new).sum() / n,
            "gh_mais1": (delta == 1).sum() / n,
        }
    return out


def migration_matrix(
    df: pd.DataFrame, *, gh_col: str, new_gh_col: str
) -> pd.DataFrame:
    """GH migration crosstab (old GH x new GH), as in the notebooks."""

    return pd.crosstab(df[gh_col], df[new_gh_col])


def performance(
    df: pd.DataFrame,
    *,
    target_col: str,
    score_col: str,
    new_score_col: str,
    segmentation_col: str | None = None,
    segments: Sequence[str] | None = None,
    platform_col: str | None = None,
) -> dict[str, dict[str, float]]:
    """PERFORMANCE block: volumetria, taxa de maus and Gini before/after.

    Gini = 2 * AUC - 1. Computed only where the segment has both classes.
    """

    segmentation_col = segmentation_col or platform_col
    segments = tuple(segments or segment_labels(df, segmentation_col))
    out: dict[str, dict[str, float]] = {}
    for seg in segments:
        d = df[_segment_mask(df, segmentation_col, seg)]
        y = pd.to_numeric(d[target_col], errors="coerce")
        n = len(d)
        maus = int((y == 1).sum())
        rec = {
            "vol_total": float(n),
            "vol_maus": float(maus),
            "taxa_maus": (maus / n) if n else np.nan,
            "gini_antes": np.nan,
            "gini_depois": np.nan,
            "delta_gini": np.nan,
        }
        if n and y.nunique(dropna=True) == 2:
            gini_antes = 2 * roc_auc_score(y, d[score_col]) - 1
            gini_depois = 2 * roc_auc_score(y, d[new_score_col]) - 1
            rec["gini_antes"] = gini_antes
            rec["gini_depois"] = gini_depois
            rec["delta_gini"] = gini_depois - gini_antes
        out[seg] = rec
    return out


def variable_drift(
    df: pd.DataFrame,
    *,
    features: Sequence[str],
    ste_suffix: str = "_ste",
    segmentation_col: str | None = None,
    importances: Mapping[str, float] | None = None,
    segments: Sequence[str] | None = None,
    platform_col: str | None = None,
) -> dict[str, dict[str, dict[str, float]]]:
    """ANALISE POR VARIAVEL block.

    Per feature and segment:
    - ``match_6a``: share equal to 6th decimal over non-null old values.
    - ``var_pct``: nanmean of (old - new)/old, masking nulls and old = 0.
    - ``importancia``: normalized model importance (segment-invariant).

    Returns ``result[segment][feature] = {...}``.
    """

    segmentation_col = segmentation_col or platform_col
    segments = tuple(segments or segment_labels(df, segmentation_col))
    out: dict[str, dict[str, dict[str, float]]] = {}
    for seg in segments:
        d = df[_segment_mask(df, segmentation_col, seg)]
        seg_res: dict[str, dict[str, float]] = {}
        for col in features:
            ste = f"{col}{ste_suffix}"
            non_null = int((~d[col].isna()).sum())
            match_6a = (
                (d[col].round(6) == d[ste].round(6)).sum() / non_null
                if non_null
                else np.nan
            )
            var_pct = np.nanmean(
                np.where(
                    d[col].isna() | d[ste].isna() | (d[col] == 0),
                    np.nan,
                    (d[col] - d[ste]) / d[col],
                )
            )
            seg_res[col] = {
                "match_6a": match_6a,
                "var_pct": var_pct,
                "importancia": float((importances or {}).get(col, np.nan)),
            }
        out[seg] = seg_res
    return out


@dataclass(frozen=True)
class FeatureMigrationMatrix:
    """Counts and independently fitted old/new nonnegative decile edges."""

    feature: str
    matrix: pd.DataFrame
    old_edges: tuple[float, ...]
    new_edges: tuple[float, ...]


def _decile_buckets(
    values: pd.Series, *, n_bins: int
) -> tuple[pd.Series, tuple[float, ...]]:
    """Bucket values into distinct sentinels, quantiles, and missing.

    Repeated quantile boundaries are intentionally retained. This keeps the
    D01..D10 coordinate system stable while allowing empty deciles for
    discrete/zero-inflated features instead of arbitrarily splitting ties.
    """

    numeric = pd.to_numeric(values, errors="coerce")
    labels = [f"D{i:02d}" for i in range(1, n_bins + 1)]
    sentinel_values = sorted(numeric[numeric < 0].dropna().unique().tolist())
    sentinel_labels = [sentinel_bucket_label(value) for value in sentinel_values]
    categories = [*sentinel_labels, *labels, MISSING_BUCKET]
    bucket = pd.Series(MISSING_BUCKET, index=values.index, dtype="object")
    negative = numeric < 0
    bucket.loc[negative] = numeric.loc[negative].map(sentinel_bucket_label)

    finite_nonnegative = numeric[(numeric >= 0) & np.isfinite(numeric)]
    if finite_nonnegative.empty:
        edges: tuple[float, ...] = ()
    else:
        raw_edges = np.quantile(
            finite_nonnegative.to_numpy(dtype=float),
            np.linspace(0.0, 1.0, n_bins + 1),
        )
        edges = tuple(float(value) for value in raw_edges)
        nonnegative = numeric >= 0
        finite = nonnegative & np.isfinite(numeric)
        codes = np.searchsorted(raw_edges[1:-1], numeric.loc[finite], side="left")
        bucket.loc[finite] = [labels[int(code)] for code in codes]
        bucket.loc[nonnegative & np.isposinf(numeric)] = labels[-1]

    return pd.Series(
        pd.Categorical(bucket, categories=categories, ordered=True),
        index=values.index,
    ), edges


def feature_migration_matrices(
    df: pd.DataFrame,
    *,
    features: Sequence[str],
    ste_suffix: str = "_ste",
    n_bins: int = 10,
) -> dict[str, FeatureMigrationMatrix]:
    """Old-feature x new-feature population counts for every feature.

    Old and new decile boundaries are fitted independently using values >= 0.
    Every distinct negative value gets its own sentinel bucket. Missing values
    are counted separately so every matrix sums to the input population size.
    """

    if n_bins < 1:
        raise ValueError("n_bins must be at least 1")

    results: dict[str, FeatureMigrationMatrix] = {}
    for feature in features:
        new_feature = f"{feature}{ste_suffix}"
        missing = [col for col in (feature, new_feature) if col not in df.columns]
        if missing:
            raise KeyError(f"Feature migration columns not found: {missing}")

        old_bucket, old_edges = _decile_buckets(df[feature], n_bins=n_bins)
        new_bucket, new_edges = _decile_buckets(df[new_feature], n_bins=n_bins)
        old_categories = old_bucket.cat.categories.tolist()
        new_categories = new_bucket.cat.categories.tolist()
        matrix = pd.crosstab(old_bucket, new_bucket, dropna=False).reindex(
            index=old_categories, columns=new_categories, fill_value=0
        )
        matrix = matrix.astype("int64")
        matrix.index.name = f"{feature}_old"
        matrix.columns.name = f"{feature}_new"
        results[feature] = FeatureMigrationMatrix(
            feature=feature,
            matrix=matrix,
            old_edges=old_edges,
            new_edges=new_edges,
        )
    return results


def population_frame(
    df: pd.DataFrame, *, target_col: str | None, flag_col: str | None
) -> pd.DataFrame:
    """Subset ``df`` to a population.

    Mirrors the notebooks: contratos Itaú = rows with non-null target
    (``ctrt_itau = where(target.isna(), 0, 1)``), or a contract flag == 1 when
    no target is available (recent reference). Base population = all rows.
    """

    if target_col and target_col in df.columns:
        return df[df[target_col].notna()]
    if flag_col and flag_col in df.columns:
        return df[df[flag_col] == 1]
    return df
