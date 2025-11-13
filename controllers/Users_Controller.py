from supabase_client import supabase
from fastapi.responses import RedirectResponse
import os
import dotenv

dotenv.load_dotenv(override=True)


def get_users():
    users = supabase.auth.admin.list_users(page=1, per_page=100)
    print("users: ", users)
    return users


def save_tokens(user_id: str, access_token: str, refresh_token: str):
    supabase.table("user_tokens").update(
        {"access_token": access_token, "refresh_token": refresh_token}
    ).eq("id", user_id).execute()
    # return {"message": "Tokens saved successfully"}
    return RedirectResponse(url=f"{os.getenv("CLIENT_URL")}/chat")
