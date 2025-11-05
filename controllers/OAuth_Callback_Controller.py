from fastapi import HTTPException
from google_auth_oauthlib.flow import InstalledAppFlow
import os
from dotenv import load_dotenv
load_dotenv(override=True)

HOST = os.getenv("HOST")
print("HOST: ", HOST)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT_SECRET_FILE = os.path.join(BASE_DIR, "client_secret.json")
SCOPES = ["https://mail.google.com/"]


async def authorize_gmail():
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_FILE,
            SCOPES,
            redirect_uri=f"{HOST}/OAuth/oauth2callback",
        )
        auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
        print("Authorization URL:", auth_url)
        return {"auth_url": auth_url}
    except Exception as e:
        print(f"Error in authorize_gmail: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


async def oauth2callback(code: str):
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        SCOPES,
        redirect_uri=f"{HOST}/OAuth/oauth2callback",
    )
    flow.fetch_token(code=code)
    creds = flow.credentials
    print("creds: ", creds.token)
    print("creds: ", creds.refresh_token)
    # כאן תוכל לשמור את creds.token ו creds.refresh_token בבסיס הנתונים
    return {"access_token": creds.token, "refresh_token": creds.refresh_token}
