import pytest
from unittest.mock import patch
from typer.testing import CliRunner
from assistant.main import app

runner = CliRunner()

@patch("assistant.main.run_scaffolding")
@patch("assistant.main.run_conversation")
def test_end_to_end(mock_run_conversation, mock_run_scaffolding):
    mock_run_conversation.return_value = {
        "name": "Python FastAPI + React + PostgreSQL",
        "pros": ["Fast development", "Great for APIs", "Scalable"],
        "cons": ["Requires separate frontend/backend teams"],
    }
    result = runner.invoke(app)
    assert result.exit_code == 0
    mock_run_conversation.assert_called_once()
    mock_run_scaffolding.assert_called_once_with(mock_run_conversation.return_value)
