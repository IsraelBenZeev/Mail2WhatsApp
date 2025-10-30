from agents import Agent, Runner, trace, function_tool, SQLiteSession
import asyncio
import os
from dotenv import load_dotenv

load_dotenv(override=True)
session = SQLiteSession("conversation_123", "conversation_history.db")
print("session:", session)
instructions2 = "You are a helpful assistant. You must remember any details the user tells you, especially their name."
# agent = Agent(name="agent_mail", instructions=instructions,model="gpt-4o-mini", tools=tools)
agent2 = Agent(name="agent_mail", instructions=instructions2, model="gpt-4o-mini")


async def main():
    with trace("email agent"):
        result1 = await Runner.run(agent2, "איך קוראים לי ואיפה אני עובד ובאיזה עיר", session=session)
        print("session:", session)
        print("result1.final_output:", result1.final_output)


asyncio.run(main())
