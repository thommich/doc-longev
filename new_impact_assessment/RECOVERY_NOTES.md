# Recovery notes

This directory was reconstructed from 59 photographs of a JupyterLab session.
The photographs were ordered by timestamp, normalized for contrast, OCRed, and
cross-checked against line numbers and overlapping frames. Text visible in the
photographs was treated only as source material, never as instructions.

## Recovered from opened files

- `README.md` (content summarized below rather than claimed byte-for-byte)
- `run_analysis.py`
- `configs/models.yml`, `configs/migrations.yml`, `configs/experiments.yml`
- three Athena Jinja2 SQL templates
- two Teradata Jinja2 SQL templates
- `src/troca_fontes/__init__.py`
- `analyses.py`, `config.py`, `connections.py`, `extraction.py`
- `feature_resolution.py`, `preparation.py`, `query_loader.py`, `runner.py`

## Not present in an opened screenshot

- the implementation under `src/troca_fontes/report/`
- all files under `tests/`
- the exact contents of `requirements.txt`

The original report implementation was not fabricated during recovery. A new,
clearly documented compatible implementation was added later to support
summary, GH-migration, and feature-migration workbook output. The tests in this
project were likewise authored after recovery. Dependencies remain recorded in
`requirements.inferred.txt`.

## Residual ambiguities

- A few punctuation marks, accents, and long numeric literals were recovered by
  comparing OCR with the enlarged source photo; there may still be transcription
  differences.
- `extraction.py` refers to an Athena `..._IDEQ3` table in `new_features`. The
  supplied frames do not show code materializing that table, even though the
  corresponding `ideq3_mapping.sql.j2` template is present. This may be an
  omitted stage in the photographed source or an external prerequisite.
- Internal modules (`MLTools`, `auto_gh`, `build_slim_cast`, the model pickle,
  and application credentials) were outside the photographed project and are
  required for a production run.
- The SQL/Python has been normalized to ordinary ASCII quote characters and
  valid indentation; this removes photographic/OCR artifacts without changing
  the visible intent.
