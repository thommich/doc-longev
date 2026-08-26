from __future__ import annotations

from troca_fontes.query_loader import QueryLoader


def test_new_source_template_allows_any_or_no_segmentation_column():
    loader = QueryLoader()
    kwargs = {
        "out_table": "db.output",
        "ideq3_table": "db.keys",
        "new_source_table": "db.source",
        "features": ["FEATURE_X"],
    }

    with_segment = loader.get(
        "athena/new_source_nearest_date.sql.j2",
        **kwargs,
        segmentation_col="CHANNEL",
    )
    without_segment = loader.get(
        "athena/new_source_nearest_date.sql.j2",
        **kwargs,
        segmentation_col=None,
    )

    assert "B.CHANNEL" in with_segment
    assert ",CHANNEL\nFROM ranked_joins" in with_segment
    assert "CHANNEL" not in without_segment
