import pytest
import pandas as pd
import numpy as np
from legacy.visualizer import clean_numeric_col, map_and_expand_countries, COUNTRY_TO_ISO, EUROZONE_ISOS

def test_clean_numeric_col():
    # Test typical percent strings
    assert clean_numeric_col(pd.Series(["0.25%"])).iloc[0] == 0.25
    assert clean_numeric_col(pd.Series(["2,400.5%"])).iloc[0] == 2400.5
    
    # Test currency formatting
    assert clean_numeric_col(pd.Series(["$123.45"])).iloc[0] == 123.45
    
    # Test string with whitespace
    assert clean_numeric_col(pd.Series(["  4.5  "])).iloc[0] == 4.5
    
    # Test None / NaN inputs
    assert np.isnan(clean_numeric_col(pd.Series([None])).iloc[0])
    assert np.isnan(clean_numeric_col(pd.Series(["invalid"])).iloc[0])

def test_map_and_expand_countries_standard():
    # Test standard mapping
    df = pd.DataFrame([
        {"Country": "United States", "Last": "4.5", "Previous": "4.5"},
        {"Country": "Japan", "Last": "0.5", "Previous": "0.5"}
    ])
    mapped = map_and_expand_countries(df)
    
    assert len(mapped) == 2
    assert mapped.iloc[0]["ISO3"] == "USA"
    assert mapped.iloc[0]["Country"] == "United States"
    assert mapped.iloc[1]["ISO3"] == "JPN"
    assert mapped.iloc[1]["Country"] == "Japan"

def test_map_and_expand_countries_euro_zone():
    # Test Euro Area expansion
    df = pd.DataFrame([
        {"Country": "Euro Area", "Last": "2.4", "Previous": "2.65"}
    ])
    mapped = map_and_expand_countries(df)
    
    # It should expand to all eurozone countries
    assert len(mapped) == len(EUROZONE_ISOS)
    assert set(mapped["ISO3"]) == set(EUROZONE_ISOS)
    
    # Check that it retained values
    for _, row in mapped.iterrows():
        assert row["Last"] == "2.4"
        assert row["Previous"] == "2.65"
        assert "Euro Area" in row["Country"]

def test_map_and_expand_countries_unknown():
    # Test unknown country fallback
    df = pd.DataFrame([
        {"Country": "Atlantis", "Last": "1.0", "Previous": "1.0"}
    ])
    mapped = map_and_expand_countries(df)
    
    assert len(mapped) == 1
    assert mapped.iloc[0]["ISO3"] is None
    assert mapped.iloc[0]["Country"] == "Atlantis"
