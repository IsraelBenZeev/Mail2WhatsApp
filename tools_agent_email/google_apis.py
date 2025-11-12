from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from dotenv import load_dotenv
from supabase_client import supabase

load_dotenv(override=True)


class GoogleApis:
    API_NAME = "gmail"
    API_VERSION = "v1"
    SCOPES = ["https://mail.google.com/"]

    # Class variable לשמירת טוקנים של כל המשתמשים (cache)
    _tokens_cache = {}

    def __init__(self, user_id: str, client_secret_file="client_secret.json"):
        self.client_secret_file = client_secret_file
        self.user_id = user_id
        self.access_token = None
        self.refresh_token = None
        # self.creds_users = GoogleApis._tokens_cache  # שימוש ב-cache משותף
        self._init_service()

    def init_tokens(self):
        print("init_tokens")
        print("user_id: ", self.user_id)
        # print("self.creds_users: ", self.creds_users)
        print("_tokens_cache: ", GoogleApis._tokens_cache)
        if (
            GoogleApis._tokens_cache
            and f"user_id_{self.user_id}" in GoogleApis._tokens_cache
        ):
            self.access_token = GoogleApis._tokens_cache[f"user_id_{self.user_id}"][
                "access_token"
            ]
            self.refresh_token = GoogleApis._tokens_cache[f"user_id_{self.user_id}"][
                "refresh_token"
            ]
            print("init_tokens from creds users")
            return True
        else:
            print("init_tokens from supabase")
            tokens = (
                supabase.table("user_tokens")
                .select("*")
                .eq("id", self.user_id)
                .execute()
            )
            if tokens.data and len(tokens.data) > 0:
                self.access_token = tokens.data[0].get("access_token")
                self.refresh_token = tokens.data[0].get("refresh_token")
                GoogleApis._tokens_cache[f"user_id_{self.user_id}"] = {
                    "access_token": self.access_token,
                    "refresh_token": self.refresh_token,
                }

                return True
            else:
                self.access_token = None
                self.refresh_token = None
                return False

    def _init_service(self) -> None:
        """
        Initialize the Gmail API service using the class tokens.
        """
        if not self.init_tokens():
            print(f"⚠️ Cannot init Gmail service: no tokens for user {self.user_id}")
            self.service = None
            return
        print("init_service")
        import json

        with open(self.client_secret_file, "r") as f:
            client_info = json.load(f)
            if "installed" in client_info:
                print("installed")
                client_id = client_info["installed"]["client_id"]
                client_secret = client_info["installed"]["client_secret"]
            elif "web" in client_info:
                print("web")
                client_id = client_info["web"]["client_id"]
                client_secret = client_info["web"]["client_secret"]
            else:
                print("client secret.json חסר 'web' או 'installed'")
                return {
                    "error": "client_secret.json must contain either 'web' or 'installed' configuration"
                }

        # Create credentials from tokens עם client_id ו-client_secret
        creds = Credentials(
            token=self.access_token,
            refresh_token=self.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=self.SCOPES,
        )

        self.refresh_tokens(creds)
        service = build(
            self.API_NAME, self.API_VERSION, credentials=creds, static_discovery=False
        )
        print("service created")
        self.service = service

    def refresh_tokens(self, creds):
        print("refresh_tokens")
        if creds and creds.expired and creds.refresh_token:
            print("refresh token")
            creds.refresh(Request())
            self.access_token = creds.token
        else:
            print("creds are not expired")
