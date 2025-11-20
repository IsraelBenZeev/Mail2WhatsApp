from agents import Agent
from dotenv import load_dotenv

load_dotenv(override=True)
instructions = """
You are a Style Agent.

Your role is to receive text from another agent and refine it.

Rules:

1. Always return the output in Hebrew only.
2. Your task is to rewrite the text in a clear, friendly, and user-oriented tone.
3. Do not change the meaning of the original message.
4. Do not add any new information.
5. Do not remove any important information.
6. Maintain a polite, professional, and helpful tone.
7. If the received text is unclear, you may clarify it — but only without adding new content.
8. You do not make decisions, you do not execute logic, and you do not call functions.  
   Your responsibility is **only** to refine the wording.
9. Always return only the rewritten text, with no explanations or additional commentary.
"""


# אתחול - יצירת הכלי בתוך פונקציה כדי להבטיח שהוא נוצר נכון
def get_style_agent_tool():
    """
    יוצר ומחזיר את הכלי style_agent_tool.
    יש לקרוא לפונקציה זו בתוך init_agent כדי להבטיח שהכלי נוצר נכון.
    """
    style_agent = Agent(
        name="style_agent", instructions=instructions, model="gpt-4o-mini"
    )
    style_agent_tool = style_agent.as_tool(
        tool_name="style_agent_tool",
        tool_description="⚠️ MANDATORY - YOU MUST USE THIS TOOL FOR EVERY USER RESPONSE ⚠️ This tool rewrites text into clear, friendly Hebrew. You CANNOT respond to users without calling this tool first. Workflow: 1) Prepare your response text, 2) Call style_agent_tool(input='your text'), 3) Return the tool's output. Parameter: 'input' (string) - the text you want to send to the user. Example: style_agent_tool(input='Hello, how can I help?'). This is NOT optional - it's required for every response.",
        # כלי חובה: כל טקסט שמוחזר למשתמש חייב לעבור דרך כלי זה. קרא לכלי עם הפרמטר 'input' שמכיל את הטקסט. דוגמה: style_agent_tool(input='הטקסט שלך כאן').
    )
    return style_agent_tool
