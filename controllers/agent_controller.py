from agents import trace, Runner, SQLiteSession
from agent import mail_agent
from datetime import datetime

session = SQLiteSession("conversation_123", "conversation_history.db")


async def handle_message(message: str):
    with trace("chat_endpoint"):
        result = await Runner.run(mail_agent, message, session=session)
        print("result:", result.final_output)
    return {
        "role": "assistant",
        "content": result.final_output,
        "time": datetime.now(),
    }
