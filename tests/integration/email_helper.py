"""Email helper utilities for integration tests using Mail.tm API."""

import re
import asyncio
from typing import Optional
import httpx


class MailTmClient:
    """Client for Mail.tm API."""

    BASE_URL = "https://api.mail.tm"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def login(self, email: str, password: str) -> str:
        """Login and get JWT token.

        Args:
            email: Mail.tm email address
            password: Mail.tm password

        Returns:
            JWT token string

        Raises:
            httpx.HTTPError: If login fails
        """
        response = await self.client.post(
            f"{self.BASE_URL}/token",
            json={"address": email, "password": password}
        )
        response.raise_for_status()
        return response.json()["token"]

    async def get_messages(self, token: str) -> list:
        """Get all messages for account.

        Args:
            token: JWT token from login

        Returns:
            List of message objects with id, subject, from, intro

        Raises:
            httpx.HTTPError: If request fails
        """
        response = await self.client.get(
            f"{self.BASE_URL}/messages",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        data = response.json()
        return data.get("hydra:member", [])

    async def get_message(self, token: str, message_id: str) -> dict:
        """Get full message including body.

        Args:
            token: JWT token from login
            message_id: Message ID to fetch

        Returns:
            Message object with full text and html body

        Raises:
            httpx.HTTPError: If request fails
        """
        response = await self.client.get(
            f"{self.BASE_URL}/messages/{message_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        return response.json()


class MailTmCodeFetcher:
    """Fetches verification codes from Mail.tm inbox."""

    def __init__(self, mail_client: MailTmClient, token: str):
        """Initialize with Mail.tm client and JWT token.

        Args:
            mail_client: MailTmClient instance
            token: JWT token from login
        """
        self.mail_client = mail_client
        self.token = token
        self._seen_message_ids = set()

    async def _mark_existing_messages_as_seen(self):
        """Mark all current messages as seen to avoid processing old emails."""
        messages = await self.mail_client.get_messages(self.token)
        self._seen_message_ids = {msg["id"] for msg in messages}

    async def wait_for_code(
        self,
        timeout: int = 90,
        poll_interval: int = 5
    ) -> str:
        """Poll Mail.tm API for Yostar email and extract 6-digit code.

        Args:
            timeout: Maximum seconds to wait for code
            poll_interval: Seconds between polling attempts

        Returns:
            6-digit verification code as string

        Raises:
            TimeoutError: If code not received within timeout
            ValueError: If code extraction fails
        """
        # Mark existing messages as seen
        await self._mark_existing_messages_as_seen()

        start_time = asyncio.get_event_loop().time()

        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                raise TimeoutError(
                    f"No verification code received within {timeout} seconds"
                )

            # Fetch messages
            messages = await self.mail_client.get_messages(self.token)

            # Look for new messages from Yostar
            for msg in messages:
                if msg["id"] in self._seen_message_ids:
                    continue

                # Check if it's from Yostar or contains verification keywords
                subject = msg.get("subject", "").lower()
                from_addr = msg.get("from", {}).get("address", "").lower()

                if "yostar" in from_addr or "yostar" in subject or "verification" in subject:
                    # Fetch full message
                    full_msg = await self.mail_client.get_message(self.token, msg["id"])

                    # Try to extract code from text or HTML body
                    text_body = full_msg.get("text", "")
                    html_body = full_msg.get("html", [""])[0] if full_msg.get("html") else ""

                    code = self._extract_code_from_body(text_body or html_body)
                    if code:
                        return code

                    # Mark as seen even if no code found
                    self._seen_message_ids.add(msg["id"])

            # Wait before next poll
            await asyncio.sleep(poll_interval)

    def _extract_code_from_body(self, email_text: str) -> Optional[str]:
        """Extract 6-digit code from email body.

        Args:
            email_text: Email body (HTML or plain text)

        Returns:
            6-digit code if found, None otherwise
        """
        # Look for 6 consecutive digits
        match = re.search(r'\b(\d{6})\b', email_text)
        if match:
            return match.group(1)
        return None
