import pandas as pd
from app import dataset_summary, missing_values, top_rows, correlation_matrix, filter_rows, group_statistics

def sample():
    return pd.DataFrame({
        "name": ["A", "B", "C"],
        "score": [90, 60, 75],
        "group": ["X", "Y", "X"],
        "other": [1, 2, 3],
        "optional": [None, 5, 6],
    })

def test_summary():
    result = dataset_summary(sample())
    assert result["rows"] == 3
    assert result["columns"] == 5

def test_missing_values():
    result = missing_values(sample())
    assert "optional" in result.index

def test_top_rows():
    result = top_rows(sample(), largest=True)
    assert result.iloc[0]["score"] == 90

def test_filter_rows():
    result = filter_rows(sample(), "show rows where score > 70")
    assert len(result) == 2

def test_group_statistics():
    result = group_statistics(sample(), "average score by group")
    assert result is not None
    assert round(result.loc["X"].iloc[0], 1) == 82.5

def test_correlation():
    result = correlation_matrix(sample())
    assert isinstance(result, pd.DataFrame)
    assert "score" in result.columns
