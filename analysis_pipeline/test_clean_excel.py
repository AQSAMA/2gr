import sys
from unittest.mock import MagicMock
import pytest

# Mock pandas and numpy if not available to allow testing the core logic
# of normalize_text without heavy environment setup.
try:
    import pandas as pd
    import numpy as np
except ImportError:
    pd = MagicMock()
    np = MagicMock()
    sys.modules["pandas"] = pd
    sys.modules["numpy"] = np

    # Simple implementations for testing normalize_text logic
    def isna(val):
        if val is None:
            return True
        if isinstance(val, float) and str(val) == "nan":
            return True
        return False

    pd.isna = isna
    # Use a unique object for NaN to make 'is' tests reliable in mock environment
    class MockNaN:
        def __repr__(self): return "nan"
    mock_nan = MockNaN()
    np.nan = mock_nan

from clean_excel import normalize_text

def test_normalize_text_zero_width_characters():
    """Verify that zero-width characters and non-breaking spaces are removed."""
    # \u200f is Right-to-Left Mark
    # \u200e is Left-to-Right Mark
    # \u200c is Zero Width Non-Joiner
    # \xa0 is Non-breaking space

    # Simple cases
    assert normalize_text("test\u200f") == "test"
    assert normalize_text("\u200etest") == "test"
    assert normalize_text("test\u200c") == "test"
    assert normalize_text("test\xa0") == "test"

    # Combination and whitespace handling
    assert normalize_text("test\u200f ") == "test"
    assert normalize_text("\u200f \u200e test \u200c \xa0") == "test"
    assert normalize_text("Arabic\u200fText") == "ArabicText"

def test_normalize_text_whitespace():
    """Verify that multiple whitespaces are collapsed and strings are stripped."""
    assert normalize_text("  test  ") == "test"
    assert normalize_text("multiple    spaces") == "multiple spaces"
    assert normalize_text("\t tab \n newline ") == "tab newline"
    assert normalize_text("word1\r\nword2") == "word1 word2"

def test_normalize_text_nan_strings():
    """Verify that strings representing 'null' are converted to np.nan."""
    import numpy as np
    # These should all return the np.nan object
    assert normalize_text("nan") is np.nan
    assert normalize_text("None") is np.nan
    assert normalize_text("null") is np.nan
    assert normalize_text("NULL") is np.nan
    assert normalize_text("") is np.nan
    assert normalize_text("   ") is np.nan  # Strips to empty string then returns np.nan

def test_normalize_text_actual_nan():
    """Verify that actual NaN/None inputs return np.nan."""
    import numpy as np
    assert normalize_text(None) is np.nan
    assert normalize_text(np.nan) is np.nan

def test_normalize_text_normal_string():
    """Verify that normal strings and numbers are handled correctly."""
    assert normalize_text("Normal Text") == "Normal Text"
    assert normalize_text("  Mixed CASE  ") == "Mixed CASE"
    assert normalize_text(123) == "123"
    assert normalize_text(45.6) == "45.6"

def test_normalize_text_keep_some_special_chars():
    """Verify it doesn't over-clean other special characters."""
    assert normalize_text("test-parameters") == "test-parameters"
    assert normalize_text("email@example.com") == "email@example.com"
    assert normalize_text("100%") == "100%"
