"""FastAPI application for backend service."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import tools, webhooks

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("🚀 Backend service starting...")
    yield
    logger.info("👋 Backend service shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Support Desk Investigator - Backend",
    description="Backend service for ticket webhooks and tool APIs",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
app.include_router(tools.router, prefix="/tools", tags=["tools"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "backend"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Support Desk Investigator - Backend",
        "version": "0.1.0",
        "docs": "/docs",
    }
