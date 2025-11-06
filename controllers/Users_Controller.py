from supabase_client import supabase
from fastapi.responses import RedirectResponse


def get_users():
    users = supabase.auth.admin.list_users(page=1, per_page=100)
    print("users: ", users)
    return users


def save_tokens(user_id: str, access_token: str, refresh_token: str):
    supabase.table("profiles").update(
        {"access_token": access_token, "refresh_token": refresh_token}
    ).eq("id", user_id).execute()
    # return {"message": "Tokens saved successfully"}
    return RedirectResponse(url="http://localhost:5173/chat")
