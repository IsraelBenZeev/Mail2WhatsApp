from supabase_client import supabase


def get_users():
    users = supabase.auth.admin.list_users(page=1, per_page=100)
    print("users: ", users)
    return users
