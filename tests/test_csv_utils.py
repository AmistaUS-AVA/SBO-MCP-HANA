"""Tests for CSV utilities."""

import pytest
from sap_mcp.csv_utils import to_csv


def test_to_csv_basic():
    """Test basic CSV conversion."""
    rows = [
        {"name": "Alice", "age": "30"},
        {"name": "Bob", "age": "25"},
    ]

    result = to_csv(rows)

    lines = result.strip().split("\n")
    assert len(lines) == 3  # header + 2 rows
    assert '"name"' in lines[0]
    assert '"age"' in lines[0]
    assert '"Alice"' in lines[1]
    assert '"Bob"' in lines[2]


def test_to_csv_with_column_order():
    """Test CSV with explicit column order."""
    rows = [
        {"b": "2", "a": "1", "c": "3"},
    ]

    result = to_csv(rows, columns=["a", "b", "c"])

    lines = result.strip().split("\n")
    # Check column order in header
    assert lines[0] == '"a","b","c"'


def test_to_csv_empty():
    """Test CSV with empty data."""
    result = to_csv([])
    assert result == ""


def test_to_csv_with_quotes():
    """Test CSV with quoted content."""
    rows = [
        {"name": 'Say "Hello"', "value": "test"},
    ]

    result = to_csv(rows)

    # Double quotes should be escaped
    assert '""' in result


def test_to_csv_with_commas():
    """Test CSV with commas in content."""
    rows = [
        {"name": "Smith, John", "value": "test"},
    ]

    result = to_csv(rows)

    # Commas should be inside quoted field
    assert '"Smith, John"' in result
