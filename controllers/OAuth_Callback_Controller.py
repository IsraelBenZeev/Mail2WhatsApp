from fastapi import HTTPException
from google_auth_oauthlib.flow import InstalledAppFlow
import os
from dotenv import load_dotenv
from controllers.Users_Controller import save_tokens_accessMail
from tempfile import NamedTemporaryFile

load_dotenv(override=True)

HOST = os.getenv("HOST")
print("HOST: ", HOST)
import json


# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# CLIENT_SECRET_FILE = os.path.join(BASE_DIR, "client_secret.json")
CLIENT_SECRET_FILE = os.getenv("GOOGLE_CLIENT_SECRET_JSON")
SCOPES = ["https://mail.google.com/"]


def write_env_json_to_file(env_key: str, file_name: str):
    """
    קוראת משתנה סביבה שמכיל JSON, ממירה אותו ל-JSON, ויוצרת קובץ עם השם הנתון ב-ROOT.

    :param env_key: מפתח משתנה הסביבה שמכיל את ה-JSON
    :param file_name: שם הקובץ שיווצר
    :return: נתיב מלא לקובץ שנוצר
    """
    json_str = os.getenv(env_key)
    if not json_str:
        raise Exception(f"Environment variable '{env_key}' not found")

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON in environment variable '{env_key}': {str(e)}")

    file_path = os.path.join(os.getcwd(), file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return file_path


def delete_file(file_path: str):
    """
    מוחקת קובץ אם הוא קיים.

    :param file_path: הנתיב המלא לקובץ למחיקה
    """
    if os.path.exists(file_path):
        os.remove(file_path)


async def authorize_gmail(user_id: str):
    temp_file = write_env_json_to_file(
        "GOOGLE_CLIENT_SECRET_JSON", "client_secret.json"
    )
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            temp_file,
            SCOPES,
            # redirect_uri=f"{HOST}/OAuth/oauth2callback",
            redirect_uri=f"{HOST}/isr/oauth2callback",
        )
        auth_url, _ = flow.authorization_url(
            prompt="consent",
            access_type="offline",
            state=user_id,
        )
        delete_file(temp_file)
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
    print(f"oauth2callback called with code={code[:20]}... and user_id={user_id}👍")
    try:
        temp_file = write_env_json_to_file(
            "GOOGLE_CLIENT_SECRET_JSON", "client_secret.json"
        )
        flow = InstalledAppFlow.from_client_secrets_file(
            temp_file,
            SCOPES,
            redirect_uri=f"{HOST}/isr/oauth2callback",
        )
        delete_file(temp_file)
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
