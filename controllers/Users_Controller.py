from supabase_client import supabase
from fastapi.responses import RedirectResponse
import os
import dotenv

dotenv.load_dotenv(override=True)


def get_users():
    users = supabase.auth.admin.list_users(page=1, per_page=100)
    print("users: ", users)
    return users


def save_token_from_supabase(body: dict):
    print("save_token_from_supabase: ", body)
    return {"message": "Token saved successfully"}


def save_tokens_accessMail(user_id: str, access_token: str, refresh_token: str):
    try:
        # משתמשים ב-upsert כדי ליצור או לעדכן רשומה
        result = (
            supabase.table("user_tokens")
            .upsert(
                {
                    "id": user_id,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
            )
            .execute()
        )
        print(f"Tokens saved successfully for user {user_id}")
        print(f"Result: {result.data}")
        return RedirectResponse(url=f"{os.getenv('CLIENT_URL')}/chat")
    except Exception as e:
        print(f"Error saving tokens to Supabase: {str(e)}")
        raise
