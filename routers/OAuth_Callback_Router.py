from fastapi import APIRouter
from controllers.OAuth_Callback_Controller import (
    authorize_gmail as authorize_gmail_controller,
    oauth2callback as oauth2callback_controller,
)

routerOAuthCallback = APIRouter()


@routerOAuthCallback.get("/authorize_gmail")
async def authorize_gmail():
    return await authorize_gmail_controller()


@routerOAuthCallback.get("/oauth2callback")
async def oauth2callback(code: str):
    return await oauth2callback_controller(code)
