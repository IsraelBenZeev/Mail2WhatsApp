from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
import os
from agents import Agent, trace, Runner
from dotenv import load_dotenv
from urllib.parse import urlencode

load_dotenv(override=True)
os.environ["GMAIL_MCP_CREDENTIALS_PATH"] = "/home/i2116/.gmail-mcp/credentials.json"




base_url = "https://server.smithery.ai/@shinzo-labs/gmail-mcp/mcp"
params = {
    "api_key": os.getenv("SMITHERY_API_KEY"),
    "profile": os.getenv("SMITHERY_PROFILE_KEY"),
}
url = f"{base_url}?{urlencode(params)}"
instructions = """
You are an AI agent equipped with tools to access Gmail. You will receive requests from the user and must choose the appropriate tool to perform the requested action. Always verify the parameters before executing any operation, and return the results in a clear and structured format. 
"""
# אתה סוכן AI המצויד בכלים לגישה ל-Gmail. תקבל בקשות מהמשתמש ועליך לבחור את הכלי המתאים כדי לבצע את הפעולה המבוקשת. תמיד ודא את הפרמטרים לפני ביצוע כל פעולה, והחזר את התוצאות בצורה ברורה ומסודרת. טפל בשגיאות באופן מסודר וספק הודעות מידע אם משהו אינו ניתן לביצוע.


class NamedMCPSession:
    """Wrapper to add name attribute to MCP ClientSession for OpenAI Agents compatibility"""

    def __init__(self, session: ClientSession, name: str = "gmail_mcp"):
        self.session = session
        self.name = name
        # Add attributes that OpenAI Agents might check for
        self.use_structured_content = False

    async def list_tools(self, *args, **kwargs):
        """Override list_tools to handle OpenAI Agents' extra parameters"""
        # OpenAI Agents passes (run_context, agent) but MCP only needs ()
        # So we'll ignore extra args
        result = await self.session.list_tools()
        # Return just the tools list, not the entire result object
        return result.tools

    def __getattr__(self, name):
        # Delegate all other attributes to the wrapped session
        if name in ["session", "name", "list_tools", "use_structured_content"]:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )
        attr = getattr(self.session, name)
        # Return bound methods as-is, they keep the session context
        return attr

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


async def main():
    # Connect to the server using HTTP client
    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools_result = await session.list_tools()
            # print(f"Available tools: {', '.join([t.name for t in tools_result.tools])}")

            # Wrap session with name attribute
            named_session = NamedMCPSession(session, name="gmail_mcp")

            agent = Agent(
                name="agent_weather",
                instructions=instructions,
                model="gpt-4o-mini",
                mcp_servers=[named_session],
            )
            # print(f"agent: {agent}")
            with trace("get maesages from GMAIL"):
                result = await Runner.run(
                    agent, "תביא לי את 5 ההודעות האחרונות מתיבת דואר נכנס דואר ראשי"
                )
                print(result.final_output)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
