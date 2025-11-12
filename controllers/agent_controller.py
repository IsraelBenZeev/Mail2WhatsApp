from agents import trace, Runner
from agent import init_agent
from datetime import datetime, timedelta
from supabase_client import supabase


# אובייקט פשוט לשמירת היסטוריית שיחה בזיכרון
class SimpleSession:
    def __init__(self, user_id: str):
        self.history = []
        self.user_id = user_id

    async def get_items(self):
        print("get_items")
        response = (
            supabase.table("messages")
            .select("*")
            .eq("user_id", self.user_id)
            .order("created_at", desc=False)
            .order("role", desc=False)
            .execute()
        )
        self.history = [
            {
                "role": item["role"],
                "content": item.get("content", ""),
            }
            for item in response.data
        ]
        print("history: ", self.history)
        return self.history

    async def add_item(self, role: str, content: str):
        print("add_item: ")
        self.history.append({"role": role, "content": content})

    # מתודה שמוסיפה רשימה של הודעות
    async def add_items(self, items: list):
        print("add_items: ")
        self.history.extend(items)


# יצירת אובייקט session פשוט
# חשוב: מעבירים את האובייקט עצמו, לא את התוצאה של get_items()
# הספרייה agents קוראת ל-get_items() בעצמה
# הערה: history הוסר כי SimpleSession דורש user_id - נוצר חדש בכל קריאה ל-handle_message


def get_mail_agent(user_id: str):
    # יוצר agent חדש לכל user_id
    # אם רוצים cache, אפשר להחזיר את השורות המבוטלות ולהשתמש ב-dict לפי user_id
    mail_agent = init_agent(user_id)
    return mail_agent


def handle_save_in_DB(message: str, result: str, user_id: str):
    try:
        supabase.table("messages").insert(
            [
                {
                    "role": "user",
                    "content": message,
                    "user_id": user_id,
                    "created_at": datetime.now().isoformat(),
                },
                {
                    "role": "assistant",
                    "content": result,
                    "user_id": user_id,
                    "created_at": (
                        datetime.now() + timedelta(milliseconds=1)
                    ).isoformat(),
                },
            ]
        ).execute()
    except Exception as e:
        print("error 👉:", e)


async def handle_message(message: str, user_id: str):
    with trace(f"chat_endpoint_{user_id}"):
        mail_agent = get_mail_agent(user_id)
        result = await Runner.run(mail_agent, message, session=SimpleSession(user_id))
        print("message 👉:", message)
        print("result 👉:", result.final_output)
        handle_save_in_DB(message, result.final_output, user_id)
    return {
        "role": "assistant",
        "content": result.final_output,
        "time": datetime.now(),
    }
