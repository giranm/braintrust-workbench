"""Agent service - FastAPI application for receiving investigation requests."""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.common.schemas import CaseFile, InvestigationResult
from src.agent.adk_workflow import ADKInvestigationWorkflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global workflow instance
workflow: ADKInvestigationWorkflow = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global workflow

    logger.info("🤖 Agent service starting...")

    # Initialize workflow
    backend_url = os.getenv("BACKEND_URL", "http://backend:8000")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    variant = os.getenv("VARIANT", "baseline")

    # Use ADK workflow
    workflow = ADKInvestigationWorkflow(
        backend_url=backend_url,
        anthropic_api_key=anthropic_api_key,
        variant=variant,
    )

    logger.info(f"✅ ADK workflow initialized (backend={backend_url}, variant={variant})")

    yield

    logger.info("👋 Agent service shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Support Desk Investigator - Agent",
    description="Investigation agent for automated support ticket analysis",
    version="0.1.0",
    lifespan=lifespan,
)


class InvestigateRequest(BaseModel):
    """Request to investigate a support ticket."""
    case_file: CaseFile


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "agent"}


@app.post("/investigate", response_model=InvestigationResult)
async def investigate(request: InvestigateRequest):
    """Run investigation workflow on a support ticket.

    Args:
        request: Investigation request with case file

    Returns:
        Investigation result with customer reply, evidence, actions
    """
    logger.info(f"🔍 Received investigation request for ticket {request.case_file.ticket_id}")

    try:
        result = await workflow.investigate(request.case_file)
        logger.info(f"✅ Investigation complete for ticket {request.case_file.ticket_id}")
        return result
    except Exception as e:
        logger.error(f"❌ Investigation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
