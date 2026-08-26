"""Typed, validated configuration for the feature-source analysis.

Configs live as YAML (``configs/models.yml``, ``configs/migrations.yml``,
``configs/experiments.yml``), one file per type, each keyed by name. They are
parsed into the frozen dataclasses below, which validate their own invariants.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml


# --------------------------------------------------------------------------- #
# Model config
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class TableRef:
    """A physical table/view and the engine that hosts it."""

    engine: str  # "athena" | "teradata"
    name: str

    def __post_init__(self) -> None:
        if self.engine not in ("athena", "teradata"):
            raise ValueError(f"Unknown engine {self.engine!r} for table {self.name!r}")


@dataclass(frozen=True)
class PopulationSpec:
    """One analysis population (e.g. correntistas ativos / contratos Itaú)."""

    key: str
    display_name: str
    # Rows kept for this population. If target_col is set, membership is
    # "target not null"; else if flag_col is set, membership is "flag == 1";
    # else all rows (the base population).
    target_col: str | None = None
    flag_col: str | None = None


@dataclass(frozen=True)
class ModelConfig:
    """Declarative metadata for a scored model (no executable logic)."""

    name: str
    display_name: str
    pkl_path: str
    flat_table: TableRef
    id_cols: tuple[str, ...]
    score_col: str = "score"
    gh_col: str = "gh"
    # Deprecated fallback kept so pre-generalisation model configs still load.
    # New configs should declare segmentation on each migration instead.
    platform_col: str | None = None
    cutpoints_gh: tuple[float, ...] = ()
    aux_cols: tuple[str, ...] = ()
    populations: tuple[PopulationSpec, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def population(self, key: str) -> PopulationSpec:
        for pop in self.populations:
            if pop.key == key:
                return pop
        raise KeyError(f"Population {key!r} not defined for model {self.name!r}")

    def __post_init__(self) -> None:
        if len(self.cutpoints_gh) < 2:
            raise ValueError(
                f"Model {self.name!r}: cutpoints_gh must have >= 2 points"
            )


# --------------------------------------------------------------------------- #
# Migration config
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class NewSourceSpec:
    """The substituting (new) feature source table."""

    engine: str
    table: str
    join_strategy: str = "nearest_date"  # nearest_date | exact
    join_key: str = "pk_riznumdoc_xx"


@dataclass(frozen=True)
class SegmentationSpec:
    """Optional breakdown attached to a migration.

    ``column`` is selected from the migration's new-source table. Unless
    ``values`` pins an order, the analysis discovers the column's unique
    non-null values in each evaluation frame.
    """

    column: str
    display_name: str | None = None
    values: tuple[Any, ...] = ()
    include_null: bool = True

    @property
    def normalized_column(self) -> str:
        return self.column.lower()


@dataclass(frozen=True)
class MigrationConfig:
    """One legacy -> new source substitution, reusable across models."""

    name: str
    display_name: str
    new_source: NewSourceSpec
    feature_suffix: str | None = None
    feature_names: tuple[str, ...] = ()
    segmentation: SegmentationSpec | None = None
    thoth: Mapping[str, Any] | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.feature_suffix and not self.feature_names:
            raise ValueError(
                f"Migration {self.name!r}: set feature_suffix or feature_names"
            )


# --------------------------------------------------------------------------- #
# Experiment config
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class ReferenceSpec:
    """One temporal reference of an experiment (antiga / recente)."""

    key: str
    label: str  # human label, e.g. "REF ANTIGA (10/10/2025)"
    date: str  # ISO date, e.g. "2025-10-10"
    anomesdia: int  # e.g. 20251010
    include_target: bool = False
    parquet: str | None = None  # cached scored flat table location


@dataclass(frozen=True)
class ExperimentConfig:
    """A concrete run = one report sheet."""

    name: str
    model: str
    migrations: tuple[str, ...]
    report_sheet: str
    references: tuple[ReferenceSpec, ...]
    populations: tuple[str, ...]
    analyses: tuple[str, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def reference(self, key: str) -> ReferenceSpec:
        for ref in self.references:
            if ref.key == key:
                return ref
        raise KeyError(f"Reference {key!r} not defined for experiment {self.name!r}")


# --------------------------------------------------------------------------- #
# YAML loaders
# --------------------------------------------------------------------------- #

def _read_yaml(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_models(path: str | Path) -> dict[str, ModelConfig]:
    raw = _read_yaml(path).get("models", {})
    out: dict[str, ModelConfig] = {}
    for name, cfg in raw.items():
        ft = cfg["flat_table"]
        pops = tuple(
            PopulationSpec(
                key=k,
                display_name=(v or {}).get("display_name", k),
                target_col=(v or {}).get("target_col"),
                flag_col=(v or {}).get("flag_col"),
            )
            for k, v in (cfg.get("populations") or {}).items()
        )
        out[name] = ModelConfig(
            name=name,
            display_name=cfg.get("display_name", name),
            pkl_path=cfg["pkl_path"],
            flat_table=TableRef(engine=ft["engine"], name=ft["name"]),
            id_cols=tuple(cfg["id_cols"]),
            score_col=cfg.get("score_col", "score"),
            gh_col=cfg.get("gh_col", "gh"),
            platform_col=cfg.get("platform_col"),
            cutpoints_gh=tuple(cfg.get("cutpoints_gh", [])),
            aux_cols=tuple(cfg.get("aux_cols", [])),
            populations=pops,
            metadata=cfg.get("metadata", {}),
        )
    return out


def load_migrations(path: str | Path) -> dict[str, MigrationConfig]:
    raw = _read_yaml(path).get("migrations", {})
    out: dict[str, MigrationConfig] = {}
    for name, cfg in raw.items():
        ns = cfg["new_source"]
        seg_raw = cfg.get("segmentation")
        # Backward compatibility for recovered configs that put PLATAFORMA
        # under ``new_source.platform_col``.
        if seg_raw is None and ns.get("platform_col"):
            seg_raw = {
                "column": ns["platform_col"],
                "display_name": ns["platform_col"],
            }
        segmentation = None
        if seg_raw:
            segmentation = SegmentationSpec(
                column=seg_raw["column"],
                display_name=seg_raw.get("display_name"),
                values=tuple(seg_raw.get("values", [])),
                include_null=bool(seg_raw.get("include_null", True)),
            )
        out[name] = MigrationConfig(
            name=name,
            display_name=cfg.get("display_name", name),
            new_source=NewSourceSpec(
                engine=ns["engine"],
                table=ns["table"],
                join_strategy=ns.get("join_strategy", "nearest_date"),
                join_key=ns.get("join_key", "pk_riznumdoc_xx"),
            ),
            feature_suffix=cfg.get("feature_suffix"),
            feature_names=tuple(cfg.get("feature_names", [])),
            segmentation=segmentation,
            thoth=cfg.get("thoth"),
            metadata=cfg.get("metadata", {}),
        )
    return out


def load_experiments(path: str | Path) -> dict[str, ExperimentConfig]:
    raw = _read_yaml(path).get("experiments", {})
    out: dict[str, ExperimentConfig] = {}
    for name, cfg in raw.items():
        refs = tuple(
            ReferenceSpec(
                key=k,
                label=(v or {}).get("label", k),
                date=v["date"],
                anomesdia=int(v["anomesdia"]),
                include_target=bool((v or {}).get("include_target", False)),
                parquet=(v or {}).get("parquet"),
            )
            for k, v in (cfg.get("references") or {}).items()
        )
        out[name] = ExperimentConfig(
            name=name,
            model=cfg["model"],
            migrations=tuple(cfg["migrations"]),
            report_sheet=cfg["report_sheet"],
            references=refs,
            populations=tuple(cfg["populations"]),
            analyses=tuple(cfg["analyses"]),
            metadata=cfg.get("metadata", {}),
        )
    return out


@dataclass(frozen=True)
class ConfigBundle:
    models: dict[str, ModelConfig]
    migrations: dict[str, MigrationConfig]
    experiments: dict[str, ExperimentConfig]


def resolve_segmentation(
    migrations: Sequence[MigrationConfig],
    *,
    legacy_column: str | None = None,
) -> SegmentationSpec | None:
    """Return the segmentation shared by an experiment's migrations.

    A combined experiment may reuse the same segmentation (as FATURAS and
    AUTORIZAÇÕES both reuse PLATAFORMA). Different segmentation columns in one
    experiment are ambiguous and therefore rejected explicitly.
    """

    specs = [m.segmentation for m in migrations if m.segmentation is not None]
    if not specs:
        return SegmentationSpec(legacy_column) if legacy_column else None

    columns = {spec.normalized_column for spec in specs}
    if len(columns) != 1:
        details = ", ".join(
            f"{m.name}={m.segmentation.column!r}"
            for m in migrations
            if m.segmentation is not None
        )
        raise ValueError(
            "Migrations in one experiment must use the same segmentation "
            f"column; found {details}"
        )

    first = specs[0]
    for other in specs[1:]:
        if (
            other.values != first.values
            or other.include_null != first.include_null
        ):
            raise ValueError(
                "Migrations sharing a segmentation column must also share its "
                "configured values and include_null setting"
            )
    return first


def load_configs(configs_dir: str | Path) -> ConfigBundle:
    d = Path(configs_dir)
    return ConfigBundle(
        models=load_models(d / "models.yml"),
        migrations=load_migrations(d / "migrations.yml"),
        experiments=load_experiments(d / "experiments.yml"),
    )
