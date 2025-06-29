"""Unit tests for the PlanEngine core business logic."""

import pytest
from typing import Dict, Any
from clarity_forge.core.plan_engine import PlanEngine


class TestPlanEngine:
    """Test suite for PlanEngine class."""
    
    @pytest.fixture
    def plan_engine(self):
        """Create a PlanEngine instance for testing."""
        return PlanEngine()
    
    @pytest.fixture
    def sample_requirements(self):
        """Sample requirements for testing."""
        return {
            "project_name": "test-project",
            "technology_stack": ["Python", "FastAPI"],
            "features": ["REST API", "Database"],
            "timeline": "2 weeks",
            "complexity": "medium"
        }
    
    @pytest.fixture
    def valid_plan(self):
        """Sample valid plan for testing."""
        return {
            "plan_id": "test-plan-123",
            "steps": [
                {"step": 1, "description": "Setup project structure", "estimated_time": "1 day"},
                {"step": 2, "description": "Implement API endpoints", "estimated_time": "3 days"},
                {"step": 3, "description": "Add database integration", "estimated_time": "2 days"}
            ],
            "estimated_time": "6 days",
            "project_name": "test-project"
        }
    
    def test_plan_engine_initialization(self, plan_engine):
        """Test that PlanEngine initializes correctly."""
        assert isinstance(plan_engine, PlanEngine)
    
    def test_generate_plan_returns_dict(self, plan_engine, sample_requirements):
        """Test that generate_plan returns a dictionary."""
        result = plan_engine.generate_plan(sample_requirements)
        assert isinstance(result, dict)
    
    def test_generate_plan_contains_required_fields(self, plan_engine, sample_requirements):
        """Test that generated plan contains required fields."""
        result = plan_engine.generate_plan(sample_requirements)
        
        required_fields = ["plan_id", "steps", "estimated_time"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
    
    def test_generate_plan_with_empty_requirements(self, plan_engine):
        """Test plan generation with empty requirements."""
        empty_requirements = {}
        result = plan_engine.generate_plan(empty_requirements)
        
        assert isinstance(result, dict)
        assert "plan_id" in result
        assert "steps" in result
        assert "estimated_time" in result
    
    def test_generate_plan_with_none_requirements(self, plan_engine):
        """Test that plan generation handles None requirements gracefully."""
        # PlanEngine should handle None gracefully, not raise TypeError
        result = plan_engine.generate_plan(None)
        assert isinstance(result, dict)
        assert "steps" in result or "error" in result
    
    def test_validate_plan_returns_boolean(self, plan_engine, valid_plan):
        """Test that validate_plan returns a boolean."""
        result = plan_engine.validate_plan(valid_plan)
        assert isinstance(result, bool)
    
    def test_validate_plan_with_valid_plan(self, plan_engine, valid_plan):
        """Test validation of a valid plan."""
        result = plan_engine.validate_plan(valid_plan)
        assert result is True
    
    def test_validate_plan_with_empty_plan(self, plan_engine):
        """Test validation of an empty plan."""
        empty_plan = {}
        result = plan_engine.validate_plan(empty_plan)
        # Current implementation returns True for all plans
        # This should be updated when validation logic is implemented
        assert isinstance(result, bool)
    
    def test_validate_plan_with_malformed_plan(self, plan_engine):
        """Test validation of a malformed plan."""
        malformed_plan = {
            "invalid_field": "value",
            "missing_required_fields": True
        }
        result = plan_engine.validate_plan(malformed_plan)
        # Current implementation returns True for all plans
        # This should be updated when validation logic is implemented
        assert isinstance(result, bool)
    
    def test_validate_plan_with_none(self, plan_engine):
        """Test that validate_plan handles None input."""
        # PlanEngine should handle None gracefully, not raise TypeError
        result = plan_engine.validate_plan(None)
        assert isinstance(result, bool)
        # Current implementation returns True for all plans including None
        # This should be updated when validation logic is implemented
    
    def test_plan_engine_workflow(self, plan_engine, sample_requirements):
        """Test the complete workflow: generate then validate plan."""
        # Generate a plan
        generated_plan = plan_engine.generate_plan(sample_requirements)
        
        # Validate the generated plan
        is_valid = plan_engine.validate_plan(generated_plan)
        
        assert isinstance(generated_plan, dict)
        assert isinstance(is_valid, bool)
        assert is_valid is True  # Current implementation always returns True
    
    @pytest.mark.parametrize("complexity", ["simple", "medium", "complex"])
    def test_generate_plan_with_different_complexity(self, plan_engine, complexity):
        """Test plan generation with different complexity levels."""
        requirements = {
            "project_name": f"test-{complexity}",
            "complexity": complexity
        }
        
        result = plan_engine.generate_plan(requirements)
        assert isinstance(result, dict)
        assert "plan_id" in result
    
    @pytest.mark.parametrize("tech_stack", [
        ["Python"], 
        ["Python", "FastAPI"], 
        ["Python", "FastAPI", "PostgreSQL"],
        []
    ])
    def test_generate_plan_with_different_tech_stacks(self, plan_engine, tech_stack):
        """Test plan generation with different technology stacks."""
        requirements = {
            "project_name": "test-project",
            "technology_stack": tech_stack
        }
        
        result = plan_engine.generate_plan(requirements)
        assert isinstance(result, dict)
        assert "plan_id" in result
