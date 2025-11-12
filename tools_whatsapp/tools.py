from agents import function_tool
from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv(override=True)
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_client = Client(account_sid, auth_token)




def send_whatsapp_message(to_number: str, message_text: str):
    """
    שולח הודעת WhatsApp דרך Twilio Sandbox או מספר רשמי
    """
    message = twilio_client.messages.create(
        from_=f'whatsapp:{os.getenv("TWILIO_FROM_NUMBER")}',
        to=f'whatsapp:{to_number}',
        body=message_text
    )
    print("Message SID:", message.sid)
    return message.sid

send_whatsapp_message("+972502291330", "שלום מהשרת!")   
print("message sent successfully")