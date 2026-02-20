#!/usr/bin/env python3
"""Initialize Frappe Helpdesk with service accounts and demo users.

This script creates:
1. Helpdesk Assistant service account (for automated responses)
2. John Doe customer user (for demo tickets)
3. Acme Corporation customer organization

Run this once after Frappe is started to seed users and organizations.
This script is idempotent - it will skip entities that already exist.

Usage:
    python scripts/init_frappe_users.py
    # or with docker compose:
    docker compose exec backend python /app/scripts/init_frappe_users.py
"""

import asyncio
import logging
import os
import sys
from base64 import b64encode

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
FRAPPE_URL = os.getenv("FRAPPE_URL", "http://localhost:8080")
FRAPPE_API_KEY = os.getenv("FRAPPE_API_KEY", "Administrator")
FRAPPE_API_SECRET = os.getenv("FRAPPE_API_SECRET", "admin123")

# Service Account Configuration
SERVICE_ACCOUNT = {
    "email": "helpdesk-assistant@example.com",
    "first_name": "Helpdesk",
    "last_name": "Assistant",
    "enabled": 1,
    "send_welcome_email": 0,
}

# Demo Customer Configuration
DEMO_CUSTOMER_USER = {
    "email": "john.doe@acmecorp.com",
    "first_name": "John",
    "last_name": "Doe",
    "enabled": 1,
    "send_welcome_email": 0,
}

# Demo Customer Organization
DEMO_CUSTOMER_ORG = {
    "customer_name": "Acme Corporation",
    "customer_primary_contact": "john.doe@acmecorp.com",
}


async def wait_for_frappe(client: httpx.AsyncClient, max_retries=30, delay=2):
    """Wait for Frappe to be ready.

    Args:
        client: HTTP client with auth
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds

    Raises:
        Exception: If Frappe is not ready after max_retries
    """
    for attempt in range(max_retries):
        try:
            response = await client.get(f"{FRAPPE_URL}/api/resource/User?limit_page_length=1")
            if response.status_code == 200:
                logger.info("✅ Frappe is ready!")
                return
        except Exception as e:
            logger.debug(f"Waiting for Frappe... ({attempt + 1}/{max_retries}): {e}")

        if attempt < max_retries - 1:
            await asyncio.sleep(delay)

    raise Exception(f"Frappe not ready after {max_retries} attempts")


async def user_exists(client: httpx.AsyncClient, email: str) -> bool:
    """Check if a user exists in Frappe.

    Args:
        client: HTTP client with auth
        email: User email to check

    Returns:
        True if user exists, False otherwise
    """
    try:
        response = await client.get(f"{FRAPPE_URL}/api/resource/User/{email}")
        return response.status_code == 200
    except Exception:
        return False


async def customer_exists(client: httpx.AsyncClient, customer_name: str) -> bool:
    """Check if a customer organization exists in Frappe.

    Args:
        client: HTTP client with auth
        customer_name: Customer organization name to check

    Returns:
        True if customer exists, False otherwise
    """
    try:
        response = await client.get(
            f"{FRAPPE_URL}/api/resource/HD%20Customer/{customer_name}"
        )
        return response.status_code == 200
    except Exception:
        return False


async def create_user(client: httpx.AsyncClient, user_data: dict) -> dict:
    """Create a user in Frappe.

    Args:
        client: HTTP client with auth
        user_data: User data dictionary

    Returns:
        Created user data

    Raises:
        httpx.HTTPError: If creation fails
    """
    logger.info(f"Creating user: {user_data['email']}")

    response = await client.post(
        f"{FRAPPE_URL}/api/resource/User",
        json=user_data,
    )
    response.raise_for_status()

    result = response.json()
    logger.info(f"✅ User created: {user_data['email']}")
    return result["data"]


async def create_customer(client: httpx.AsyncClient, customer_data: dict) -> dict:
    """Create a customer organization in Frappe Helpdesk.

    Args:
        client: HTTP client with auth
        customer_data: Customer data dictionary

    Returns:
        Created customer data

    Raises:
        httpx.HTTPError: If creation fails
    """
    logger.info(f"Creating customer organization: {customer_data['customer_name']}")

    response = await client.post(
        f"{FRAPPE_URL}/api/resource/HD%20Customer",
        json=customer_data,
    )
    response.raise_for_status()

    result = response.json()
    logger.info(f"✅ Customer organization created: {customer_data['customer_name']}")
    return result["data"]


async def main():
    """Main initialization workflow (idempotent - skips entities that exist)."""
    logger.info("🚀 Starting Frappe user initialization...")

    # Create HTTP client with basic auth
    auth_token = f"{FRAPPE_API_KEY}:{FRAPPE_API_SECRET}"
    auth_header = b64encode(auth_token.encode()).decode()

    async with httpx.AsyncClient(
        headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/json",
        },
        timeout=30.0,
    ) as client:
        try:
            # Wait for Frappe to be ready
            logger.info("⏳ Waiting for Frappe to be ready...")
            await wait_for_frappe(client)

            # Check and create Helpdesk Assistant service account
            if await user_exists(client, SERVICE_ACCOUNT["email"]):
                logger.info(
                    f"✅ Service account '{SERVICE_ACCOUNT['email']}' already exists. Skipping."
                )
            else:
                await create_user(client, SERVICE_ACCOUNT)

            # Check and create demo customer user
            if await user_exists(client, DEMO_CUSTOMER_USER["email"]):
                logger.info(
                    f"✅ Demo user '{DEMO_CUSTOMER_USER['email']}' already exists. Skipping."
                )
            else:
                await create_user(client, DEMO_CUSTOMER_USER)

            # Check and create demo customer organization
            if await customer_exists(client, DEMO_CUSTOMER_ORG["customer_name"]):
                logger.info(
                    f"✅ Customer organization '{DEMO_CUSTOMER_ORG['customer_name']}' already exists. Skipping."
                )
            else:
                await create_customer(client, DEMO_CUSTOMER_ORG)

            logger.info("🎉 Frappe user initialization complete!")
            logger.info("")
            logger.info("📋 Created accounts:")
            logger.info(f"  • Service Account: {SERVICE_ACCOUNT['email']}")
            logger.info(f"  • Demo Customer: {DEMO_CUSTOMER_USER['email']}")
            logger.info(f"  • Customer Org: {DEMO_CUSTOMER_ORG['customer_name']}")

        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}", exc_info=True)
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
