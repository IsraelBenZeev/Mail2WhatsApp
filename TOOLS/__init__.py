from .gmail_tools import GmailTool

gmail_tool = GmailTool('../../client_secret.json')
print(f"GmailTool: {gmail_tool.search_emails("from:i0548542122@gmail.com")}")