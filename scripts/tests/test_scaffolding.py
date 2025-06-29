import pytest
from unittest.mock import patch, mock_open
from scaffolding.planner import generate_plan
from scaffolding.builder import (
    create_service_folders,
    create_project_documentation,
    create_starter_configs,
)

def test_generate_plan():
    plan = generate_plan("test idea", ["test stack"])
    assert plan["idea"] == "test idea"
    assert plan["stack"] == ["test stack"]
    assert "project_name" in plan
    assert "epics" in plan

@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open)
def test_create_service_folders(mock_open, mock_makedirs):
    create_service_folders("test-service")
    mock_makedirs.assert_called_once_with("src/test-service/interfaces", exist_ok=True)
    mock_open.assert_called_with("src/test-service/__init__.py", "w")

@patch("builtins.open", new_callable=mock_open)
def test_create_project_documentation(mock_open):
    create_project_documentation()
    mock_open.assert_any_call("README.md", "w")
    mock_open.assert_any_call("ARCHITECTURE.md", "w")

@patch("builtins.open", new_callable=mock_open)
def test_create_starter_configs(mock_open):
    with patch("os.makedirs") as mock_makedirs:
        create_starter_configs()
        mock_open.assert_any_call("Dockerfile", "w")
        mock_open.assert_any_call(".github/workflows/ci.yml", "w")
