from fastapi import HTTPException, Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os
from dotenv import load_dotenv
from controllers.Users_Controller import save_tokens_accessMail

load_dotenv(override=True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT_SECRET_FILE = os.path.join(BASE_DIR, "client_secret.json")
SCOPES = ["https://mail.google.com/"]


def get_base_url(request: Request) -> str:
    """Get base URL from request or environment variable"""
    # Try to get from environment variable first (for local development)
    host = os.getenv("HOST")
    if host:
        return host

    # Otherwise, construct from request
    scheme = request.url.scheme
    host = request.url.hostname
    # Vercel uses port 443 for HTTPS, but we don't need to include it in the URL
    if request.url.port and request.url.port not in [80, 443]:
        return f"{scheme}://{host}:{request.url.port}"
    return f"{scheme}://{host}"


async def authorize_gmail(user_id: str, request: Request):
    try:
        base_url = get_base_url(request)
        redirect_uri = f"{base_url}/OAuth/oauth2callback"
        print(f"Using redirect_uri: {redirect_uri}")

        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_FILE,
            SCOPES,
            redirect_uri=redirect_uri,
        )
        auth_url, _ = flow.authorization_url(
            prompt="consent",
            access_type="offline",
            state=user_id,
        )
        return {"auth_url": auth_url}
    except Exception as e:
        print(f"Error in authorize_gmail: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


async def oauth2callback(code: str, state: str, request: Request):
    """
    Callback endpoint שמקבל את הטוקנים ומחזיר אותם יחד עם user_id
    user_id הועבר דרך state parameter ב-OAuth flow
    """
    user_id = state
    print(f"oauth2callback called with code={code[:20]}... and user_id={user_id}")
    try:
        base_url = get_base_url(request)
        redirect_uri = f"{base_url}/OAuth/oauth2callback"
        print(f"Using redirect_uri: {redirect_uri}")

        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_FILE,
            SCOPES,
            redirect_uri=redirect_uri,
        )
        flow.fetch_token(code=code)
        creds = flow.credentials

        print("creds token: ", creds.token)
        print("creds refresh_token: ", creds.refresh_token)
        print("user_id: ", user_id)

        # return {
        #     "user_id": user_id,
        #     "access_token": creds.token,
        #     "refresh_token": creds.refresh_token,
        # }
        return save_tokens_accessMail(user_id, creds.token, creds.refresh_token)
    except Exception as e:
        print(f"Error in oauth2callback: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
