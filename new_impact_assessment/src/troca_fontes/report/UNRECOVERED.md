# Original report package was unrecovered

The screenshots show this directory in the project tree and the visible README
describes it as an "openpyxl v6-dashboard builder". No screenshot opens a file
inside the directory, so its Python implementation cannot be transcribed from
the supplied evidence.

The recovered `runner.py` imports `troca_fontes.report.workbook` and revealed
the interface names `ReferenceReport`, `SheetReport`, and `build_workbook`, but
the original implementation and exact dataclass fields remain unavailable.

`workbook.py` is a post-recovery compatible implementation. It does not claim
to reproduce the unavailable v6 formatting byte-for-byte; it provides summary,
GH migration, and feature migration sheets using the recovered interface.
