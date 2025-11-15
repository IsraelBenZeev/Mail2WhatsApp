from fastapi import HTTPException
from google_auth_oauthlib.flow import InstalledAppFlow
import os
from dotenv import load_dotenv
from controllers.Users_Controller import save_tokens_accessMail

load_dotenv(override=True)

HOST = os.getenv("HOST")
print("HOST: ", HOST)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT_SECRET_FILE = os.path.join(BASE_DIR, "client_secret.json")
SCOPES = ["https://mail.google.com/"]


async def authorize_gmail(user_id: str):
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_FILE,
            SCOPES,
            redirect_uri=f"{HOST}/OAuth/oauth2callback",
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


async def oauth2callback(code: str, state: str):
    """
    Callback endpoint שמקבל את הטוקנים ומחזיר אותם יחד עם user_id
    user_id הועבר דרך state parameter ב-OAuth flow
    """
    user_id = state
    print(f"oauth2callback called with code={code[:20]}... and user_id={user_id}")
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_FILE,
            SCOPES,
            redirect_uri=f"{HOST}/OAuth/oauth2callback",
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
