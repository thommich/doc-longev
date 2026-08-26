# troca_fontes — feature-source substitution analysis

Config-driven, reusable framework for evaluating the impact of re-sourcing a
model's features from a new data source ("troca de books/fontes"). It holds the
population and model fixed, swaps only the feature source, measures movement in
score, GH (risk band), Gini, and the features themselves, then writes summary
and migration details to an Excel workbook.

## Migration segmentation

Segmentation belongs to a migration, not to a model. It is optional and may use
any column selected from the migration's new-source table:

```yaml
migrations:
  new_book:
    display_name: "NEW BOOK"
    feature_suffix: "_book"
    new_source:
      engine: athena
      table: workspace_db.new_book
    segmentation:
      column: CHANNEL
      display_name: "CANAL"
      # Optional. Omit to discover and sort unique values automatically.
      values: [APP, BRANCH]
      include_null: true
```

If `segmentation` is omitted, analyses produce a TOTAL view only. Migrations
combined in one experiment must declare the same segmentation column and
settings. The recovered `new_source.platform_col` form remains accepted as a
backward-compatible alias.

## Feature migration matrices

Add `feature_migration_matrix` to an experiment's `analyses` list. For every
reference, population, migration segment, and substituted feature, the report
contains an old-bucket x new-bucket count matrix.

- Old and new decile boundaries are fitted independently.
- Only values greater than or equal to zero define the deciles.
- Every distinct negative value receives its own category, such as
  `SENTINEL (-999)`, `SENTINEL (-2)`, or `SENTINEL (-1)`.
- Null/non-numeric values use `MISSING`, so each matrix total reconciles to its
  input population.
- Repeated quantile boundaries are retained. Discrete or zero-inflated
  features can therefore have empty deciles rather than having tied values
  split arbitrarily.

The evaluation frame preserves the production value as `<feature>` and the
new-source value as `<feature>_ste`. Rescoring substitutes `_ste` values while
drift and migration analyses compare both versions.

## Layout

```text
troca_fontes/
├── configs/                  # models.yml, migrations.yml, experiments.yml
├── templates/                # Jinja2 SQL: athena/ and teradata/
├── src/troca_fontes/
│   ├── config.py             # dataclasses + YAML loaders
│   ├── feature_resolution.py # suffix-based features + pickle importances
│   ├── connections.py        # Athena/S3/Teradata bootstrap
│   ├── query_loader.py       # Jinja2 renderer
│   ├── extraction.py         # render/run SQL -> cached parquet
│   ├── preparation.py        # join new source, rescore, assign GH
│   ├── analyses.py           # match, migration, Gini, feature drift
│   ├── report/               # summary + GH/feature migration workbook writer
│   └── runner.py             # orchestration
├── run_analysis.py           # CLI
└── tests/                    # config, analysis, preparation, SQL, report tests
```

## Usage

```bash
python run_analysis.py --experiment bordo_faturas bordo_ft_au
python run_analysis.py --experiment bordo_faturas --refresh
python run_analysis.py --all -o out/troca_fontes_books.xlsx
```

The workbook creates a summary sheet and, when enabled, separate `MIG GH` and
`MIG VAR` detail sheets for each experiment.

## Runnable example notebook

`example_run.ipynb` is an executed, self-contained example using synthetic
data. It defines a model, migration, reference, and experiment; automatically
discovers migration segments; runs score/GH, performance, drift, GH-migration,
and feature-migration analyses; and creates:

```text
example_output/example_migration_report.xlsx
example_output/synthetic_model.joblib
```

Run the notebook with the project root as its working directory. It does not
connect to Athena, Teradata, or internal credential services.

Extraction requires the surrounding repository's HVAC/Teradata setup. When a
reference's `parquet` value is set, the scored flat table is loaded from that
location instead of being streamed from Teradata.

See `RECOVERY_NOTES.md` for evidence boundaries and unrecovered components.
