import pytest
from unittest.mock import MagicMock
from backend.src.matching import calculate_score, find_best_lender
from backend import create_app
from config import TestingConfig


@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        yield app


# --- calculate_score tests (no app context needed) ---

def test_perfect_match_high():
    assert calculate_score("High", "High") == 3

def test_perfect_match_medium():
    assert calculate_score("Medium", "Medium") == 3

def test_perfect_match_low():
    assert calculate_score("Low", "Low") == 3

def test_worst_match():
    assert calculate_score("High", "Low") == 0

def test_partial_match():
    assert calculate_score("High", "Medium") == 1


# --- find_best_lender tests (need app context) ---

def test_find_best_lender_returns_best_match(app, monkeypatch):
    lender_high = MagicMock()
    lender_high.id = 1
    lender_high.resource_type = "High"

    lender_low = MagicMock()
    lender_low.id = 2
    lender_low.resource_type = "Low"

    mock_query = MagicMock()
    mock_query.filter_by.return_value.filter.return_value.all.return_value = [lender_high, lender_low]
    mock_query.filter_by.return_value.all.return_value = [lender_high, lender_low]

    monkeypatch.setattr("backend.src.matching.Lender.query", mock_query)

    result = find_best_lender("High")
    assert result.resource_type == "High"


def test_find_best_lender_returns_none_when_no_lenders(app, monkeypatch):
    mock_query = MagicMock()
    mock_query.filter_by.return_value.filter.return_value.all.return_value = []
    mock_query.filter_by.return_value.all.return_value = []

    monkeypatch.setattr("backend.src.matching.Lender.query", mock_query)

    result = find_best_lender("High")
    assert result is None


def test_find_best_lender_excludes_declined_lender(app, monkeypatch):
    lender_1 = MagicMock()
    lender_1.id = 1
    lender_1.resource_type = "High"

    lender_2 = MagicMock()
    lender_2.id = 2
    lender_2.resource_type = "Medium"

    mock_query = MagicMock()
    mock_query.filter_by.return_value.filter.return_value.all.return_value = [lender_2]

    monkeypatch.setattr("backend.src.matching.Lender.query", mock_query)

    result = find_best_lender("High", exclude_lender_id=1)
    assert result.id == 2
