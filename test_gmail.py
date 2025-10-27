#!/usr/bin/env python3
"""
Test script to check if Gmail MCP server works.
This will try to search for emails.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from TOOLS.gmail_tools import GmailTool


def test_search_emails():
    print("=" * 60)
    print("Testing Gmail Search Emails")
    print("=" * 60)
    print()

    # Initialize GmailTool
    try:
        gmail_tool = GmailTool("client_secret.json")
        print("✅ GmailTool initialized successfully")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize GmailTool: {e}")
        print("\nMake sure you have run: uv run python setup_auth.py")
        print("to authorize the application first.")
        return

    # Test search for emails
    print("Searching for emails in INBOX...")
    print()

    try:
        result = gmail_tool.search_emails(
            query=None,  # Get all emails
            label="INBOX",
            max_results=5,  # Just get 5 emails for testing
        )

        print(f"✅ Found {result.count} emails")
        print()

        if result.messages:
            print("📧 Email list:")
            print("-" * 60)
            for i, msg in enumerate(result.messages, 1):
                print(f"\n{i}. ID: {msg.msg_id}")
                print(f"   From: {msg.sender}")
                print(f"   Subject: {msg.subject}")
                print(f"   Date: {msg.date}")
                print(f"   Attachments: {'Yes' if msg.has_attachments else 'No'}")
        else:
            print("No emails found.")

        print("\n" + "=" * 60)
        print("✅ Test completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Error searching emails: {e}")
        print("\nPossible reasons:")
        print("1. No token file exists (run: uv run python setup_auth.py)")
        print("2. Token expired (rerun setup_auth.py)")
        print("3. Network issue")


if __name__ == "__main__":
    test_search_emails()
