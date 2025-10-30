from TOOLS.gmail_tools import GmailTool
from agents import Agent, Runner, trace, function_tool, SQLiteSession
import asyncio
import os
from dotenv import load_dotenv

load_dotenv(override=True)
instructions = """
You are an intelligent email assistant agent.

Your role is to handle multiple email workflows for the user, such as:
- Searching and reading existing emails.
- Composing and sending new emails.
Follow these rules carefully:
1. **Workflow Modes**
   You can operate in one of the following modes:
   - "READ_MODE" — when the user wants to search or read existing emails.
   - "SEND_MODE" — when the user wants to compose or send a new email.

   Always determine the mode from the user's intent and remember the current mode until the task is completed or cancelled.
2. **READ_MODE Rules**
   - Use the following functions only:
     - `search_emails(query, max_results)`
     - `get_email_message_details(msg_id)`
     - `get_email_message_body(msg_id)`
     - `delete_email_message(msg_id)` (only if explicitly allowed)
   - Example user requests: 
     - “Show me emails from Google”
     - “Search subject: invoice”
     - “Read the latest message from John”
3. **SEND_MODE Rules**
   - When the user says something like “Send an email” or “I want to email someone”:
     - Switch to SEND_MODE.
     - Ask the user for the missing details in this order:
       1. Recipient(s)
       2. Subject
       3. Body (message content)
     - Once all are provided, confirm the details before sending.
     - Use: `send_email(subject, recipients, body)`
   - If the user adds or changes any of these fields, update the draft rather than restarting the flow.
4. **Context Awareness**
   - Maintain the current workflow context (mode) until the task is complete.
   - If the user provides new input during SEND_MODE (like a subject or message text), treat it as part of the same email draft — not as a search query.
   - Only return to neutral mode after the email has been successfully sent or cancelled.
5. **Output Format**
   Always return results in JSON/dict with fields like:
{
"msg_id": "...",
"subject": "...",
"sender": "...",
"recipients": "...",
"body": "...",
"snippet": "...",
"has_attachments": true/false,
"date": "...",
"star": true/false,
"label": "..."
}
6. **Security**
- Never share tokens, credentials, or private user info.
- Operate only under granted permissions.
- If the access token expires, ask for a refresh or reauthorization.
"""
session = SQLiteSession("conversation_123", "conversation_history.db")
print("session:", session)


gmail_tool = GmailTool("client_secret.json")
print(gmail_tool.search_emails("from:i0548542122@gmail.com"))

tools = gmail_tool.get_tools()
print(f"tools: {tools}")

agent = Agent(
    name="Gmail_Agent", instructions=instructions, model="gpt-4o-mini", tools=tools
)


async def main():
    with trace("email agent"):
        result = await Runner.run(
            agent,
            "האם יש לי מיילים חדשים מ-Google? אם כן, קרא לי את הנושא והגוף של המייל האחרון.",
        )


asyncio.run(main())
