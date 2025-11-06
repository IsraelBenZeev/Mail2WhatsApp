from tools_agent_email.gmail_tools import GmailTool

gmail_tool = GmailTool()
# print(gmail_tool.search_emails("from:i0548542122@gmail.com"))
print(gmail_tool.send_email("i0548542122@gmail.com", "test", "test"))
