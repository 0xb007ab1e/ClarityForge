import pytest
from unittest.mock import patch, MagicMock
from ai_engine.model import generate_response, classify

@pytest.fixture
def mock_hf_request():
    with patch('ai_engine.model._hf_request') as mock_request:
        yield mock_request

def test_generate_response(mock_hf_request):
    mock_hf_request.return_value = [{'generated_text': 'test response'}]
    response = generate_response("test context")
    assert response == "test response"

def test_classify(mock_hf_request):
    mock_hf_request.return_value = {'labels': ['tech support', 'billing'], 'scores': [0.9, 0.1]}
    labels = classify("test text")
    assert labels == ["tech support"]
