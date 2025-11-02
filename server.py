from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
from routers.LLM_router import routerLLM

app = FastAPI()
origins = [
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routerLLM, prefix="/llm")

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"Server running on http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
