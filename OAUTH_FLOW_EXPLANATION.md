# תהליך OAuth Flow עם State Parameter

## זרימת הנתונים:

```
1. Client → Server (POST /authorize_gmail)
   { "user_id": "123" }
   
2. Server → Google (Authorization URL)
   https://accounts.google.com/o/oauth2/auth?
     ...&state=123&...
   ↑
   ה-user_id נשלח כ-state
   
3. User מאשר ב-Google
   Google שומר את state=123
   
4. Google → Server (GET /oauth2callback)
   https://yourhost.com/OAuth/oauth2callback?
     code=ABC123&state=123
   ↑                    ↑
   authorization code   ה-user_id חזר!
   
5. Server שומר ב-DB:
   {
     "user_id": "123",  ← מהפרמטר state
     "access_token": "...",
     "refresh_token": "..."
   }
```

## למה זה עובד?

- **State Parameter** הוא חלק מהסטנדרט של OAuth 2.0
- Google **חייב** להחזיר את אותו state ששלחנו
- זה עובד כמו "session" - אנחנו שולחים מידע, Google שומר אותו, ומחזיר אותו בחזרה
- זה גם עוזר למניעת CSRF attacks

## בקוד שלך:

1. **שורה 28** - שולח את user_id כ-state:
   ```python
   state=user_id  # "123"
   ```

2. **שורה 21** - מקבל את state מ-Google:
   ```python
   async def oauth2callback(code: str, state: str):
       # state = "123" (מה ש-Google החזיר)
   ```

3. **שורה 24** - ממיר ל-user_id:
   ```python
   user_id = state  # "123"
   ```

4. **שורה 65** - שומר ב-DB:
   ```python
   "user_id": user_id  # "123"
   ```

