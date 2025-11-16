from fastapi import APIRouter, Request
from pydantic import BaseModel
from controllers.OAuth_Callback_Controller import (
    authorize_gmail as authorize_gmail_controller,
    oauth2callback as oauth2callback_controller,
)

routerOAuthCallback = APIRouter()


class AuthorizeRequest(BaseModel):
    user_id: str


@routerOAuthCallback.get("/authorize_gmail/{user_id}")
async def authorize_gmail(user_id: str, request: Request):
    print("user_id: ", user_id)
    return await authorize_gmail_controller(user_id, request)


@routerOAuthCallback.get("/oauth2callback")
async def oauth2callback(code: str, state: str, request: Request):
    print("state in oauth2callback: ", state)
    return await oauth2callback_controller(code, state, request)
