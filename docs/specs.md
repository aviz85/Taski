# אפיון אפליקציית ניהול משימות

## ארכיטקטורה כללית
- Django Backend + DRF
- Frontend: HTML, CSS, JavaScript (Vanilla)
- תקשורת: REST API
- אבטחה: JWT + CSRF Protection
- CORS מוגדר עבור פיתוח לוקאלי

## מודלים
### User
- username (string)
- email (email)
- password (hashed)
- created_at (datetime)
- is_active (boolean)

### Task
- title (string)
- description (text)
- created_at (datetime)
- due_date (datetime)
- status (enum: TODO, IN_PROGRESS, DONE)
- priority (enum: LOW, MEDIUM, HIGH)
- owner (FK -> User)
- assigned_to (FK -> User)

## Endpoints
### Authentication
```
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/logout/
POST /api/auth/refresh/
```

### Tasks
```
GET /api/tasks/
POST /api/tasks/
GET /api/tasks/{id}/
PUT /api/tasks/{id}/
DELETE /api/tasks/{id}/
```

## אבטחה
### JWT
- Access Token (תוקף: 15 דקות)
- Refresh Token (תוקף: 7 ימים)
- שמירת טוקנים ב-localStorage

### CSRF
- CSRF Token בכל בקשת POST/PUT/DELETE
- הגדרת CSRF_TRUSTED_ORIGINS בדג'נגו

### CORS
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
CORS_ALLOW_CREDENTIALS = True
```

## מבנה תיקיות
```
project/
├── backend/
│   ├── manage.py
│   ├── core/
│   ├── tasks/
│   └── authentication/
├── frontend/
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── assets/
└── docs/
    └── task_manager_spec.md
```

## פונקציונליות Frontend
### דפים
- דף התחברות/הרשמה
- דף ראשי עם רשימת משימות
- דף יצירת/עריכת משימה
- דף פרופיל משתמש

### תכונות
- סינון משימות לפי סטטוס/עדיפות
- חיפוש משימות
- מיון לפי תאריך/עדיפות
- תצוגת לוח זמנים
- התראות על משימות שמועדן מתקרב

## הגדרות Django
### Required Apps
```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',
    'tasks',
    'authentication',
]
```

### DRF Settings
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}
```

## שלבי פיתוח מומלצים
1. הקמת פרויקט Django בסיסי
2. הגדרת מודלים ומיגרציות
3. יישום אותנטיקציה
4. יישום API למשימות
5. פיתוח ממשק משתמש בסיסי
6. אינטגרציה של Frontend ו-Backend
7. הוספת תכונות מתקדמות
8. בדיקות ותיקון באגים