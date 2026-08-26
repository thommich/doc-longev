"""Thin Jinja2 SQL template loader.

Mirrors the ``meridiancrediariobordo.utils.QueryLoader`` pattern: templates live
under ``templates/<engine>/<name>.sql.j2`` and are rendered with keyword args.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined


_DEFAULT_TEMPLATES = Path(__file__).resolve().parents[2] / "templates"


class QueryLoader:
    def __init__(self, templates_dir: str | Path | None = None) -> None:
        base = Path(templates_dir) if templates_dir else _DEFAULT_TEMPLATES
        self._env = Environment(
            loader=FileSystemLoader(str(base)),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def get(self, path: str, **kwargs) -> str:
        """Render ``templates/<path>`` (e.g. ``athena/ideq3_mapping.sql.j2``)."""

        return self._env.get_template(path).render(**kwargs)
