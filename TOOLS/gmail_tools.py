import os
import base64
from typing import Literal, Optional, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pydantic import BaseModel, Field
from .google_apis import create_service


class EmailMessage(BaseModel):
    msg_id: str = Field(..., description="The ID of the email message.")
    subject: str = Field(..., description="The subject of the email message.")
    sender: str = Field(..., description="The sender of the email message.")
    recipients: str = Field(..., description="The recipients of the email message.")
    body: str = Field(..., description="The body of the email message.")
    snippet: str = Field(..., description="A snippet of the email message.")
    has_attachments: bool = Field(
        ..., description="Indicates if the email has attachments."
    )
    date: str = Field(..., description="The date when the email was sent.")
    star: bool = Field(..., description="Indicates if the email is starred.")
    label: str = Field(..., description="Labels associated with the email message.")


class EmailMessages(BaseModel):
    count: int = Field(..., description="The number of email messages.")
    messages: list[EmailMessage] = Field(..., description="List of email messages.")
    next_page_token: str | None = Field(
        ..., description="Token for the next page of results."
    )


class GmailTool:
    API_NAME = "gmail"
    API_VERSION = "v1"
    SCOPES = ["https://mail.google.com/"]

    def __init__(self, client_secret_file: str) -> None:
        self.client_secret_file = client_secret_file
        self._init_service()

    def _init_service(self) -> None:
        """
        Initialize the Gmail API service.
        """
        self.service = create_service(
            self.client_secret_file, self.API_NAME, self.API_VERSION, self.SCOPES
        )

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        body_type: Literal["plain", "html"] = "plain",
        attachment_paths: Optional[List] = None,
    ) -> dict:
        """
        Send an email using the Gmail API.

        Args:
            to (str): Recipient email address.
            subject (str): Email subject.
            body (str): Email body content.
            body_type (str): Type of the body content ('plain' or 'html').
            attachment_paths (list): List of file paths for attachments.

        Returns :
            dict: Response from the Gmail API.
        """
        try:
            message = MIMEMultipart()
            message["to"] = to
            message["subject"] = subject

            if body_type.lower() not in ["plain", "html"]:
                return 'Error: body_type must be either "plain" or "html".'

            message.attach(MIMEText(body, body_type.lower()))
            if attachment_paths:
                for attachment_path in attachment_paths:
                    if os.path.exists(attachment_path):
                        filename = os.path.basename(attachment_path)

                        with open(attachment_path, "rb") as attachment:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(attachment.read())

                        encoders.encode_base64(part)

                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename= {filename}",
                        )
                        message.attach(part)
                    else:
                        return f"File not found - {attachment_path}"

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
            response = (
                self.service.users()
                .messages()
                .send(userId="me", body={"raw": raw_message})
                .execute()
            )

            return {"msg_id": response["id"], "status": "success"}

        except Exception as e:
            return {"error": f"An error occurred: {str(e)}", "status": "failed"}

    def search_emails(
        self,
        query: Optional[str] = None,
        label: Literal["ALL", "INBOX", "SENT", "DRAFT", "SPAM", "TRASH"] = "INBOX",
        max_results: Optional[int] = 10,
        next_page_token: Optional[str] = None,
    ):
        """
        Search for emails in the user's mailbox using the Gmail API.

        Args:
            query (str): Search query string. Default is None, which returns all emails.
            labels (str): Labels to filter the search results. Default is 'INBOX'.
            Available labels include: 'INBOX', 'SENT', 'DRAFT', 'SPAM', 'TRASH',.
            max_results (int): Maximum number of messages to return. The maximum allowed is 500.
        """
        messages = []
        next_page_token_ = next_page_token

        if label == "ALL":
            label_ = None
        else:
            label_ = [label]
        while True:
            result = (
                self.service.users()
                .messages()
                .list(
                    userId="me",
                    q=query,
                    LabelIds=label_,
                    maxResults=min(500, max_results - len(messages))
                    if max_results
                    else 500,
                    pageToken=next_page_token_,
                )
                .execute()
            )

            messages.extend(result.get("messages", []))

            next_page_token_ = result.get("nextPageToken")
            if not next_page_token_ or (max_results and len(messages) >= max_results):
                break

        # compile emails details
        email_messages = []
        for message_ in messages:
            msg_id = message_["id"]
            msg_details = self.get_email_message_details(msg_id)
            email_messages.append(msg_details)

        email_messages_ = (
            email_messages[:max_results] if max_results else email_messages
        )

        return EmailMessages(
            count=len(email_messages_),
            messages=email_messages_,
            next_page_token=next_page_token_,
        )

    def get_email_message_details(self, msg_id: str) -> EmailMessage:
        """
        Get detailed information about an email message.

        Args:
            msg_id (str): The ID of the email message.

        Returns:
            EmailMessage: Detailed information about the email message.
        """
        try:
            message = (
                self.service.users().messages().get(userId="me", id=msg_id).execute()
            )

            headers = message["payload"].get("headers", [])
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "")
            to = next((h["value"] for h in headers if h["name"] == "To"), "")
            date = next((h["value"] for h in headers if h["name"] == "Date"), "")

            body = self._get_message_body(message["payload"])
            snippet = message.get("snippet", "")
            has_attachments = bool(
                message["payload"].get("parts", [])
                and any(
                    part.get("filename")
                    for part in message["payload"].get("parts", [])
                    if part.get("filename")
                )
            )

            label_ids = message.get("labelIds", [])
            label = ", ".join(label_ids)
            star = "STARRED" in label_ids

            return EmailMessage(
                msg_id=msg_id,
                subject=subject,
                sender=sender,
                recipients=to,
                body=body,
                snippet=snippet,
                has_attachments=has_attachments,
                date=date,
                star=star,
                label=label,
            )
        except Exception as e:
            return EmailMessage(
                msg_id=msg_id,
                subject="",
                sender="",
                recipients="",
                body=f"Error retrieving message: {str(e)}",
                snippet="",
                has_attachments=False,
                date="",
                star=False,
                label="",
            )

    def _get_message_body(self, payload: dict) -> str:
        """
        Extract the body text from an email message payload.

        Args:
            payload (dict): The email message payload.

        Returns:
            str: The email body text.
        """
        body = ""
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    data = part["body"].get("data")
                    if data:
                        body = base64.urlsafe_b64decode(data).decode("utf-8")
                        break
        else:
            if payload["mimeType"] == "text/plain":
                data = payload["body"].get("data")
                if data:
                    body = base64.urlsafe_b64decode(data).decode("utf-8")
        return body

    def get_email_message_body(self, msg_id: str) -> str:
        """
        Get the body of an email message.

        Args:
            msg_id (str): The ID of the email message.

        Returns:
            str: The email body text.
        """
        try:
            message = (
                self.service.users().messages().get(userId="me", id=msg_id).execute()
            )
            return self._get_message_body(message["payload"])
        except Exception as e:
            return f"Error retrieving message body: {str(e)}"

    def delete_email_message(self, msg_id: str) -> dict:
        """
        Delete an email message.

        Args:
            msg_id (str): The ID of the email message to delete.

        Returns:
            dict: Response indicating success or failure.
        """
        try:
            self.service.users().messages().delete(userId="me", id=msg_id).execute()
            return {"msg_id": msg_id, "status": "success"}
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}", "status": "failed"}
