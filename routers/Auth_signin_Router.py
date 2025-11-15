from fastapi import APIRouter,Request
from controllers.Users_Controller import save_token_from_supabase

routerAuthSignin = APIRouter()




@routerAuthSignin.post("/signin-callback")
async def signin_callback(request: Request):
    body = await request.json()
    return save_token_from_supabase(body)
