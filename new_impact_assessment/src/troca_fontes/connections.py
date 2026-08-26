"""Infra connections: Athena / S3 / Teradata bootstrap and S3 helpers.

Reuses the repo's existing plumbing (``MLTools.Connections`` and
``app/src/credentials.py:HVACCredentials``). Kept isolated so the analysis and
reporting layers never import infra.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_PARAMS_PATH = _REPO_ROOT / "app/src/meridiancrediariobordo/artifacts/parametros_execucao.yml"


@dataclass
class Connections:
    """Lazily-constructed handles to Athena, S3 and Teradata."""

    env: str = "prod"
    _athena: Any = None
    _s3: Any = None
    _tera: Any = None

    @property
    def athena(self):
        if self._athena is None:
            from MLTools import Connections as mlcon

            self._athena = mlcon.Athena()
        return self._athena

    @property
    def s3(self):
        if self._s3 is None:
            from MLTools import Connections as mlcon

            self._s3 = mlcon.S3()
        return self._s3

    @property
    def teradata(self):
        if self._tera is None:
            from MLTools import Connections as mlcon
            from app.src.credentials import HVACCredentials

            params = yaml.safe_load(open(_PARAMS_PATH))
            vault = params["segredo_vault"][self.env]
            pwd = HVACCredentials(
                role=vault["role"], hvac_path=vault["path"]
            ).get_password(key="password")
            self._tera = mlcon.Teradata(
                user="DC6PARC",
                pwd=pwd,
                env=params["teradata"]["cloud"],
                logmech="102",
            )
        return self._tera


def clear_s3_folder(folder_path: str) -> None:
    import awswrangler as wr

    try:
        arquivos = wr.s3.list_objects(folder_path)
    except Exception:
        arquivos = []
    if arquivos:
        wr.s3.delete_objects(folder_path)


def drop_if_exists(conn, table: str) -> None:
    try:
        conn.execute(f"DROP TABLE {table}")
    except Exception as exc:  # noqa: BLE001 - best-effort drop
        print(f"drop_if_exists({table}) ignored: {exc}")
