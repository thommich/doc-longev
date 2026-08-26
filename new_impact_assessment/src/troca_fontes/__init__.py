"""Config-driven feature-source substitution ("troca de fontes") analysis."""

from __future__ import annotations

from .config import (
    ConfigBundle,
    ExperimentConfig,
    MigrationConfig,
    ModelConfig,
    SegmentationSpec,
    load_configs,
    load_experiments,
    load_migrations,
    load_models,
)


def run(*args, **kwargs):
    """Lazily import orchestration so analysis-only use stays lightweight."""

    from .runner import run as _run

    return _run(*args, **kwargs)


def run_experiment(*args, **kwargs):
    """Lazily import orchestration so config/analysis imports need no DB stack."""

    from .runner import run_experiment as _run_experiment

    return _run_experiment(*args, **kwargs)


def analyse_reference(*args, **kwargs):
    """Run analyses on an in-memory evaluation frame."""

    from .runner import analyse_reference as _analyse_reference

    return _analyse_reference(*args, **kwargs)

__all__ = [
    "ConfigBundle",
    "ExperimentConfig",
    "MigrationConfig",
    "ModelConfig",
    "SegmentationSpec",
    "load_configs",
    "load_experiments",
    "load_migrations",
    "load_models",
    "run",
    "run_experiment",
    "analyse_reference",
]
