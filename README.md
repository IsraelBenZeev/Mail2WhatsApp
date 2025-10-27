# Gmail MCP Server

מקשר לשרת Gmail באמצעות Model Context Protocol (MCP).

## התקנה

### 1. התקנת תלויות

```bash
# באמצעות uv
uv pip install -e .

# או באמצעות pip רגיל
pip install -e .
```

### 2. הגדרת Gmail API

1. עבור ל-Google Cloud Console
2. צור project חדש
3. הפעל את Gmail API
4. צור OAuth 2.0 credentials
5. הורד את ה-client secret והכנס אותו כ-`client_secret.json` בתיקיית הפרויקט

## הרצה

### 1. הגדרת הרשאות (נדרש פעם אחת בלבד)

**הסבר קצר:**
- `client_secret.json` - ✅ כבר יש לך (זה ההרשאות של האפליקציה)
- `token files/token_gmail_v1.json` - ❌ חסר (זה הטוקן האישי שלך שאתה מקבל אחרי אישור)

לפני השימוש בשרת, צריך לעשות authorization פעם אחת:

#### בסביבת Windows (או WSL עם דפדפן):
```bash
uv run python setup_auth.py
```

#### ב-WSL בלי דפדפן (Windows PowerShell):
```powershell
cd \\wsl$\Ubuntu\home\i2116\projects\exercises\Mail2WhatsApp
uv run python setup_auth.py
```

זה יפעיל את הדפדפן שלך כדי לאשר את ההרשאות. הטוקן יישמר ב-`token files/token_gmail_v1.json`.

### 2. הרצת השרת

#### דרך Cursor (או IDE אחר)

הוסף את ההגדרות הבאות לקובץ המאקרו שלך:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "uv",
      "args": ["run", "--directory", "/home/i2116/projects/exercises/Mail2WhatsApp", "python", "mcp_gmail.py"],
      "cwd": "/home/i2116/projects/exercises/Mail2WhatsApp"
    }
  }
}
```

#### בדיקת שרת MCP (עם token):

```bash
# מתיקיית mcp_clients
uv run client_gmail.py
```

#### בדיקה ישירה של Gmail tools (ממתיקייה הראשית):

```bash
# פעם אחת - עשיית authorization (נדרש טוקן)
uv run python setup_auth.py

# אחרי שיש טוקן - בדיקת פונקציית search
uv run python test_gmail.py
```

**הערה:** `test_gmail.py` מחפש עד 5 מיילים מה-INBOX שלך.

## כלים זמינים

- **Gmail-Send-Email** - שליחת אימייל
- **Gmail-Search-Emails** - חיפוש אימיילים (תיבה נכנסת/נשלחים/טיוטה)

## הערות

- בפעם הראשונה שתפעיל את השרת, תצטרך לאשר את ההרשאות בדפדפן
- Token נשמר אוטומטית בתיקיית `token files/` לפעם הבאה

