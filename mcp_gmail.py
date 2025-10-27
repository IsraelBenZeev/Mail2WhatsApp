import os
import sys
from mcp.server.fastmcp import FastMCP

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from TOOLS.gmail_tools import GmailTool

work_dir = os.path.dirname(os.path.abspath(__file__))
gmail_tool = GmailTool(os.path.join(work_dir, "client_secret.json"))

mcp = FastMCP(
    "Gmail",
    dependencies=[
        "google-api-python-client",
        "google-auth-httplib2",
        "google-auth-oauthlib",
    ],
)

mcp.add_tool(
    gmail_tool.send_email,
    name="Gmail-Send-Email",
    description="Send an email message in Gmail",
)
# mcp.add_tool(
#     gmail_tool.get_email_message_details,
#     name="Gmail-Get-Email-Message-Details",
#     description="Get details of an email message in Gmail",
# )
# mcp.add_tool(
#     gmail_tool.get_email_message_body,
#     name="Get-Email-Message-Body",
#     description="Get the body of an email message (Gmail)",
# )
mcp.add_tool(
    gmail_tool.search_emails,
    name="Gmail-Search-Emails",
    description="Search or return emails in Gmail. Default is None, which returns all email",
)
# mcp.add_tool(
#     gmail_tool.delete_email_message,
#     name="Gmail-Delete-Email-Message",
#     description="Delete an email message in Gmail.",
# )

if __name__ == "__main__":
    mcp.run()
