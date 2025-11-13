from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
from dotenv import load_dotenv

load_dotenv(override=True)

from routers.LLM_Router import routerLLM
from routers.OAuth_Callback_Router import routerOAuthCallback
from routers.Users_Router import routerUsers
# from supabase_client import supabase

app = FastAPI()
# origins = [
#     "http://localhost:5173",
#     "http://localhost:5174",
# ]
origins = [
    os.getenv("CLIENT_URL"),
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    print("root endpoint called!🙌")
    return {"message": "Welcome to the Mail2WhatsApp server!", "version": "5.0"}

app.include_router(routerLLM, prefix="/llm", tags=["llm"])
app.include_router(routerOAuthCallback, prefix="/OAuth", tags=["OAuth"])
app.include_router(routerUsers, prefix="/users", tags=["users"])

HOST = os.getenv("HOST")

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"Server running on {HOST}:{port}")
    print("Registered routes:")
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            print(f"  {list(route.methods)} {route.path}")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)


# פקודת הרצה uv run uvicorn app:app --reload
# פקודת הרצה uv run python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
