import pytest
from unittest.mock import MagicMock, patch
from recommendation.stack import TechStackRecommender

@pytest.fixture
def mock_datastore():
    return MagicMock()

@pytest.fixture
def mock_query_model():
    with patch('recommendation.stack.query_model') as mock:
        mock.return_value = [
            {
                "name": "Python FastAPI + React + PostgreSQL",
                "pros": ["Fast development", "Great for APIs", "Scalable"],
                "cons": ["Requires separate frontend/backend teams"],
            }
        ]
        yield mock

@pytest.fixture
def mock_search_duckduckgo():
    with patch('recommendation.stack.search_duckduckgo') as mock:
        mock.return_value = None
        yield mock

def test_recommend(mock_datastore, mock_query_model, mock_search_duckduckgo):
    recommender = TechStackRecommender(mock_datastore)
    with patch('builtins.input', return_value='1'):
        chosen_stack = recommender.recommend("test idea", ["test constraint"])
    assert chosen_stack['name'] == "Python FastAPI + React + PostgreSQL"
    mock_datastore.save.assert_called_once_with("chosen_stack", chosen_stack)
