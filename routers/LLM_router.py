from fastapi import APIRouter
from fastapi import Request
from controllers.agent_controller import handle_message

routerLLM = APIRouter()


@routerLLM.post("/send-message")
async def chat(request: Request):
    request_data = await request.json()
    print("Received request:", request_data)
    message = request_data.get("message", "")
    print("message: ", message)
    return await handle_message(message)
