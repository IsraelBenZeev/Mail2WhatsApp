import os
import base64
from typing import Literal, Optional, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pydantic import BaseModel, Field
from agents import function_tool
from dotenv import load_dotenv
from tools_agent_email.google_apis import GoogleApis

load_dotenv(override=True)


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
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        print("GmailTool user_id: ", self.user_id)
        self.service_manager = GoogleApis(self.user_id)
        self.service = self.service_manager.service

    def send_email(
        self,
        to: Optional[str] = None,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        body_type: Literal["plain", "html"] = "plain",
        attachment_paths: Optional[List[str]] = None,
    ) -> dict:
        """
        Send an email using the Gmail API.

        Args:
            to (str): Recipient email address. If not provided, will return error asking for recipient.
            subject (str): Email subject. If not provided, will return error asking for subject.
            body (str): Email body content. If not provided, will return error asking for body.
            body_type (str): Type of the body content ('plain' or 'html').
            attachment_paths (list): List of file paths for attachments.

        Returns :
            dict: Response from the Gmail API or error message with instructions.
        """
        if not self.service:
            return {
                "error": "Gmail service not initialized. tokens are not valid.",
                "status": "error",
            }
        # Validate required parameters
        if not to:
            return {
                "error": "Missing recipient email address. Please provide the recipient's email address (to).",
                "status": "missing_parameters",
            }
        if not subject:
            return {
                "error": "Missing email subject. Please provide the email subject.",
                "status": "missing_parameters",
            }
        if not body:
            return {
                "error": "Missing email body. Please provide the email message content (body).",
                "status": "missing_parameters",
            }

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
        if not self.service:
            return {
                "error": "Gmail service not initialized. tokens are not valid.",
                "status": "error",
            }
        messages = []
        next_page_token_ = next_page_token

        if label == "ALL":
            label_ = None
        else:
            label_ = [label]
        while True:
            # Build the API call parameters
            api_params = {
                "userId": "me",
                "maxResults": min(500, max_results - len(messages))
                if max_results
                else 500,
            }

            # Build query string
            query_parts = []
            if query:
                query_parts.append(query)
            if label_ is not None and label != "ALL":
                query_parts.append(f"label:{label.lower()}")

            if query_parts:
                api_params["q"] = " ".join(query_parts)
            if next_page_token_:
                api_params["pageToken"] = next_page_token_

            result = self.service.users().messages().list(**api_params).execute()

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
        if not self.service:
            return {
                "error": "Gmail service not initialized. tokens are not valid.",
                "status": "error",
            }
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
        if not self.service:
            return "Gmail service not initialized. tokens are not valid."
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
        if not self.service:
            return "Gmail service not initialized. tokens are not valid."
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
        if not self.service:
            return {
                "error": "Gmail service not initialized. tokens are not valid.",
                "status": "error",
            }
        try:
            self.service.users().messages().delete(userId="me", id=msg_id).execute()
            return {"msg_id": msg_id, "status": "success"}
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}", "status": "failed"}

    def get_tools(self):
        """
        Get all available Gmail tools as a list.

        Returns:
            list: List of function tools that can be used by an agent.
        """
        if not self.service:
            # החזר רשימה ריקה במקום dict - Agent מצפה לרשימה
            print("⚠️ Gmail service not initialized. Returning empty tools list.")
            return []

        # Create wrapper functions to avoid binding issues with @function_tool
        @function_tool
        def send_email(
            to: Optional[str] = None,
            subject: Optional[str] = None,
            body: Optional[str] = None,
            body_type: Literal["plain", "html"] = "plain",
            attachment_paths: Optional[List[str]] = None,
        ) -> dict:
            """Send an email using the Gmail API. All parameters (to, subject, body) are required but should be collected from the user before calling this function."""
            return self.send_email(to, subject, body, body_type, attachment_paths)

        @function_tool
        def search_emails(
            query: Optional[str] = None,
            label: Literal["ALL", "INBOX", "SENT", "DRAFT", "SPAM", "TRASH"] = "INBOX",
            max_results: Optional[int] = 10,
            next_page_token: Optional[str] = None,
        ):
            """Search for emails in the user's mailbox using the Gmail API."""
            return self.search_emails(query, label, max_results, next_page_token)

        @function_tool
        def get_email_message_details(msg_id: str) -> EmailMessage:
            """Get detailed information about an email message."""
            return self.get_email_message_details(msg_id)

        @function_tool
        def get_email_message_body(msg_id: str) -> str:
            """Get the body of an email message."""
            return self.get_email_message_body(msg_id)

        @function_tool
        def delete_email_message(msg_id: str) -> dict:
            """Delete an email message."""
            return self.delete_email_message(msg_id)

        return [
            send_email,
            search_emails,
            get_email_message_details,
            get_email_message_body,
            delete_email_message,
        ]
