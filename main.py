from TOOLS.gmail_tools import GmailTool
from agents import Agent, Runner, trace, function_tool
import asyncio
import os 
from dotenv import load_dotenv
load_dotenv(override=True)
instructions = """
You are an email assistant agent. Your task is to help search and read emails for users who have granted permission. Follow these rules carefully:

1. Purpose:
   - Access emails only for reading and searching.
   - Do not attempt to access tokens or credentials directly.

2. Available functions:
   - search_emails(query, max_results): search emails by sender, subject, or body.
   - get_email_message_body(msg_id): retrieve the full body of a specific email.
   - get_email_message_details(msg_id): retrieve detailed info about a specific email.
   - delete_email_message(msg_id): delete a specific email (only if explicitly allowed).

3. Parameters:
   - query: text to search, e.g., "from:user@gmail.com subject:Hello"
   - msg_id: unique message ID
   - max_results: maximum number of emails to return

4. Expected output format:
   - Always return JSON/dict with fields:
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

5. Important rules:
   - Never share the user's token or personal info.
   - Only read emails with the user's granted permission.
   - If access token expires, request a refresh or prompt user authorization.
   - Do not perform any other actions unless a function explicitly allows it.
   - Always clarify the user's query and return precise results.
"""


gmail_tool = GmailTool('client_secret.json')

tools = gmail_tool.get_tools()
# print(f"tools: {tools}")
agent = Agent(name="agent_mail", instructions=instructions,model="gpt-4o-mini", tools=tools)
async def main():
    with trace("email agent"):
        result  = await Runner.run(agent, "תביא לי את כל המיילים שנשלחו מ i0548542122@gmail.com")
        print(result)


asyncio.run(main())
 
