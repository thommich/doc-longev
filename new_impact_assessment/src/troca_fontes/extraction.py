"""Config-driven extraction: render SQL templates and materialise the
per-reference input frames, caching to parquet.

Each reference produces three frames used by :mod:`preparation`:
- ``flat``: scored model flat table (old-source features + score/gh).
- ``new_features``: substituted features recomputed from the new source.
- ``target``: Itaú-contract labels (matured) or contract flag (recent).

Set ``refresh=False`` (default) to reuse cached parquet under ``cache_dir`` and
avoid touching Athena/Teradata. Extraction only runs for missing/stale caches.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import pandas as pd

from .config import MigrationConfig, ModelConfig, ReferenceSpec
from .connections import Connections, drop_if_exists
from .query_loader import QueryLoader


# Default source objects (overridable via model/migration metadata).
TBEQ3 = "DB_CORP_DADOSCADASTRAIS_CADASTROINTERNOMODERNIZADO_SOR_01.TBEQ3_GEST_DOCM_CADA_PESS"
FOUCAULT_CONTRATACAO = "MEBM_V.VDC64151_FOUCAULT_CONTRATACAO"
FOUCAULT_PD_ITAU = "MEBM_V.VDC64171_FOUCAULT_PD_ITAU"
CONTRATACAO_FAMILIAS = ("CRED_CORR_ITAU", "CRED_NCORR_ITAU")
PD_FAMILIAS = ("CRED_CORR", "CRED_NCORR")
WORKSPACE = "workspace_db"


@dataclass
class ReferenceData:
    flat: pd.DataFrame
    new_features: pd.DataFrame
    target: pd.DataFrame | None


@dataclass
class Extractor:
    conn: Connections
    loader: QueryLoader
    cache_dir: Path
    refresh: bool = False

    def _cache(self, name: str) -> Path:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        return self.cache_dir / f"{name}.parquet"

    def _cached(self, name: str, build) -> pd.DataFrame:
        path = self._cache(name)
        if path.exists() and not self.refresh:
            return pd.read_parquet(path)
        df = build()
        df.to_parquet(path, index=False)
        return df

    # -- individual stages --------------------------------------------------

    def flat_table(self, model: ModelConfig, ref: ReferenceSpec) -> pd.DataFrame:
        def build() -> pd.DataFrame:
            if ref.parquet:  # pre-staged scored flat table
                return pd.read_parquet(ref.parquet)
            from build_slim_cast import stream_to_parquet

            sql = self.loader.get(
                "teradata/flat_table_pull.sql.j2",
                flat_table=model.flat_table.name,
                ref_date=ref.date,
            )
            out = self._cache(f"flat_{model.name}_{ref.anomesdia}")
            stream_to_parquet(
                self.conn.teradata,
                sql,
                out_path=str(out),
                float32=True,
                compression="snappy",
            )
            return pd.read_parquet(out)

        df = self._cached(f"flat_{model.name}_{ref.anomesdia}", build)
        df.columns = [c.lower() for c in df.columns]
        if "anomesdia" not in df.columns:
            df["anomesdia"] = ref.anomesdia
        return df

    def new_features(
        self,
        model: ModelConfig,
        migration: MigrationConfig,
        ref: ReferenceSpec,
        features: Sequence[str],
    ) -> pd.DataFrame:
        tag = f"newfeat_{model.name}_{migration.name}_{ref.anomesdia}"

        def build() -> pd.DataFrame:
            athena = self.conn.athena
            ideq3 = f"{WORKSPACE}.TMS_{model.name}_{ref.key}_IDEQ3".upper()
            out_table = (
                f"{WORKSPACE}.TMS_{model.name}_{ref.key}_{migration.name}_STE".upper()
            )
            drop_if_exists(athena, out_table)
            athena.execute(
                self.loader.get(
                    "athena/new_source_nearest_date.sql.j2",
                    out_table=out_table,
                    ideq3_table=ideq3,
                    new_source_table=migration.new_source.table,
                    features=[f.upper() for f in features],
                    segmentation_col=(
                        migration.segmentation.column
                        if migration.segmentation is not None
                        else None
                    ),
                )
            )
            return athena.query(f"SELECT * FROM {out_table}")

        return self._cached(tag, build)

    def contracts(
        self, model: ModelConfig, ref: ReferenceSpec, flat: pd.DataFrame
    ) -> pd.DataFrame | None:
        """Itaú-contract labels for the reference.

        Matured references (``include_target``) get the Foucault performance
        labels (``target_60_m6``); recent references get a contract flag
        (``cntrt_itau``) when a population declares a ``flag_col``.
        """

        if ref.include_target:
            tag = f"target_{model.name}_{ref.anomesdia}"

            def build() -> pd.DataFrame:
                tera = self.conn.teradata
                out_table = f"MES6_T.TMS_PD_ITAU_{ref.key}_{model.name}".upper()
                drop_if_exists(tera, out_table)
                tera.execute(
                    self.loader.get(
                        "teradata/target_itau.sql.j2",
                        out_table=out_table,
                        flat_table=model.flat_table.name,
                        ref_date=ref.date,
                        contratacao_view=FOUCAULT_CONTRATACAO,
                        pd_itau_view=FOUCAULT_PD_ITAU,
                        contratacao_familias=CONTRATACAO_FAMILIAS,
                        pd_familias=PD_FAMILIAS,
                    )
                )
                return tera.query(f"SELECT * FROM {out_table}")

            return self._cached(tag, build)

        # recent reference: build a contract flag if a population needs one
        flag_pop = next((p for p in model.populations if p.flag_col), None)
        contratacao = model.metadata.get("contratacao_recente_table")
        if flag_pop is None or not contratacao:
            return None
        tag = f"contracts_{model.name}_{ref.anomesdia}"

        def build() -> pd.DataFrame:
            athena = self.conn.athena
            keys = f"{WORKSPACE}.TMS_{model.name}_{ref.key}_KEYS".upper()
            out_table = f"{WORKSPACE}.TMS_CNTRT_ITAU_{ref.key}_{model.name}".upper()
            drop_if_exists(athena, out_table)
            athena.upload(
                df=flat[list(model.id_cols)].drop_duplicates().reset_index(drop=True),
                table_name=keys.split(".")[-1].lower(),
                if_exists="overwrite",
            )
            athena.execute(
                self.loader.get(
                    "athena/contratos_itau_recente.sql.j2",
                    out_table=out_table,
                    pub_table=keys,
                    contratacao_table=contratacao,
                    ref_date=ref.date,
                )
            )
            return athena.query(f"SELECT * FROM {out_table}")

        return self._cached(tag, build)

    def reference_data(
        self,
        model: ModelConfig,
        migrations: Sequence[MigrationConfig],
        ref: ReferenceSpec,
        features_by_migration: dict[str, Sequence[str]],
    ) -> ReferenceData:
        flat = self.flat_table(model, ref)
        parts = [
            self.new_features(model, m, ref, features_by_migration[m.name])
            for m in migrations
        ]
        merged = parts[0]
        for extra in parts[1:]:
            merged = merged.merge(
                extra, on=list(model.id_cols), how="outer", suffixes=("", "_dup")
            )
            merged = merged[[c for c in merged.columns if not c.endswith("_dup")]]
        return ReferenceData(
            flat=flat,
            new_features=merged,
            target=self.contracts(model, ref, flat),
        )
