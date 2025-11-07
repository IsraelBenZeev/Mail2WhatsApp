from fastapi import APIRouter, Request
from controllers.agent_controller import handle_message

routerLLM = APIRouter()


@routerLLM.post("/ask-llm/{user_id}")
async def chat(user_id: str, request: Request):
    request_data = await request.json()
    print("Received request:", request_data)
    message = request_data.get("message", "")
    print("message: ", message)
    return await handle_message(message, user_id)
