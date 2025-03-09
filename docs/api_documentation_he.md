# תיעוד ה-API - Taski

## סקירה כללית

מסמך זה מספק מדריך מקיף ל-API של Taski, ממשק RESTful לניהול משימות. ה-API מאפשר למשתמשים להירשם, להתחבר ולבצע פעולות CRUD על משימות.

## כתובת בסיס

כל נקודות הקצה של ה-API הן יחסיות לכתובת הבסיס:

```
http://localhost:8000/api/
```

## אימות

ה-API משתמש באימות JWT (JSON Web Token). רוב נקודות הקצה דורשות אימות.

### תהליך האימות

1. הרשמת משתמש חדש או התחברות עם פרטי התחברות קיימים
2. קבלת טוקן גישה וטוקן רענון
3. הכללת טוקן הגישה בכותרת ה-Authorization לבקשות הבאות
4. כאשר טוקן הגישה פג תוקף, יש להשתמש בטוקן הרענון כדי לקבל טוקן גישה חדש

### כותרות אימות

עבור נקודות קצה מאומתות, יש לכלול את הכותרת הבאה:

```
Authorization: Bearer <access_token>
```

## נקודות קצה

### אימות

#### הרשמת משתמש חדש

```
POST /api/auth/register/
```

##### גוף הבקשה

```json
{
  "username": "example_user",
  "email": "user@example.com",
  "password": "secure_password123"
}
```

##### תגובה (201 Created)

```json
{
  "user": {
    "id": 1,
    "username": "example_user",
    "email": "user@example.com"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
  }
}
```

##### שגיאות אפשריות

- `400 Bad Request`: חסרים שדות נדרשים
- `400 Bad Request`: שם המשתמש כבר קיים
- `400 Bad Request`: כתובת האימייל כבר קיימת

#### התחברות

```
POST /api/auth/login/
```

##### גוף הבקשה

```json
{
  "username": "example_user",
  "password": "secure_password123"
}
```

##### תגובה (200 OK)

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
}
```

##### שגיאות אפשריות

- `401 Unauthorized`: פרטי התחברות שגויים

#### רענון טוקן

```
POST /api/auth/refresh/
```

##### גוף הבקשה

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
}
```

##### תגובה (200 OK)

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
}
```

##### שגיאות אפשריות

- `401 Unauthorized`: טוקן רענון לא תקף או פג תוקף

### משימות

#### הצגת כל המשימות

מחזיר משימות שבהן המשתמש המאומת הוא הבעלים או מוקצה למשימה.

```
GET /api/tasks/
```

##### פרמטרים בשאילתה

| פרמטר     | סוג    | תיאור                                           |
|-----------|--------|------------------------------------------------|
| status    | מחרוזת | סינון לפי סטטוס (TODO, IN_PROGRESS, DONE)      |
| priority  | מחרוזת | סינון לפי עדיפות (LOW, MEDIUM, HIGH)           |
| search    | מחרוזת | חיפוש משימות התואמות את השאילתה בכותרת/תיאור  |
| ordering  | מחרוזת | סידור תוצאות (created_at, -created_at, due_date, וכו') |

##### תגובה (200 OK)

```json
[
  {
    "id": 1,
    "title": "השלמת תיעוד הפרויקט",
    "description": "כתיבת תיעוד מקיף עבור הפרויקט",
    "created_at": "2025-03-09T14:00:00Z",
    "due_date": "2025-03-15T23:59:59Z",
    "status": "TODO",
    "priority": "HIGH",
    "owner": 1,
    "assigned_to": 1,
    "owner_details": {
      "id": 1,
      "username": "example_user",
      "email": "user@example.com"
    },
    "assigned_to_details": {
      "id": 1,
      "username": "example_user",
      "email": "user@example.com"
    }
  },
  ...
]
```

##### שגיאות אפשריות

- `401 Unauthorized`: חסר טוקן אימות או טוקן לא תקף

#### יצירת משימה חדשה

```
POST /api/tasks/
```

##### גוף הבקשה

```json
{
  "title": "יישום תכונה חדשה",
  "description": "יישום פונקציונליות התחברות",
  "due_date": "2025-03-20T18:00:00Z",
  "status": "TODO",
  "priority": "MEDIUM",
  "assigned_to": 2,
  "owner": 1
}
```

##### תגובה (201 Created)

```json
{
  "id": 2,
  "title": "יישום תכונה חדשה",
  "description": "יישום פונקציונליות התחברות",
  "created_at": "2025-03-09T15:30:00Z",
  "due_date": "2025-03-20T18:00:00Z",
  "status": "TODO",
  "priority": "MEDIUM",
  "owner": 1,
  "assigned_to": 2,
  "owner_details": {
    "id": 1,
    "username": "example_user",
    "email": "user@example.com"
  },
  "assigned_to_details": {
    "id": 2,
    "username": "another_user",
    "email": "another@example.com"
  }
}
```

##### שגיאות אפשריות

- `400 Bad Request`: חסרים שדות נדרשים
- `401 Unauthorized`: חסר טוקן אימות או טוקן לא תקף

#### קבלת משימה ספציפית

```
GET /api/tasks/{id}/
```

##### תגובה (200 OK)

```json
{
  "id": 2,
  "title": "יישום תכונה חדשה",
  "description": "יישום פונקציונליות התחברות",
  "created_at": "2025-03-09T15:30:00Z",
  "due_date": "2025-03-20T18:00:00Z",
  "status": "TODO",
  "priority": "MEDIUM",
  "owner": 1,
  "assigned_to": 2,
  "owner_details": {
    "id": 1,
    "username": "example_user",
    "email": "user@example.com"
  },
  "assigned_to_details": {
    "id": 2,
    "username": "another_user",
    "email": "another@example.com"
  }
}
```

##### שגיאות אפשריות

- `401 Unauthorized`: חסר טוקן אימות או טוקן לא תקף
- `404 Not Found`: המשימה לא נמצאה או למשתמש אין גישה אליה

#### עדכון משימה

```
PUT /api/tasks/{id}/
```

##### גוף הבקשה (עדכון מלא)

```json
{
  "title": "יישום תכונה חדשה",
  "description": "תיאור מעודכן עם יותר פרטים",
  "due_date": "2025-03-22T18:00:00Z",
  "status": "IN_PROGRESS",
  "priority": "HIGH",
  "assigned_to": 2,
  "owner": 1
}
```

##### תגובה (200 OK)

אובייקט המשימה עם השדות המעודכנים.

##### עדכון חלקי

```
PATCH /api/tasks/{id}/
```

##### גוף הבקשה (עדכון חלקי)

```json
{
  "status": "IN_PROGRESS",
  "priority": "HIGH"
}
```

##### תגובה (200 OK)

אובייקט המשימה עם השדות המעודכנים.

##### שגיאות אפשריות

- `400 Bad Request`: נתונים לא תקינים
- `401 Unauthorized`: חסר טוקן אימות או טוקן לא תקף
- `404 Not Found`: המשימה לא נמצאה או למשתמש אין גישה אליה

#### מחיקת משימה

```
DELETE /api/tasks/{id}/
```

##### תגובה (204 No Content)

אין גוף תגובה.

##### שגיאות אפשריות

- `401 Unauthorized`: חסר טוקן אימות או טוקן לא תקף
- `404 Not Found`: המשימה לא נמצאה או למשתמש אין גישה אליה

## קודי סטטוס

| קוד סטטוס  | תיאור                                               |
|------------|----------------------------------------------------|
| 200        | OK - הבקשה בוצעה בהצלחה                           |
| 201        | Created - המשאב נוצר בהצלחה                       |
| 204        | No Content - הבקשה בוצעה בהצלחה (אין גוף תגובה)   |
| 400        | Bad Request - בקשה לא תקינה או כשל בוולידציה      |
| 401        | Unauthorized - נדרש אימות או האימות נכשל          |
| 403        | Forbidden - למשתמש אין הרשאות מתאימות              |
| 404        | Not Found - המשאב לא נמצא                          |
| 500        | Internal Server Error - השרת נתקל בשגיאה           |

## מודלים

### משימה (Task)

| שדה        | סוג      | תיאור                                      |
|------------|----------|-------------------------------------------|
| id         | מספר שלם | מזהה ייחודי                                |
| title      | מחרוזת   | כותרת המשימה                              |
| description| מחרוזת   | תיאור מפורט של המשימה                     |
| created_at | תאריך/שעה| מועד יצירת המשימה (נוצר אוטומטית)         |
| due_date   | תאריך/שעה| מועד היעד של המשימה                       |
| status     | מחרוזת   | סטטוס המשימה (TODO, IN_PROGRESS, DONE)    |
| priority   | מחרוזת   | רמת עדיפות (LOW, MEDIUM, HIGH)             |
| owner      | מספר שלם | מזהה של המשתמש שיצר את המשימה             |
| assigned_to| מספר שלם | מזהה של המשתמש שהוקצה למשימה              |

## דוגמאות

### דוגמה: תהליך עבודה מלא של משתמש

1. הרשמת משתמש חדש

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "email": "newuser@example.com", "password": "password123"}'
```

2. התחברות

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "password": "password123"}'
```

3. יצירת משימה (באמצעות טוקן גישה)

```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..." \
  -H "Content-Type: application/json" \
  -d '{"title": "משימה חדשה", "description": "תיאור המשימה", "due_date": "2025-04-01T12:00:00Z", "status": "TODO", "priority": "MEDIUM", "assigned_to": 1, "owner": 1}'
```

4. הצגת כל המשימות

```bash
curl -X GET http://localhost:8000/api/tasks/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
```

5. סינון משימות לפי סטטוס

```bash
curl -X GET "http://localhost:8000/api/tasks/?status=TODO" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
```

## הערות

- טוקני גישה פגים לאחר 15 דקות. יש להשתמש בטוקן רענון כדי לקבל טוקן גישה חדש.
- כל שדות התאריך והשעה צריכים להיות בפורמט ISO 8601 עם מידע על אזור זמן.
- לסינון וחיפוש משימות, ניתן לשלב מספר פרמטרים בשאילתה. 