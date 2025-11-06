# איך State עובד ב-OAuth 2.0

## מה הספרייה עושה:

### 1. ב-authorization_url():
```python
flow.authorization_url(state=user_id)
```
- הספרייה לוקחת את הערך `user_id` ומכניסה אותו ל-URL:
  ```
  https://accounts.google.com/o/oauth2/auth?...&state=123&...
  ```
- הספרייה **לא שומרת** את זה - היא פשוט מוסיפה את זה ל-URL

### 2. מה Google עושה:
- Google **רואה** את הפרמטר `state=123` ב-URL
- Google **שומר** את זה זמנית
- כשהמשתמש מאשר, Google **מחזיר** את אותו state בחזרה:
  ```
  https://yourhost.com/OAuth/oauth2callback?code=ABC&state=123
  ```

### 3. מה אנחנו עושים ב-callback:
- **אנחנו** (לא הספרייה) קוראים את `state` מה-query string
- **אנחנו** ממירים אותו ל-`user_id`
- הספרייה לא עושה את זה אוטומטית!

## למה זה עובד?

זה **סטנדרט OAuth 2.0** - כל ספק OAuth (Google, Facebook, GitHub וכו') עובד כך:
1. אתה שולח `state` ב-authorization request
2. הספק **חייב** להחזיר את אותו `state` בחזרה
3. זה עוזר למניעת CSRF attacks

## בקוד שלך:

```python
# שלב 1: שולח state
state=user_id  # הספרייה מוסיפה את זה ל-URL

# שלב 2: Google מחזיר state
# Google עושה את זה אוטומטית (סטנדרט)

# שלב 3: אנחנו קוראים state
async def oauth2callback(code: str, state: str):  # FastAPI קורא את זה מה-URL
    user_id = state  # אנחנו ממירים את זה
```

**הספרייה לא "יודעת" - זה אנחנו שעושים את זה!**

