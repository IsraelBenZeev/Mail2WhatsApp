from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
from agents import trace, Runner, SQLiteSession
from datetime import datetime

from app import mail_agent

app = FastAPI()
session = SQLiteSession("conversation_123", "conversation_history.db")
origins = [
    "http://localhost:5173",  # הכתובת של React/Vite
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/hello")
async def hello(request: Request):
    request_data = (await request.json())
    print("Received request:", request_data)
    print("name: ", request_data.get("name"))
    return {"message": "hello"}


@app.post("/send-message")
async def chat(request: Request):
    request_data = (await request.json())
    print("Received request:", request_data)
    message = request_data.get("message", "")
    print("message: ", message)
    with trace("chat_endpoint"):
        result = await Runner.run(mail_agent, message, session=session)
        print("result:", result.final_output)
    return {
        "role": "assistant",
        "content": result.final_output,
        "time": datetime.now(),

    }


if __name__ == "__main__":
    # Allow running this file directly: read PORT from env (default 8000)

    port = int(os.getenv("PORT", "8000"))
    print(f"Server running on http://0.0.0.0:{port}")
    # Use 0.0.0.0 to be reachable from other machines on the network; change to 127.0.0.1 for local only
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
