"""CSV formatting utilities for MCP tool output."""

import csv
import io
from typing import Any, Sequence


def to_csv(rows: Sequence[dict[str, Any]], columns: list[str] | None = None) -> str:
    """Convert a list of dictionaries to CSV string.

    Args:
        rows: List of row dictionaries
        columns: Optional list of column names to include (in order).
                 If None, uses keys from first row.

    Returns:
        CSV formatted string with headers
    """
    if not rows:
        return ""

    output = io.StringIO()

    # Determine columns
    if columns is None:
        columns = list(rows[0].keys())

    writer = csv.DictWriter(
        output,
        fieldnames=columns,
        quoting=csv.QUOTE_ALL,
        extrasaction="ignore",
    )
    writer.writeheader()

    for row in rows:
        writer.writerow(row)

    return output.getvalue()


def cursor_to_rows(cursor, column_names: list[str] | None = None) -> list[dict[str, Any]]:
    """Convert a database cursor to a list of dictionaries.

    Args:
        cursor: Database cursor with results
        column_names: Optional override for column names.
                      If None, uses cursor.description.

    Returns:
        List of row dictionaries
    """
    if column_names is None:
        column_names = [desc[0] for desc in cursor.description]

    rows = []
    for row in cursor:
        row_dict = {}
        for i, value in enumerate(row):
            row_dict[column_names[i]] = value
        rows.append(row_dict)

    return rows


def cursor_to_csv(cursor, column_mapping: list[tuple[str, str]] | None = None) -> str:
    """Convert a database cursor directly to CSV string.

    Args:
        cursor: Database cursor with results
        column_mapping: Optional list of (db_column, display_name) tuples.
                        If None, uses cursor column names as-is.

    Returns:
        CSV formatted string with headers
    """
    if column_mapping:
        db_columns = [m[0] for m in column_mapping]
        display_names = [m[1] for m in column_mapping]
        rows = cursor_to_rows(cursor, db_columns)
        # Rename columns for display
        renamed_rows = []
        for row in rows:
            renamed = {}
            for db_col, display_name in column_mapping:
                renamed[display_name] = row.get(db_col)
            renamed_rows.append(renamed)
        return to_csv(renamed_rows, display_names)
    else:
        rows = cursor_to_rows(cursor)
        return to_csv(rows)
