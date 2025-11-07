from agents import trace, Runner, SQLiteSession
from agent import init_agent
from datetime import datetime

session = SQLiteSession("conversation_123", "conversation_history.db")

# Lazy initialization - יוצר את הסוכן רק בפעם הראשונה שמשתמשים בו
_mail_agent = None

def get_mail_agent(user_id: str):
    global _mail_agent
    if _mail_agent is None:
        _mail_agent = init_agent(user_id)
    return _mail_agent


async def handle_message(message: str, user_id: str):
    with trace(f"chat_endpoint_{user_id}"):
        mail_agent = get_mail_agent(user_id)
        result = await Runner.run(mail_agent, message, session=session)
        print("result:", result.final_output)
    return {
        "role": "assistant",
        "content": result.final_output,
        "time": datetime.now(),
    }
