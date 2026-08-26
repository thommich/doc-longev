from __future__ import annotations

import pytest

from troca_fontes.config import (
    MigrationConfig,
    NewSourceSpec,
    SegmentationSpec,
    load_configs,
    resolve_segmentation,
)


def _migration(name: str, column: str | None) -> MigrationConfig:
    return MigrationConfig(
        name=name,
        display_name=name,
        new_source=NewSourceSpec(engine="athena", table=f"db.{name}"),
        feature_suffix="_x",
        segmentation=SegmentationSpec(column) if column else None,
    )


def test_recovered_migrations_use_migration_owned_segmentation():
    bundle = load_configs("configs")
    migration = bundle.migrations["faturas_ft"]

    assert migration.segmentation is not None
    assert migration.segmentation.normalized_column == "plataforma"
    assert migration.segmentation.values == ("VQ", "NPC", "VQ|NPC")
    assert bundle.models["bordo"].platform_col is None


def test_combined_migrations_must_share_segmentation_column():
    with pytest.raises(ValueError, match="same segmentation column"):
        resolve_segmentation([_migration("one", "CHANNEL"), _migration("two", "REGION")])


def test_migration_can_omit_segmentation():
    assert resolve_segmentation([_migration("plain", None)]) is None

