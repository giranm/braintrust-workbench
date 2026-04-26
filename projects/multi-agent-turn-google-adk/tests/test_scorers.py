"""Tests for Braintrust scorer implementations."""

from src.scorers import routing_accuracy, task_completion, tool_selection


class TestRoutingAccuracy:
    def test_correct_routing(self):
        score = routing_accuracy(
            output="response",
            expected={"agent": "order_agent"},
            metadata={"agent": "order_agent"},
        )
        assert score.score == 1.0

    def test_incorrect_routing(self):
        score = routing_accuracy(
            output="response",
            expected={"agent": "order_agent"},
            metadata={"agent": "faq_agent"},
        )
        assert score.score == 0.0


class TestToolSelection:
    def test_correct_tool(self):
        score = tool_selection(
            output="response",
            expected={"tools": ["lookup_order"]},
            metadata={"tools_called": ["lookup_order"]},
        )
        assert score.score == 1.0

    def test_wrong_tool(self):
        score = tool_selection(
            output="response",
            expected={"tools": ["lookup_order"]},
            metadata={"tools_called": ["search_faq"]},
        )
        assert score.score == 0.0

    def test_partial_match(self):
        score = tool_selection(
            output="response",
            expected={"tools": ["lookup_order", "cancel_order"]},
            metadata={"tools_called": ["lookup_order"]},
        )
        assert score.score == 0.5

    def test_no_tools_expected_none_called(self):
        score = tool_selection(
            output="response",
            expected={"tools": []},
            metadata={"tools_called": []},
        )
        assert score.score == 1.0


class TestTaskCompletion:
    def test_all_terms_present(self):
        score = task_completion(
            output="Order 12345 is in_transit and arriving soon.",
            expected={"must_contain": ["12345", "in_transit"]},
        )
        assert score.score == 1.0

    def test_partial_match(self):
        score = task_completion(
            output="Order 12345 is on its way.",
            expected={"must_contain": ["12345", "in_transit"]},
        )
        assert score.score == 0.5

    def test_no_requirements(self):
        score = task_completion(
            output="anything",
            expected={},
        )
        assert score.score == 1.0
