import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


class GoogleApis:
    API_NAME = "gmail"
    API_VERSION = "v1"
    SCOPES = ["https://mail.google.com/"]

    def __init__(self, client_secret_file="client_secret.json"):
        self.client_secret_file = client_secret_file
        self.access_token = os.getenv("ACCESS_TOKEN") or None
        self.refresh_token = os.getenv("REFRESH_TOKEN") or None
        self._init_service()

    def init_tokens(self):
        print("init_tokens")
        self.access_token = os.getenv("ACCESS_TOKEN")
        self.refresh_token = os.getenv("REFRESH_TOKEN")

    def _init_service(self) -> None:
        """
        Initialize the Gmail API service using the class tokens.
        """
        # בדיקה שהטוקנים קיימים
        print("init_service")
        if not self.access_token or not self.refresh_token:
            print("בדיקה שהטוקנים קיימים")
            raise ValueError("Tokens not initialized. Please call init_tokens() first.")

        # Load client info from client_secret_file (נדרש גם עבור טוקנים תקפים)
        import json

        # אתחול ה client_id וה client_secret
        with open(self.client_secret_file, "r") as f:
            client_info = json.load(f)
            # תמיכה גם ב-"web" וגם ב-"installed" (לפי סוג האפליקציה ב-Google Cloud Console)
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
                raise ValueError(
                    "client_secret.json must contain either 'web' or 'installed' configuration"
                )

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
        if creds.expired and creds.refresh_token:
            print("refresh token")
            creds.refresh(Request())
            self.access_token = creds.token
