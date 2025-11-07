from tools_agent_email.gmail_tools import GmailTool
from supabase_client import supabase

gmail_tool = GmailTool("7177d1bd-4875-4666-9a03-8d29e09880e8")
# print(gmail_tool.search_emails("from:i0548542122@gmail.com"))
print(gmail_tool.send_email("i0548542122@gmail.com", "test", "test"))
