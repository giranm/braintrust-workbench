"""
Tests for Support Desk Investigator
"""

import pytest
from unittest.mock import Mock, patch
from src.main import SupportAgent


class TestSupportAgent:
    """Test suite for SupportAgent class."""

    @pytest.fixture
    def agent(self):
        """Create a SupportAgent instance for testing."""
        with patch('src.main.braintrust.init_logger'), \
             patch('src.main.OpenAI'):
            return SupportAgent(model="gpt-4o-mini")

    def test_agent_initialization(self, agent):
        """Test that agent initializes correctly."""
        assert agent.model == "gpt-4o-mini"
        assert agent.client is not None
        assert agent.logger is not None

    def test_system_prompt_generation(self, agent):
        """Test system prompt generation for different categories."""
        # Test billing category
        billing_prompt = agent._build_system_prompt("billing")
        assert "billing" in billing_prompt.lower()
        assert "helpful" in billing_prompt.lower()

        # Test technical category
        technical_prompt = agent._build_system_prompt("technical")
        assert "technical" in technical_prompt.lower()

        # Test general category
        general_prompt = agent._build_system_prompt("general")
        assert "general" in general_prompt.lower()

    @patch('src.main.OpenAI')
    @patch('src.main.braintrust.init_logger')
    def test_generate_response_structure(self, mock_logger, mock_openai):
        """Test that generate_response returns correct structure."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        mock_response.usage = Mock(
            total_tokens=100,
            prompt_tokens=50,
            completion_tokens=50
        )

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Mock Braintrust logger
        mock_span = Mock()
        mock_span.__enter__ = Mock(return_value=mock_span)
        mock_span.__exit__ = Mock(return_value=None)
        mock_logger_instance = Mock()
        mock_logger_instance.span.return_value = mock_span
        mock_logger.return_value = mock_logger_instance

        # Create agent and generate response
        agent = SupportAgent()
        result = agent.generate_response("Test ticket", "general")

        # Verify result structure
        assert "response" in result
        assert "category" in result
        assert "model" in result
        assert "tokens_used" in result
        assert result["category"] == "general"
        assert result["tokens_used"] == 100


class TestEvalScorers:
    """Test suite for evaluation scorers."""

    def test_quality_scorer_import(self):
        """Test that quality scorer can be imported."""
        from src.eval import quality_scorer
        assert callable(quality_scorer)

    def test_empathy_scorer_import(self):
        """Test that empathy scorer can be imported."""
        from src.eval import empathy_scorer
        assert callable(empathy_scorer)

    def test_resolution_scorer_import(self):
        """Test that resolution scorer can be imported."""
        from src.eval import resolution_scorer
        assert callable(resolution_scorer)

    def test_test_dataset_exists(self):
        """Test that test dataset is defined."""
        from src.eval import TEST_DATASET
        assert isinstance(TEST_DATASET, list)
        assert len(TEST_DATASET) > 0
        assert "input" in TEST_DATASET[0]
        assert "category" in TEST_DATASET[0]
        assert "expected" in TEST_DATASET[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
