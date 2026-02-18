#!/usr/bin/env python3
"""Ingest sample incidents into Qdrant vector database.

This script populates Qdrant with historical incidents for semantic similarity search.
Run this once after Qdrant is started to seed the knowledge base.

Usage:
    python scripts/ingest-qdrant.py
    # or with docker compose:
    docker compose --profile tools up -d
    docker compose exec backend python /app/scripts/ingest-qdrant.py
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "incidents"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
VECTOR_SIZE = 384  # Dimension for all-MiniLM-L6-v2 (local model)


# Sample incidents for knowledge base
SAMPLE_INCIDENTS = [
    {
        "title": "Checkout 502 Bad Gateway errors",
        "description": "Multiple users reporting 502 errors when attempting to complete checkout process. Error occurs after payment information is submitted.",
        "root_cause": "Payment gateway service was experiencing high latency due to database connection pool exhaustion. The checkout service timeout was too aggressive (5s) causing premature 502 responses.",
        "resolution": "1. Increased database connection pool size from 20 to 50\n2. Adjusted checkout service timeout to 15s\n3. Added retry logic with exponential backoff\n4. Implemented circuit breaker pattern",
        "category": "error",
        "severity": "high",
        "affected_services": ["checkout", "payment-gateway", "database"],
        "tags": ["502", "timeout", "database", "payment"],
    },
    {
        "title": "User authentication failing intermittently",
        "description": "Users reporting intermittent authentication failures. Login works sometimes but fails other times with 'Invalid credentials' error even with correct password.",
        "root_cause": "Redis cache inconsistency due to multiple Redis instances behind load balancer without session affinity. Users were hitting different cache nodes with inconsistent session data.",
        "resolution": "1. Configured load balancer with session affinity (sticky sessions)\n2. Implemented Redis Sentinel for HA\n3. Added session replication across Redis nodes\n4. Updated session timeout to 30 minutes",
        "category": "authentication",
        "severity": "high",
        "affected_services": ["auth-service", "redis", "load-balancer"],
        "tags": ["auth", "intermittent", "cache", "session"],
    },
    {
        "title": "Dashboard loading extremely slowly",
        "description": "Customer dashboard taking 30+ seconds to load. Performance degradation started gradually over past week.",
        "root_cause": "N+1 query problem in dashboard API. Each user widget was making separate database queries instead of using joins. With 20+ widgets per dashboard, this resulted in 100+ sequential queries.",
        "resolution": "1. Refactored queries to use JOIN statements\n2. Implemented query result caching (5min TTL)\n3. Added database indexes on frequently queried columns\n4. Load reduced from 30s to <2s",
        "category": "performance",
        "severity": "medium",
        "affected_services": ["dashboard-api", "database"],
        "tags": ["slow", "performance", "database", "n+1"],
    },
    {
        "title": "Email notifications not being delivered",
        "description": "Users not receiving password reset emails or order confirmation emails. Email service logs show successful sends but users report nothing in inbox or spam.",
        "root_cause": "SMTP server IP address was blacklisted due to spam score from previous batch email campaign. Email reputation score dropped below threshold.",
        "resolution": "1. Contacted SMTP provider to delist IP\n2. Implemented SPF, DKIM, and DMARC records\n3. Set up email warm-up schedule\n4. Migrated to dedicated IP for transactional emails\n5. Separated batch/marketing emails to different IP pool",
        "category": "email",
        "severity": "high",
        "affected_services": ["email-service", "smtp"],
        "tags": ["email", "delivery", "blacklist", "smtp"],
    },
    {
        "title": "API rate limit exceeded errors",
        "description": "Third-party API integration failing with 429 Too Many Requests errors. Started occurring after deployment of new feature that syncs customer data every 5 minutes.",
        "root_cause": "New sync feature was making API calls for all customers in parallel without rate limiting. With 10k+ customers, this exceeded API provider's rate limit of 100 req/sec.",
        "resolution": "1. Implemented request batching (100 customers per batch)\n2. Added delay between batches (1 second)\n3. Implemented exponential backoff for 429 responses\n4. Added API usage monitoring dashboard\n5. Changed sync schedule to incremental (only changed customers)",
        "category": "integration",
        "severity": "medium",
        "affected_services": ["sync-service", "third-party-api"],
        "tags": ["rate-limit", "429", "api", "throttling"],
    },
    {
        "title": "Mobile app crashes on startup",
        "description": "iOS app version 2.1.0 crashing immediately after launch for users on iOS 14 and earlier. Works fine on iOS 15+.",
        "root_cause": "Used iOS 15+ API (UISheetPresentationController) without version checking. App tried to instantiate unsupported API on older iOS versions, causing crash.",
        "resolution": "1. Added iOS version checking before using new APIs\n2. Implemented fallback UI for older iOS versions\n3. Released hotfix version 2.1.1\n4. Added automated testing for multiple iOS versions in CI/CD",
        "category": "mobile",
        "severity": "critical",
        "affected_services": ["ios-app"],
        "tags": ["crash", "ios", "compatibility", "mobile"],
    },
    {
        "title": "Database replication lag increasing",
        "description": "Read replica lag increased from <1s to 30+ seconds. Reports and analytics showing stale data.",
        "root_cause": "Single large transaction (data migration script) was blocking replication. The migration was processing 10M rows without chunking, causing write locks.",
        "resolution": "1. Killed the problematic migration transaction\n2. Rewrote migration to process in batches of 1000 rows\n3. Added COMMIT after each batch\n4. Set up replication lag monitoring with alerts\n5. Documented best practices for large data migrations",
        "category": "database",
        "severity": "high",
        "affected_services": ["database", "read-replica"],
        "tags": ["replication", "lag", "database", "migration"],
    },
    {
        "title": "S3 bucket permissions error",
        "description": "File upload feature failing with 403 Forbidden errors. Users unable to upload profile pictures or documents.",
        "root_cause": "AWS IAM policy was accidentally modified during security audit, removing PutObject permission for application role. The policy change was deployed without testing.",
        "resolution": "1. Restored IAM policy to include s3:PutObject permission\n2. Added automated IAM policy testing in CI/CD\n3. Implemented policy version control\n4. Required peer review for all IAM changes",
        "category": "aws",
        "severity": "high",
        "affected_services": ["upload-service", "s3"],
        "tags": ["s3", "403", "permissions", "aws", "iam"],
    },
    {
        "title": "Memory leak in background worker",
        "description": "Background job processor consuming increasing memory over time, eventually crashing with OOM error after 12-24 hours of operation.",
        "root_cause": "Event listeners were not being properly cleaned up after job completion. Each job added new listeners without removing old ones, causing memory to grow indefinitely.",
        "resolution": "1. Added explicit removeListener() calls after job completion\n2. Implemented WeakMap for temporary references\n3. Added memory monitoring and alerting\n4. Set worker restart schedule every 6 hours as safeguard\n5. Wrote integration test to detect memory leaks",
        "category": "performance",
        "severity": "high",
        "affected_services": ["worker-service"],
        "tags": ["memory-leak", "oom", "worker", "background-jobs"],
    },
    {
        "title": "Websocket connections dropping frequently",
        "description": "Real-time features (chat, notifications) disconnecting every 1-2 minutes. Users need to refresh page to reconnect.",
        "root_cause": "Load balancer timeout set to 60 seconds, but websocket ping/pong interval was 90 seconds. Load balancer was closing idle connections before ping could keep them alive.",
        "resolution": "1. Reduced websocket ping interval to 30 seconds\n2. Increased load balancer timeout to 300 seconds\n3. Implemented automatic reconnection with exponential backoff\n4. Added connection health monitoring dashboard",
        "category": "realtime",
        "severity": "medium",
        "affected_services": ["websocket-server", "load-balancer"],
        "tags": ["websocket", "disconnect", "timeout", "realtime"],
    },
    {
        "title": "Scheduled reports not being generated",
        "description": "Daily and weekly scheduled reports stopped being sent to customers. Cron job logs show no errors but no reports are produced.",
        "root_cause": "Cron job was scheduled in UTC but database query used server local time (PST). Time zone mismatch caused query to find no records needing report generation.",
        "resolution": "1. Standardized all timestamps to UTC in database\n2. Updated cron schedule to UTC\n3. Added timezone conversion helpers\n4. Implemented report generation monitoring\n5. Added tests for timezone handling",
        "category": "scheduled-jobs",
        "severity": "medium",
        "affected_services": ["report-service", "cron"],
        "tags": ["cron", "timezone", "scheduled", "reports"],
    },
    {
        "title": "CDN cache serving stale content",
        "description": "Users seeing old version of website even after deployment. CSS and JavaScript files not updating for 24+ hours.",
        "root_cause": "CDN cache TTL was set to 7 days with no cache invalidation on deployment. New deployments were not purging CDN cache, causing users to receive stale assets.",
        "resolution": "1. Added CDN cache purge step to deployment pipeline\n2. Reduced TTL to 1 hour for HTML files\n3. Implemented cache busting with content hashes in filenames\n4. Added versioning to static assets\n5. Set up cache-control headers correctly",
        "category": "deployment",
        "severity": "medium",
        "affected_services": ["cdn", "frontend"],
        "tags": ["cdn", "cache", "stale", "deployment"],
    },
    {
        "title": "Search functionality returning no results",
        "description": "Site-wide search returning 0 results for all queries. Search worked fine yesterday but completely broken today.",
        "root_cause": "Elasticsearch index was accidentally deleted during maintenance. The delete command was run on production instead of staging due to misconfigured terminal session.",
        "resolution": "1. Restored index from backup (3 hours old)\n2. Reindexed recent changes from database\n3. Implemented terminal prompt highlighting for production\n4. Required MFA for production Elasticsearch access\n5. Added index backup monitoring",
        "category": "search",
        "severity": "critical",
        "affected_services": ["search-service", "elasticsearch"],
        "tags": ["search", "elasticsearch", "index", "deleted"],
    },
    {
        "title": "Payment processing double-charging customers",
        "description": "Multiple customers reporting being charged twice for single orders. Payment gateway shows two successful charges within seconds of each other.",
        "root_cause": "Race condition in payment processing. Slow response from payment gateway caused frontend to show timeout error, user clicked retry, but first payment actually succeeded, resulting in duplicate charge.",
        "resolution": "1. Implemented idempotency keys for payment requests\n2. Added duplicate payment detection (same amount, same card, <5min apart)\n3. Improved frontend loading states and timeouts\n4. Added refund automation for detected duplicates\n5. Implemented payment reconciliation dashboard",
        "category": "payment",
        "severity": "critical",
        "affected_services": ["payment-service", "payment-gateway"],
        "tags": ["payment", "double-charge", "race-condition", "idempotency"],
    },
    {
        "title": "High CPU usage on application servers",
        "description": "Application servers consistently at 90%+ CPU utilization. Response times degraded from 200ms to 3+ seconds.",
        "root_cause": "Inefficient regex pattern in validation logic. Pattern was using catastrophic backtracking on certain input strings, causing CPU to spike to 100% for several seconds per request.",
        "resolution": "1. Replaced problematic regex with simpler pattern\n2. Added input length limits before validation\n3. Implemented request timeout middleware\n4. Added CPU profiling in staging\n5. Set up performance regression testing",
        "category": "performance",
        "severity": "high",
        "affected_services": ["application-server"],
        "tags": ["cpu", "performance", "regex", "backtracking"],
    },
    {
        "title": "SSL certificate expiration causing service outage",
        "description": "Production site showing SSL certificate error. All HTTPS traffic failing. Service completely unavailable to users.",
        "root_cause": "SSL certificate expired and auto-renewal failed silently. Renewal process encountered rate limit from Let's Encrypt but alerts were not configured. Certificate expired at midnight causing immediate outage.",
        "resolution": "1. Manually requested new certificate from Let's Encrypt\n2. Set up certificate expiration monitoring (30, 14, 7 days before)\n3. Configured PagerDuty alerts for cert renewal failures\n4. Implemented automated cert renewal with multiple providers\n5. Added runbook for emergency cert renewal",
        "category": "security",
        "severity": "critical",
        "affected_services": ["load-balancer", "ssl"],
        "tags": ["ssl", "certificate", "expiration", "outage"],
    },
    {
        "title": "File uploads failing for files >10MB",
        "description": "Users unable to upload large files. Upload progress reaches 100% but then fails with generic error message. Works fine for small files.",
        "root_cause": "Nginx max request body size was set to 10MB but application expected up to 50MB. Nginx was rejecting requests before they reached application, returning 413 error that frontend didn't handle correctly.",
        "resolution": "1. Increased nginx client_max_body_size to 100MB\n2. Updated frontend to handle 413 errors gracefully\n3. Added file size validation before upload starts\n4. Implemented chunked upload for files >50MB\n5. Added upload size limits to UI",
        "category": "upload",
        "severity": "medium",
        "affected_services": ["nginx", "upload-service"],
        "tags": ["upload", "file-size", "413", "nginx"],
    },
    {
        "title": "Database connection pool exhausted",
        "description": "Application unable to process requests. Error logs showing 'Cannot acquire connection from pool - all connections are in use'. Service effectively down.",
        "root_cause": "Long-running transactions not being committed or rolled back. A buggy report query was holding database connections open indefinitely, exhausting the pool of 50 connections within minutes.",
        "resolution": "1. Killed long-running sessions in database\n2. Fixed report query to use read-only transaction\n3. Implemented connection timeout (30s)\n4. Increased pool size from 50 to 100\n5. Added connection pool monitoring\n6. Implemented statement timeout in database",
        "category": "database",
        "severity": "critical",
        "affected_services": ["database", "connection-pool"],
        "tags": ["database", "connection-pool", "exhausted", "timeout"],
    },
    {
        "title": "Mobile push notifications not working",
        "description": "Users not receiving push notifications on mobile devices. Notification logs show messages being queued but not delivered.",
        "root_cause": "Firebase Cloud Messaging (FCM) server key was rotated for security reasons but application still using old key. All push requests were failing authentication.",
        "resolution": "1. Updated application with new FCM server key\n2. Deployed hotfix to all environments\n3. Implemented secret rotation testing procedure\n4. Added FCM delivery monitoring dashboard\n5. Set up key expiration alerts",
        "category": "mobile",
        "severity": "high",
        "affected_services": ["push-notification-service", "fcm"],
        "tags": ["push-notifications", "fcm", "mobile", "auth"],
    },
    {
        "title": "Deployment rollback needed after feature release",
        "description": "New feature causing widespread errors in production. Error rate jumped from <0.1% to 15% immediately after deployment.",
        "root_cause": "Feature flag was incorrectly configured to enable for 100% of users instead of planned 10% gradual rollout. Untested edge cases in new code path caused failures for users with specific account configurations.",
        "resolution": "1. Immediately rolled back deployment\n2. Fixed feature flag configuration\n3. Added integration tests for edge cases\n4. Re-deployed with 5% rollout\n5. Gradually increased to 100% over 3 days\n6. Implemented automated rollback triggers",
        "category": "deployment",
        "severity": "high",
        "affected_services": ["application", "feature-flags"],
        "tags": ["deployment", "rollback", "feature-flag", "errors"],
    },
]


def get_embedding(text: str, embedding_model: SentenceTransformer) -> list[float]:
    """Generate embedding vector for text using local sentence-transformers model.

    Args:
        text: Text to embed
        embedding_model: SentenceTransformer model instance

    Returns:
        Embedding vector as list
    """
    # sentence-transformers encode is synchronous, returns numpy array
    embedding = embedding_model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


async def create_collection(qdrant_client: AsyncQdrantClient):
    """Create Qdrant collection for incidents.

    Args:
        qdrant_client: Qdrant async client
    """
    logger.info(f"Creating collection '{COLLECTION_NAME}'...")

    try:
        # Check if collection already exists
        collections = await qdrant_client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if COLLECTION_NAME in collection_names:
            logger.info(f"Collection '{COLLECTION_NAME}' already exists, recreating...")
            await qdrant_client.delete_collection(COLLECTION_NAME)

        # Create collection with vector configuration
        await qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )

        logger.info(f"✅ Collection '{COLLECTION_NAME}' created successfully")

    except Exception as e:
        logger.error(f"❌ Failed to create collection: {e}")
        raise


async def ingest_incidents(
    qdrant_client: AsyncQdrantClient,
    embedding_model: SentenceTransformer,
):
    """Ingest sample incidents into Qdrant.

    Args:
        qdrant_client: Qdrant async client
        embedding_model: SentenceTransformer model for embeddings
    """
    logger.info(f"Ingesting {len(SAMPLE_INCIDENTS)} incidents...")

    points = []

    for idx, incident in enumerate(SAMPLE_INCIDENTS):
        logger.info(f"Processing incident {idx + 1}/{len(SAMPLE_INCIDENTS)}: {incident['title']}")

        # Create combined text for embedding (title + description + resolution)
        combined_text = f"{incident['title']}\n{incident['description']}\n{incident['resolution']}"

        # Generate embedding using local model (synchronous)
        vector = get_embedding(combined_text, embedding_model)

        # Create point with payload
        point = PointStruct(
            id=idx + 1,
            vector=vector,
            payload={
                "incident_id": f"INC-2025-{idx + 1:03d}",
                "title": incident["title"],
                "description": incident["description"],
                "root_cause": incident["root_cause"],
                "resolution": incident["resolution"],
                "category": incident["category"],
                "severity": incident["severity"],
                "affected_services": incident["affected_services"],
                "tags": incident["tags"],
                "created_at": (datetime.now() - timedelta(days=30 + idx)).isoformat(),
                "resolved_at": (datetime.now() - timedelta(days=25 + idx)).isoformat(),
            },
        )

        points.append(point)

    # Upload points to Qdrant
    logger.info("Uploading points to Qdrant...")
    await qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    logger.info(f"✅ Successfully ingested {len(points)} incidents")


async def verify_ingestion(qdrant_client: AsyncQdrantClient):
    """Verify that incidents were ingested correctly.

    Args:
        qdrant_client: Qdrant async client
    """
    logger.info("Verifying ingestion...")

    collection_info = await qdrant_client.get_collection(COLLECTION_NAME)
    logger.info(f"Collection info: {collection_info.points_count} points")

    if collection_info.points_count == len(SAMPLE_INCIDENTS):
        logger.info("✅ Verification successful!")
    else:
        logger.warning(
            f"⚠️  Expected {len(SAMPLE_INCIDENTS)} points but found {collection_info.points_count}"
        )


async def main():
    """Main ingestion workflow (idempotent - skips if data already exists)."""
    logger.info("🚀 Starting Qdrant ingestion check...")

    # Initialize Qdrant client
    qdrant_client = AsyncQdrantClient(url=QDRANT_URL)

    try:
        # Check if collection exists and has data (idempotency check)
        collections = await qdrant_client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if COLLECTION_NAME in collection_names:
            collection_info = await qdrant_client.get_collection(COLLECTION_NAME)
            if collection_info.points_count > 0:
                logger.info(
                    f"✅ Collection '{COLLECTION_NAME}' already exists with "
                    f"{collection_info.points_count} points. Skipping ingestion."
                )
                return

        # Collection doesn't exist or is empty - proceed with ingestion
        logger.info(f"📥 Loading local embedding model: {EMBEDDING_MODEL}")
        embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info(f"✅ Model loaded (dimension={embedding_model.get_sentence_embedding_dimension()})")

        # Create collection
        await create_collection(qdrant_client)

        # Ingest incidents
        await ingest_incidents(qdrant_client, embedding_model)

        # Verify
        await verify_ingestion(qdrant_client)

        logger.info("🎉 Ingestion complete!")

    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}", exc_info=True)
        sys.exit(1)

    finally:
        await qdrant_client.close()


if __name__ == "__main__":
    asyncio.run(main())
