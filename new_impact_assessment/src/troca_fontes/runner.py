"""Orchestration: experiment -> extract -> prepare -> analyse -> workbook."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import pandas as pd

from . import analyses
from .config import (
    ConfigBundle,
    ExperimentConfig,
    ModelConfig,
    SegmentationSpec,
    resolve_segmentation,
)
from .connections import Connections
from .extraction import Extractor
from .feature_resolution import (
    all_substituted_features,
    feature_importances,
    resolve,
)
from .preparation import NEW_GH_COL, NEW_SCORE_COL, STE_SUFFIX, build_eval_frame
from .query_loader import QueryLoader
from .report import workbook as wb


def analyse_reference(
    eval_df: pd.DataFrame,
    *,
    model: ModelConfig,
    experiment: ExperimentConfig,
    include_target: bool,
    features: Sequence[str],
    importances,
    segmentation: SegmentationSpec | None,
) -> dict:
    """Run configured analyses against an already prepared evaluation frame.

    This public in-memory entry point is useful for notebooks, tests, and data
    sources that do not use the framework's production extraction layer.
    """

    segment_col = segmentation.normalized_column if segmentation else None
    segments = analyses.segment_labels(
        eval_df,
        segment_col,
        configured_values=segmentation.values if segmentation else (),
        include_null=segmentation.include_null if segmentation else False,
    )
    match, drift, gh_migration, feature_migration = {}, {}, {}, {}
    for pop_key in experiment.populations:
        pop = model.population(pop_key)
        frame = analyses.population_frame(
            eval_df, target_col=pop.target_col, flag_col=pop.flag_col
        )
        match[pop_key] = analyses.score_gh_match(
            frame,
            score_col=model.score_col,
            new_score_col=NEW_SCORE_COL,
            gh_col=model.gh_col,
            new_gh_col=NEW_GH_COL,
            segmentation_col=segment_col,
            segments=segments,
        )
        if "per_variable_drift" in experiment.analyses:
            drift[pop_key] = analyses.variable_drift(
                frame,
                features=features,
                ste_suffix=STE_SUFFIX,
                segmentation_col=segment_col,
                importances=importances,
                segments=segments,
            )
        if (
            "gh_migration_matrix" in experiment.analyses
            or "migration_matrix" in experiment.analyses
        ):
            gh_migration[pop_key] = {
                seg: analyses.migration_matrix(
                    frame[analyses._segment_mask(frame, segment_col, seg)],
                    gh_col=model.gh_col,
                    new_gh_col=NEW_GH_COL,
                )
                for seg in segments
            }
        if "feature_migration_matrix" in experiment.analyses:
            feature_migration[pop_key] = {
                seg: analyses.feature_migration_matrices(
                    frame[analyses._segment_mask(frame, segment_col, seg)],
                    features=features,
                    ste_suffix=STE_SUFFIX,
                )
                for seg in segments
            }

    performance = None
    target_population = next(
        (model.population(key) for key in experiment.populations
         if model.population(key).target_col),
        None,
    )
    if (
        "performance_gini" in experiment.analyses
        and include_target
        and target_population is not None
    ):
        contr = target_population
        frame = analyses.population_frame(
            eval_df, target_col=contr.target_col, flag_col=contr.flag_col
        )
        performance = analyses.performance(
            frame,
            target_col=contr.target_col,
            score_col=model.score_col,
            new_score_col=NEW_SCORE_COL,
            segmentation_col=segment_col,
            segments=segments,
        )
    return {
        "match": match,
        "drift": drift if "per_variable_drift" in experiment.analyses else None,
        "performance": performance,
        "gh_migration": gh_migration or None,
        "feature_migration": feature_migration or None,
        "segments": segments,
    }


# Compatibility for code written against the initially recovered private name.
_analyse_reference = analyse_reference


def _volumetria_counts(
    eval_df, model, populations, *, segmentation_col, segments
) -> dict:
    counts = {}
    for pop_key in populations:
        pop = model.population(pop_key)
        frame = analyses.population_frame(
            eval_df, target_col=pop.target_col, flag_col=pop.flag_col
        )
        for seg in segments:
            mask = analyses._segment_mask(frame, segmentation_col, seg)
            counts[(pop_key, seg)] = int(mask.sum())
    return counts


def run_experiment(
    experiment: ExperimentConfig,
    bundle: ConfigBundle,
    *,
    cache_dir: str | Path,
    refresh: bool = False,
    connections: Connections | None = None,
) -> wb.SheetReport:
    model = bundle.models[experiment.model]
    migrations = [bundle.migrations[m] for m in experiment.migrations]
    segmentation = resolve_segmentation(
        migrations, legacy_column=model.platform_col
    )
    segment_col = segmentation.normalized_column if segmentation else None
    resolved = resolve(model, migrations)
    features = all_substituted_features(resolved)
    features_by_migration = {
        r.migration.name: list(r.features) for r in resolved
    }
    importances = feature_importances(model).to_dict()

    extractor = Extractor(
        conn=connections or Connections(),
        loader=QueryLoader(),
        cache_dir=Path(cache_dir),
        refresh=refresh,
    )

    ref_reports, all_counts = [], {}
    for ref in experiment.references:
        data = extractor.reference_data(
            model, migrations, ref, features_by_migration
        )
        target_population = next(
            (model.population(key) for key in experiment.populations
             if model.population(key).target_col),
            None,
        )
        eval_df = build_eval_frame(
            data.flat,
            data.new_features,
            model=model,
            substituted=features,
            join_cols=model.id_cols,
            target=data.target,
            target_col=(
                target_population.target_col
                if ref.include_target and target_population is not None
                else None
            ),
            segmentation_col=segment_col,
        )
        blocks = analyse_reference(
            eval_df,
            model=model,
            experiment=experiment,
            include_target=ref.include_target,
            features=features,
            importances=importances,
            segmentation=segmentation,
        )
        ref_reports.append(
            wb.ReferenceReport(
                banner=f"ANÁLISES - REF {ref.key.upper()}",
                match=blocks["match"],
                performance=blocks["performance"],
                drift=blocks["drift"],
                gh_migration=blocks["gh_migration"],
                feature_migration=blocks["feature_migration"],
                segments=blocks["segments"],
            )
        )
        for (pop_key, seg), val in _volumetria_counts(
            eval_df,
            model,
            experiment.populations,
            segmentation_col=segment_col,
            segments=blocks["segments"],
        ).items():
            all_counts[(pop_key, ref.key, seg)] = val

    groups = [
        (p, model.population(p).display_name) for p in experiment.populations
    ]
    volumetrias = {
        "groups": groups,
        "ref_keys": [r.key for r in experiment.references],
        "counts": all_counts,
        "segments": list(
            dict.fromkeys(
                seg
                for report in ref_reports
                for seg in report.segments
            )
        ),
        "segmentation_name": (
            segmentation.display_name or segmentation.column
            if segmentation
            else None
        ),
    }
    meta = {**model.metadata, **experiment.metadata}
    book_display = " + ".join(m.display_name for m in migrations)
    return wb.SheetReport(
        sheet_name=experiment.report_sheet,
        model_display=model.display_name,
        book_display=book_display,
        publicos=meta.get("publicos", [f"- {lbl}" for _, lbl in groups]),
        referencias=meta.get(
            "referencias", [r.label for r in experiment.references]
        ),
        ref_labels=[f"REF {r.key.upper()}" for r in experiment.references],
        volumetrias=volumetrias,
        notes=meta.get("observacoes", []),
        features=features,
        references=ref_reports,
    )


def run(
    experiment_names: Sequence[str],
    configs_dir: str | Path,
    *,
    output: str | Path,
    cache_dir: str | Path,
    refresh: bool = False,
) -> Path:
    from .config import load_configs

    bundle = load_configs(configs_dir)
    reports = [
        run_experiment(
            bundle.experiments[name],
            bundle,
            cache_dir=cache_dir,
            refresh=refresh,
        )
        for name in experiment_names
    ]
    workbook = wb.build_workbook(reports)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output)
    return output
