import gradio as gr
from TOOLS.gmail_tools import GmailTool
from agents import Agent, Runner, trace, SQLiteSession
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(override=True)

session = SQLiteSession("conversation_123", "conversation_history.db")
print("session:", session)

# הגדרת הסוכן
instructions = """
You are an intelligent email assistant agent.

Your role is to handle multiple email workflows for the user, such as:
- Searching and reading existing emails.
- Composing and sending new emails.

Follow these rules carefully:

1. **Workflow Modes**
   You can operate in one of the following modes:
   - "READ_MODE" — when the user wants to search or read existing emails.
   - "SEND_MODE" — when the user wants to compose or send a new email.

   Always determine the mode from the user's intent and remember the current mode until the task is completed or cancelled.

2. **READ_MODE Rules**
   - Use the following functions only:
     - `search_emails(query, max_results)`
     - `get_email_message_details(msg_id)`
     - `get_email_message_body(msg_id)`
     - `delete_email_message(msg_id)` (only if explicitly allowed)
   - Example user requests: 
     - “Show me emails from Google”
     - “Search subject: invoice”
     - “Read the latest message from John”

3. **SEND_MODE Rules - CRITICAL**
   - When the user says something like "Send an email" or "I want to email someone":
     - Switch to SEND_MODE IMMEDIATELY.
     - **DO NOT call send_email function yet!**
     - First, check what information you already have:
       * If recipient (to) is missing → Ask: "מי הנמען? (What is the recipient email address?)"
       * If subject is missing → Ask: "מה נושא המייל? (What is the email subject?)"
       * If body is missing → Ask: "מה תוכן המייל? (What is the email message content?)"
     - Only after you have ALL THREE pieces of information (to, subject, body), present a summary and ask for confirmation:
       "אני מוכן לשלוח מייל:
        אל: [recipient]
        נושא: [subject]
        תוכן: [body]
        האם לשלוח? (Should I send this email?)"
     - Only call `send_email(to, subject, body)` AFTER user confirms.
   
   **NEVER call send_email without explicit user confirmation!**
   
   - If the user adds or changes any of these fields during the conversation, update the draft and confirm again before sending.

4. **Context Awareness**
   - Maintain the current workflow context (mode) until the task is complete.
   - If the user provides new input during SEND_MODE (like a subject or message text), treat it as part of the same email draft — not as a search query.
   - Only return to neutral mode after the email has been successfully sent or cancelled.

5. **Output Format**
   Always return results in JSON/dict with fields like:
{
"msg_id": "...",
"subject": "...",
"sender": "...",
"recipients": "...",
"body": "...",
"snippet": "...",
"has_attachments": true/false,
"date": "...",
"star": true/false,
"label": "..."
}

6. **Security**
- Never share tokens, credentials, or private user info.
- Operate only under granted permissions.
- If the access token expires, ask for a refresh or reauthorization.
"""

# אתחול
gmail_tool = GmailTool("client_secret.json")
tools = gmail_tool.get_tools()
agent = Agent(
    name="סוכן_מיילים", instructions=instructions, model="gpt-4o-mini", tools=tools
)


# פונקציה אסינכרונית לטיפול בשאילתות
async def process_query_async(message, history):
    try:
        # הרצת הסוכן עם trace
        with trace("Gmail_Agent_Query"):
            # result = await Runner.run(agent, message)
            result = await Runner.run(agent, message, session=session)
            print("📚 היסטוריה אחרי הריצה:", session)

        # המרת התוצאה לטקסט
        if hasattr(result, "output"):
            response = result.output
        else:
            response = str(result)

        return response
    except Exception as e:
        return f"❌ שגיאה: {str(e)}"


# פונקציה סינכרונית לממשק
def process_query(message, history):
    return asyncio.run(process_query_async(message, history))


# בניית הממשק
with gr.Blocks(
    theme=gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="cyan",
    ),
    title="🤖 סוכן מיילים חכם",
    css="""
        .gradio-container {
            direction: rtl;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .footer {
            text-align: center;
            padding: 15px;
            color: #666;
            font-size: 0.9em;
        }
        .example-btn {
            margin: 5px;
        }
    """,
) as demo:
    # כותרת
    gr.HTML("""
        <div class="header">
            <h1>🤖 סוכן מיילים חכם</h1>
            <p>עוזר אישי לניהול ואיתור מיילים בחשבון Gmail שלך</p>
        </div>
    """)

    # אזור הצ'אט
    chatbot = gr.Chatbot(
        value=[],
        elem_id="chatbot",
        height=500,
        show_label=False,
        avatar_images=(None, "🤖"),
        bubble_full_width=False,
        rtl=True,
    )

    # שדה קלט
    with gr.Row():
        msg = gr.Textbox(
            placeholder="שאל אותי משהו על המיילים שלך... לדוגמה: 'תביא לי מיילים מהשבוע האחרון'",
            show_label=False,
            scale=9,
            container=False,
        )
        submit = gr.Button("📤 שלח", scale=1, variant="primary")

    # דוגמאות
    gr.Markdown("### 💡 דוגמאות לשאילתות:")
    with gr.Row():
        gr.Examples(
            examples=[
                "תביא לי את כל המיילים שנשלחו מ i0548542122@gmail.com",
                "חפש מיילים עם הנושא 'חשבונית'",
                "הצג לי מיילים חשובים מהשבוע האחרון",
                "תן לי רשימה של המיילים הלא קרואים",
                "מה יש לי ממייקרוסופט?",
            ],
            inputs=msg,
            label=None,
        )

    # פונקציית התגובה
    def respond(message, chat_history):
        if not message.strip():
            return "", chat_history

        # הוספת ההודעה של המשתמש
        chat_history.append([message, None])

        # קבלת התשובה
        bot_response = process_query(message, chat_history)

        # עדכון ההיסטוריה עם התשובה
        chat_history[-1][1] = bot_response

        return "", chat_history

    # חיבור האירועים
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    submit.click(respond, [msg, chatbot], [msg, chatbot])

    # כפתור ניקוי
    clear = gr.Button("🗑️ נקה שיחה")
    clear.click(lambda: [], None, chatbot)

    # כותרת תחתונה
    gr.HTML("""
        <div class="footer">
            <p>🔒 הנתונים שלך מאובטחים ונשמרים רק במכשיר שלך</p>
            <p>נוצר עם ❤️ באמצעות Gradio ו-OpenAI Agents</p>
        </div>
    """)

# הרצת הממשק
if __name__ == "__main__":
    print("🚀 מפעיל את הסוכן...")
    print("📧 מתחבר לחשבון Gmail...")
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False, inbrowser=True)
