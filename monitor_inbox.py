#!/usr/bin/env python3
"""Monitor Mail.tm inbox for new Yostar emails in real-time."""

import asyncio
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests', 'integration'))

from email_helper import MailTmClient, MailTmCodeFetcher

load_dotenv()


async def monitor_inbox(poll_interval=10):
    """Monitor inbox and display new emails as they arrive."""
    email = os.getenv("TEST_ACCOUNT_EMAIL")
    password = os.getenv("TEST_ACCOUNT_EMAIL_PASSWORD")

    print(f"📧 Monitoring inbox: {email}")
    print(f"⏱️  Polling every {poll_interval} seconds")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)

    client = MailTmClient()
    try:
        # Login
        token = await client.login(email, password)
        print(f"✓ Logged in successfully\n")

        # Get initial message count
        messages = await client.get_messages(token)
        seen_ids = {msg["id"] for msg in messages}

        print(f"Current inbox: {len(messages)} message(s)")

        # Show existing messages
        if messages:
            print("\nExisting messages:")
            for i, msg in enumerate(messages, 1):
                subject = msg.get("subject", "No subject")
                from_addr = msg.get("from", {}).get("address", "Unknown")
                intro = msg.get("intro", "")[:50]
                print(f"  {i}. {subject}")
                print(f"     From: {from_addr}")
                print(f"     Preview: {intro}...")

                # Try to extract code
                full_msg = await client.get_message(token, msg["id"])
                text_body = full_msg.get("text", "")
                html_body = full_msg.get("html", [""])[0] if full_msg.get("html") else ""

                fetcher = MailTmCodeFetcher(client, token)
                code = fetcher._extract_code_from_body(text_body or html_body)
                if code:
                    print(f"     🔑 Code found: {code}")
                print()

        print(f"\n👀 Watching for new emails... (Press Ctrl+C to stop)\n")

        # Monitor for new messages
        while True:
            await asyncio.sleep(poll_interval)

            messages = await client.get_messages(token)
            new_messages = [msg for msg in messages if msg["id"] not in seen_ids]

            if new_messages:
                timestamp = datetime.now().strftime('%H:%M:%S')
                print(f"\n🔔 [{timestamp}] NEW EMAIL(S) RECEIVED!")
                print("-" * 60)

                for msg in new_messages:
                    subject = msg.get("subject", "No subject")
                    from_addr = msg.get("from", {}).get("address", "Unknown")

                    print(f"\n📨 Subject: {subject}")
                    print(f"   From: {from_addr}")

                    # Get full message
                    full_msg = await client.get_message(token, msg["id"])
                    text_body = full_msg.get("text", "")
                    html_body = full_msg.get("html", [""])[0] if full_msg.get("html") else ""

                    # Try to extract code
                    fetcher = MailTmCodeFetcher(client, token)
                    code = fetcher._extract_code_from_body(text_body or html_body)

                    if code:
                        print(f"\n   🔑 VERIFICATION CODE: {code}")
                        print(f"   ✅ Code is ready to use!")
                    else:
                        # Show preview of content
                        preview = (text_body or html_body)[:200]
                        print(f"\n   Preview: {preview}...")

                    print("-" * 60)

                    # Mark as seen
                    seen_ids.add(msg["id"])
            else:
                # Show activity indicator
                print(f".", end="", flush=True)

    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()


if __name__ == "__main__":
    interval = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    print(f"\n{'='*60}")
    print("  Mail.tm Inbox Monitor")
    print(f"{'='*60}\n")

    try:
        asyncio.run(monitor_inbox(poll_interval=interval))
    except KeyboardInterrupt:
        print("\nExiting...")
