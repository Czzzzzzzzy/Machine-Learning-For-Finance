"""Inspect local C2O data files.

Examples
--------
Inspect every supported file in data/:

    python3 inspect_data.py

Inspect one file:

    python3 inspect_data.py --file prices.parquet

Write a markdown report:

    python3 inspect_data.py --save-md outputs/data_inspection.md
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd
import pyarrow.parquet as pq


SUPPORTED_SUFFIXES = {".parquet", ".csv", ".tsv"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect C2O parquet/csv data files.")
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument(
        "--file",
        default=None,
        help="Inspect only one file name, for example prices.parquet.",
    )
    parser.add_argument(
        "--sample-rows",
        type=int,
        default=5,
        help="Number of sample rows to print per file.",
    )
    parser.add_argument(
        "--max-cols",
        type=int,
        default=12,
        help="Maximum number of sample columns to print per file.",
    )
    parser.add_argument(
        "--missing",
        action="store_true",
        help="Also compute missing-value counts. This can be slower for large files.",
    )
    parser.add_argument(
        "--save-md",
        type=Path,
        default=None,
        help="Optional path to save the inspection as markdown.",
    )
    return parser.parse_args()


def human_size(num_bytes: int) -> str:
    value = float(num_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024.0 or unit == "TB":
            return f"{value:.1f}{unit}" if unit != "B" else f"{int(value)}B"
        value /= 1024.0
    return f"{value:.1f}TB"


def iter_data_files(data_dir: Path, file_name: str | None) -> list[Path]:
    if file_name:
        path = data_dir / file_name
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return [path]

    files = [
        path
        for path in data_dir.iterdir()
        if path.is_file()
        and not path.name.startswith("._")
        and path.suffix.lower() in SUPPORTED_SUFFIXES
    ]
    return sorted(files)


def date_like_columns(columns: Iterable[str]) -> list[str]:
    out: list[str] = []
    for column in columns:
        lower = column.lower()
        if "date" in lower or lower in {"updated", "timestamp", "time"}:
            out.append(column)
    return out


def csv_separator(path: Path) -> str:
    return "\t" if path.suffix.lower() == ".tsv" else ","


def parquet_shape_and_schema(path: Path) -> tuple[int, int, list[tuple[str, str]]]:
    parquet = pq.ParquetFile(path)
    schema = parquet.schema_arrow
    fields = [(field.name, str(field.type)) for field in schema]
    return parquet.metadata.num_rows, len(fields), fields


def parquet_sample(path: Path, sample_rows: int) -> pd.DataFrame:
    parquet = pq.ParquetFile(path)
    batches = parquet.iter_batches(batch_size=sample_rows)
    try:
        batch = next(batches)
    except StopIteration:
        return pd.DataFrame()
    return batch.to_pandas().head(sample_rows)


def csv_shape_and_schema(path: Path) -> tuple[int, int, list[tuple[str, str]]]:
    sep = csv_separator(path)
    header = pd.read_csv(path, sep=sep, nrows=0)
    sample = pd.read_csv(path, sep=sep, nrows=1000)
    row_count = 0
    for chunk in pd.read_csv(path, sep=sep, usecols=[header.columns[0]], chunksize=250_000):
        row_count += len(chunk)
    fields = [(column, str(sample[column].dtype)) for column in header.columns]
    return row_count, len(header.columns), fields


def csv_sample(path: Path, sample_rows: int) -> pd.DataFrame:
    return pd.read_csv(path, sep=csv_separator(path), nrows=sample_rows)


def date_ranges(path: Path, fields: list[tuple[str, str]]) -> list[tuple[str, str, str]]:
    columns = date_like_columns([name for name, _ in fields])
    ranges: list[tuple[str, str, str]] = []
    for column in columns:
        try:
            if path.suffix.lower() == ".parquet":
                values = pd.read_parquet(path, columns=[column])[column]
                parsed = pd.to_datetime(values, errors="coerce")
            else:
                parsed_parts = []
                for chunk in pd.read_csv(
                    path,
                    sep=csv_separator(path),
                    usecols=[column],
                    chunksize=250_000,
                ):
                    parsed_parts.append(pd.to_datetime(chunk[column], errors="coerce"))
                parsed = pd.concat(parsed_parts, ignore_index=True) if parsed_parts else pd.Series(dtype="datetime64[ns]")
            parsed = parsed.dropna()
            if not parsed.empty:
                ranges.append((column, str(parsed.min().date()), str(parsed.max().date())))
        except Exception as exc:
            ranges.append((column, "ERROR", str(exc)))
    return ranges


def missing_counts(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        frame = pd.read_parquet(path)
    else:
        frame = pd.read_csv(path, sep=csv_separator(path))
    missing = frame.isna().sum().rename("missing_count").reset_index()
    missing = missing.rename(columns={"index": "column"})
    missing["missing_fraction"] = missing["missing_count"] / len(frame) if len(frame) else 0.0
    return missing.sort_values("missing_count", ascending=False)


def truncate_sample(frame: pd.DataFrame, max_cols: int) -> tuple[pd.DataFrame, int]:
    if len(frame.columns) <= max_cols:
        return frame, 0
    hidden = len(frame.columns) - max_cols
    return frame.iloc[:, :max_cols], hidden


def render_file(
    path: Path,
    sample_rows: int,
    max_cols: int,
    include_missing: bool,
) -> str:
    suffix = path.suffix.lower()
    if suffix == ".parquet":
        rows, cols, fields = parquet_shape_and_schema(path)
        sample = parquet_sample(path, sample_rows)
    elif suffix in {".csv", ".tsv"}:
        rows, cols, fields = csv_shape_and_schema(path)
        sample = csv_sample(path, sample_rows)
    else:
        return f"## {path.name}\n\nUnsupported file type: `{suffix}`\n"

    lines: list[str] = []
    lines.append(f"## {path.name}")
    lines.append("")
    lines.append(f"- Path: `{path}`")
    lines.append(f"- Size: `{human_size(path.stat().st_size)}`")
    lines.append(f"- Shape: `{rows:,} rows x {cols:,} columns`")
    lines.append("")

    ranges = date_ranges(path, fields)
    if ranges:
        lines.append("### Date Ranges")
        lines.append("")
        lines.append("| column | min | max |")
        lines.append("|---|---:|---:|")
        for column, start, end in ranges:
            lines.append(f"| `{column}` | {start} | {end} |")
        lines.append("")

    lines.append("### Columns")
    lines.append("")
    lines.append("| # | column | dtype |")
    lines.append("|---:|---|---|")
    for idx, (column, dtype) in enumerate(fields, start=1):
        lines.append(f"| {idx} | `{column}` | `{dtype}` |")
    lines.append("")

    lines.append("### Sample")
    lines.append("")
    if sample.empty:
        lines.append("_No rows._")
    else:
        shown, hidden = truncate_sample(sample, max_cols)
        lines.append(shown.to_markdown(index=False))
        if hidden:
            lines.append("")
            lines.append(f"_Sample truncated: {hidden} additional columns hidden. Use --max-cols to show more._")
    lines.append("")

    if include_missing:
        lines.append("### Missing Values")
        lines.append("")
        miss = missing_counts(path).head(max_cols)
        lines.append(miss.to_markdown(index=False, floatfmt=".4f"))
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    files = iter_data_files(args.data_dir, args.file)
    if not files:
        raise SystemExit(f"No supported data files found in {args.data_dir}")

    sections = ["# C2O Data Inspection", ""]
    sections.append(
        f"Scanned `{len(files)}` file(s) under `{args.data_dir}`. "
        "Apple resource-fork files beginning with `._` are ignored."
    )
    sections.append("")

    for path in files:
        sections.append(render_file(path, args.sample_rows, args.max_cols, args.missing))

    report = "\n".join(sections).rstrip() + "\n"
    if args.save_md:
        args.save_md.parent.mkdir(parents=True, exist_ok=True)
        args.save_md.write_text(report, encoding="utf-8")
        print(f"Wrote data inspection report to {args.save_md}")
    else:
        print(report)


if __name__ == "__main__":
    main()
