from fastapi import APIRouter, Request
from controllers.agent_controller import handle_message
from supabase_client import supabase

routerLLM = APIRouter()


@routerLLM.post("/ask-llm/{user_id}")
async def chat(user_id: str, request: Request):
    print("user_id from ask-llm: ", user_id)
    request_data = await request.json()
    print("Received request:", request_data)
    message = request_data.get("message", "")
    print("message: ", message)
    return await handle_message(message, user_id)


@routerLLM.get("/get-messages/{user_id}")
async def get_messages(user_id: str):
    response = supabase.table("messages")\
    .select("*")\
    .eq("user_id", user_id)\
    .order("created_at", desc=False)\
    .order("role", desc=False)\
    .execute()
    return response.data