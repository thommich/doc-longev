"""CLI entry point for the troca-de-fontes analysis framework.

Examples::

    python run_analysis.py --experiment bordo_faturas
    python run_analysis.py --experiment bordo_faturas bordo_ft_au --refresh
    python run_analysis.py --all --output out/troca_fontes_books.xlsx
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE / "src"))

from troca_fontes.config import load_configs  # noqa: E402
from troca_fontes.runner import run  # noqa: E402


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Feature-source substitution analysis")
    p.add_argument(
        "--experiment",
        "-e",
        nargs="+",
        default=[],
        help="experiment name(s) from configs/experiments.yml",
    )
    p.add_argument("--all", action="store_true", help="run every experiment")
    p.add_argument(
        "--configs", default=str(_HERE / "configs"), help="configs directory"
    )
    p.add_argument(
        "--output",
        "-o",
        default=str(_HERE / "out" / "troca_fontes_books.xlsx"),
    )
    p.add_argument("--cache-dir", default=str(_HERE / "cache"))
    p.add_argument(
        "--refresh",
        action="store_true",
        help="re-run extraction instead of using cached parquet",
    )
    args = p.parse_args(argv)

    experiments = args.experiment
    if args.all:
        experiments = list(load_configs(args.configs).experiments)
    if not experiments:
        p.error("provide --experiment NAME ... or --all")

    out = run(
        experiments,
        args.configs,
        output=args.output,
        cache_dir=args.cache_dir,
        refresh=args.refresh,
    )
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
