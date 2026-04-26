"""Tests for mock tool implementations."""

from src.tools.mock_tools import (
    cancel_order,
    get_invoice,
    lookup_order,
    process_refund,
    search_faq,
)


class TestLookupOrder:
    def test_existing_order(self):
        result = lookup_order("12345")
        assert result["order_id"] == "12345"
        assert result["status"] == "in_transit"
        assert result["tracking_url"] is not None

    def test_missing_order(self):
        result = lookup_order("99999")
        assert "error" in result


class TestCancelOrder:
    def test_cancel_processing_order(self):
        result = cancel_order("11111", "changed my mind")
        assert result["success"] is True
        assert result["refund_initiated"] is True

    def test_cancel_shipped_order(self):
        result = cancel_order("12345", "too slow")
        assert result["success"] is False

    def test_cancel_missing_order(self):
        result = cancel_order("99999", "reason")
        assert "error" in result


class TestProcessRefund:
    def test_valid_refund(self):
        result = process_refund("12345", 50.00)
        assert result["success"] is True
        assert result["amount_refunded"] == 50.00
        assert result["reference_number"].startswith("REF-")

    def test_refund_exceeds_total(self):
        result = process_refund("12345", 999.99)
        assert result["success"] is False

    def test_refund_missing_order(self):
        result = process_refund("99999", 10.00)
        assert "error" in result


class TestGetInvoice:
    def test_existing_order(self):
        result = get_invoice("12345")
        assert result["order_id"] == "12345"
        assert result["invoice_url"].endswith(".pdf")
        assert len(result["line_items"]) == 2

    def test_missing_order(self):
        result = get_invoice("99999")
        assert "error" in result


class TestSearchFaq:
    def test_returns_results(self):
        result = search_faq("return policy")
        assert "results" in result
        assert len(result["results"]) <= 3

    def test_returns_max_three(self):
        result = search_faq("shipping international payment")
        assert len(result["results"]) == 3
