import gradio as gr
from TOOLS.gmail_tools import GmailTool
from agents import Agent, Runner, trace
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(override=True)

# הגדרת הסוכן
instructions = """
You are a smart email agent with tools for sending, searching, and retrieving email details.
Workflow: Searching for emails or retrieving a list of emails
Ask the user for search details:
Keywords (subject, body, sender)
Label filter (INBOX, SENT, DRAFT, SPAM, TRASH, ALL)
Maximum number of results (default: 10, maximum: 500)
Use search_emails to find the emails.
Display results clearly, showing important information for each email: sender, subject, date, and a snippet of the content.
If the user wants more details about a specific email, use get_email_message_details or get_email_message_body with the msg_id.
Summarize many results in a clear, readable format.
Always confirm with the user before deleting emails (delete_email_message).
Workflow: Sending emails
When the user requests to send an email, make sure all required details are present:
Recipient (to)
Subject (subject)
Content (body)
Content type (body_type) – 'plain' or 'html'. Default is 'plain' if not provided.
Optional attachments (attachment_paths)
If any detail is missing, ask the user for it.
Do not perform email searches or display existing emails once the user has provided all sending details.
Immediately use send_email to send the email.
General behavior rules
Display results and actions clearly, professionally, and in a user-friendly way.
Always respond in Hebrew, even when showing information or asking the user for details.
"""

# אתחול
gmail_tool = GmailTool('client_secret.json')
tools = gmail_tool.get_tools()
agent = Agent(
    name="סוכן_מיילים", 
    instructions=instructions,
    model="gpt-4o-mini", 
    tools=tools
)

# פונקציה אסינכרונית לטיפול בשאילתות
async def process_query_async(message, history):
    try:
        # הרצת הסוכן עם trace
        with trace("Gmail_Agent_Query") as t:
            result = await Runner.run(agent, message)
        
        # המרת התוצאה לטקסט
        if hasattr(result, 'output'):
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
    """
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
        rtl=True
    )
    
    # שדה קלט
    with gr.Row():
        msg = gr.Textbox(
            placeholder="שאל אותי משהו על המיילים שלך... לדוגמה: 'תביא לי מיילים מהשבוע האחרון'",
            show_label=False,
            scale=9,
            container=False
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
            label=None
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
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True
    )
