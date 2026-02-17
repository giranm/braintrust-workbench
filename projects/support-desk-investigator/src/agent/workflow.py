"""Investigation workflow implementation.

Four-phase workflow:
1. Triage - Analyze ticket priority and categorize issue type
2. Gather - Collect evidence from logs, incidents, deployments, customer data
3. Verify - Cross-reference evidence and validate hypotheses
4. Finalize - Generate customer reply and internal notes
"""

import logging
from datetime import datetime
from typing import Optional

from anthropic import Anthropic
from src.common.schemas import (
    CaseFile,
    InvestigationResult,
    Evidence,
    Action,
    ActionType,
)
from src.agent.tools import ToolClient

logger = logging.getLogger(__name__)


class InvestigationWorkflow:
    """Multi-phase investigation workflow for support tickets."""

    def __init__(
        self,
        backend_url: str,
        anthropic_api_key: Optional[str] = None,
        variant: str = "baseline",
    ):
        self.tool_client = ToolClient(backend_url)
        self.anthropic = Anthropic(api_key=anthropic_api_key) if anthropic_api_key else None
        self.variant = variant
        logger.info(f"🤖 Initialized investigation workflow (variant={variant})")

    async def investigate(
        self, case_file: CaseFile
    ) -> InvestigationResult:
        """Run full investigation workflow on a support ticket.

        Args:
            case_file: Normalized ticket data

        Returns:
            Investigation result with customer reply, internal notes, evidence, actions
        """
        start_time = datetime.now()
        logger.info(f"🔍 Starting investigation for ticket {case_file.ticket_id}")

        try:
            # Phase 1: Triage
            triage_result = await self._phase_triage(case_file)
            logger.info(f"✅ Triage complete: {triage_result['category']}")

            # Phase 2: Gather evidence
            evidence = await self._phase_gather(case_file, triage_result)
            logger.info(f"✅ Gathered {len(evidence)} pieces of evidence")

            # Phase 3: Verify and analyze
            analysis = await self._phase_verify(case_file, evidence)
            logger.info(f"✅ Verification complete (confidence={analysis['confidence']})")

            # Phase 4: Finalize response
            result = await self._phase_finalize(case_file, evidence, analysis)

            elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            result.investigation_time_ms = elapsed_ms

            logger.info(f"✅ Investigation complete in {elapsed_ms}ms")
            return result

        except Exception as e:
            logger.error(f"❌ Investigation failed: {e}", exc_info=True)
            # Return a fallback result
            return InvestigationResult(
                ticket_id=case_file.ticket_id,
                customer_reply="Thank you for contacting support. We're investigating your issue and will respond shortly.",
                internal_notes=f"Investigation failed: {str(e)}",
                evidence=[],
                actions=[Action(
                    type=ActionType.ESCALATE,
                    reason="Automated investigation failed",
                    metadata={"error": str(e)}
                )],
                confidence=0.0,
                should_escalate=True,
            )

    async def _phase_triage(self, case_file: CaseFile) -> dict:
        """Phase 1: Triage - Categorize and prioritize the ticket.

        Determines:
        - Issue category (error, request, question, incident)
        - Severity assessment
        - Required tools for investigation
        """
        logger.info("📋 Phase 1: Triage")

        # Get full ticket details
        ticket_details = await self.tool_client.get_ticket(case_file.ticket_id)

        # Simple keyword-based categorization for baseline
        description_lower = case_file.description.lower()
        subject_lower = case_file.subject.lower()
        combined = f"{subject_lower} {description_lower}"

        # Detect issue category
        if any(kw in combined for kw in ["error", "502", "500", "503", "timeout", "crash", "failed"]):
            category = "error"
            requires_logs = True
        elif any(kw in combined for kw in ["request", "can you", "could you", "please add", "enable"]):
            category = "request"
            requires_logs = False
        elif any(kw in combined for kw in ["how to", "how do", "question", "what is", "explain"]):
            category = "question"
            requires_logs = False
        else:
            category = "incident"
            requires_logs = True

        return {
            "category": category,
            "requires_logs": requires_logs,
            "requires_incidents": category in ["error", "incident"],
            "requires_deploys": category in ["error", "incident"],
            "severity": case_file.priority,
        }

    async def _phase_gather(self, case_file: CaseFile, triage: dict) -> list[Evidence]:
        """Phase 2: Gather - Collect evidence from various sources.

        Uses tool client to:
        - Query logs for errors
        - Search similar incidents
        - Check recent deployments
        - Fetch customer information
        """
        logger.info("📦 Phase 2: Gather")

        evidence = []

        # Always get customer info if available
        if case_file.customer_id:
            customer_data = await self.tool_client.get_customer(case_file.customer_id)
            evidence.append(Evidence(
                source="customer_profile",
                content=f"Customer: {customer_data.get('name', 'Unknown')} ({customer_data.get('tier', 'standard')})",
                confidence=1.0,
                timestamp=datetime.now(),
            ))

        # Gather based on triage
        if triage["requires_logs"]:
            # Query logs for error patterns
            query = case_file.subject
            logs = await self.tool_client.query_logs(query=query, limit=10)
            if logs:
                evidence.append(Evidence(
                    source="logs",
                    content=f"Found {len(logs)} log entries matching '{query}'",
                    confidence=0.8,
                    timestamp=datetime.now(),
                    metadata={"count": len(logs), "query": query},
                ))

        if triage["requires_incidents"]:
            # Search for similar past incidents
            incidents = await self.tool_client.search_incidents(
                query=case_file.subject,
                limit=5
            )
            if incidents:
                evidence.append(Evidence(
                    source="similar_incidents",
                    content=f"Found {len(incidents)} similar incidents",
                    confidence=0.7,
                    timestamp=datetime.now(),
                    metadata={"count": len(incidents)},
                ))

        if triage["requires_deploys"]:
            # Check recent deployments
            deploys = await self.tool_client.get_recent_deploys(hours=24)
            if deploys:
                evidence.append(Evidence(
                    source="deployments",
                    content=f"Found {len(deploys)} deployments in last 24h",
                    confidence=0.6,
                    timestamp=datetime.now(),
                    metadata={"count": len(deploys)},
                ))

        return evidence

    async def _phase_verify(self, case_file: CaseFile, evidence: list[Evidence]) -> dict:
        """Phase 3: Verify - Analyze evidence and determine root cause.

        Cross-references evidence and validates hypotheses.
        For baseline variant: simple rule-based verification.
        For improved variant: LLM-based analysis.
        """
        logger.info("🔬 Phase 3: Verify")

        # Baseline: Simple rule-based verification
        has_logs = any(e.source == "logs" for e in evidence)
        has_incidents = any(e.source == "similar_incidents" for e in evidence)
        has_deploys = any(e.source == "deployments" for e in evidence)

        # Calculate confidence score
        confidence = 0.5  # Base confidence
        if has_logs:
            confidence += 0.2
        if has_incidents:
            confidence += 0.2
        if has_deploys:
            confidence += 0.1

        # Determine if we have enough information
        should_escalate = confidence < 0.6 or case_file.priority == "Urgent"

        return {
            "confidence": confidence,
            "has_sufficient_evidence": confidence >= 0.6,
            "should_escalate": should_escalate,
            "root_cause_hypothesis": "Investigation in progress" if confidence < 0.8 else "Likely deployment-related issue",
        }

    async def _phase_finalize(
        self,
        case_file: CaseFile,
        evidence: list[Evidence],
        analysis: dict,
    ) -> InvestigationResult:
        """Phase 4: Finalize - Generate customer reply and internal notes.

        Creates structured output with:
        - Customer-facing reply
        - Internal investigation notes
        - Recommended actions
        """
        logger.info("📝 Phase 4: Finalize")

        # Baseline: Template-based response
        if analysis["should_escalate"]:
            customer_reply = (
                f"Thank you for reporting this issue with {case_file.subject}. "
                "We're actively investigating and will update you shortly. "
                "This ticket has been escalated to our engineering team for priority attention."
            )
            internal_notes = (
                f"Automated investigation completed.\n"
                f"Confidence: {analysis['confidence']:.0%}\n"
                f"Evidence collected: {len(evidence)} sources\n"
                f"Recommendation: Escalate for human review"
            )
            actions = [
                Action(
                    type=ActionType.ESCALATE,
                    reason=f"Low confidence ({analysis['confidence']:.0%}) or urgent priority",
                    metadata={"confidence": analysis["confidence"]},
                )
            ]
        else:
            customer_reply = (
                f"Thank you for contacting support regarding {case_file.subject}. "
                f"We've investigated this issue and identified {len(evidence)} relevant data points. "
                "Our team is preparing a detailed response and will follow up shortly."
            )
            internal_notes = (
                f"Automated investigation completed.\n"
                f"Confidence: {analysis['confidence']:.0%}\n"
                f"Evidence collected:\n" +
                "\n".join(f"- {e.source}: {e.content}" for e in evidence) +
                f"\n\nRoot cause: {analysis['root_cause_hypothesis']}"
            )
            actions = [
                Action(
                    type=ActionType.REQUEST_INFO,
                    reason="Additional customer context needed",
                    metadata={"suggested_questions": ["Can you provide the exact time this occurred?"]},
                )
            ]

        return InvestigationResult(
            ticket_id=case_file.ticket_id,
            customer_reply=customer_reply,
            internal_notes=internal_notes,
            evidence=evidence,
            actions=actions,
            confidence=analysis["confidence"],
            should_escalate=analysis["should_escalate"],
        )
