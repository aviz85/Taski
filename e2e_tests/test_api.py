import unittest
import requests
import random
import string
from datetime import datetime, timedelta

class TaskiAPITests(unittest.TestCase):
    """
    בדיקות API למערכת Taski
    """
    
    @classmethod
    def setUpClass(cls):
        """הגדרת נתוני בדיקה ו-URL בסיסי"""
        cls.base_url = "http://localhost:8000/api"
        
        # יצירת פרטי משתמש אקראיים לבדיקות
        rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        cls.test_username = f"apitest_{rand_suffix}"
        cls.test_email = f"apitest_{rand_suffix}@example.com"
        cls.test_password = "ApiTest123"
        
        # משתנים לשמירת מזהים ונתונים
        cls.access_token = None
        cls.refresh_token = None
        cls.user_id = None
        cls.task_id = None
    
    def test_01_register_user(self):
        """בדיקת הרשמת משתמש חדש"""
        url = f"{self.base_url}/auth/register/"
        data = {
            "username": self.test_username,
            "email": self.test_email,
            "password": self.test_password
        }
        
        response = requests.post(url, json=data)
        self.assertEqual(response.status_code, 201, f"נכשל בהרשמת משתמש חדש: {response.content}")
        
        # שמירת הטוקנים ומזהה המשתמש לשימוש בהמשך
        response_data = response.json()
        self.__class__.access_token = response_data['tokens']['access']
        self.__class__.refresh_token = response_data['tokens']['refresh']
        self.__class__.user_id = response_data['user']['id']
        
        # בדיקה שהתקבלו הנתונים הנכונים
        self.assertEqual(response_data['user']['username'], self.test_username)
        self.assertEqual(response_data['user']['email'], self.test_email)
    
    def test_02_login(self):
        """בדיקת התחברות למערכת"""
        url = f"{self.base_url}/auth/login/"
        data = {
            "username": self.test_username,
            "password": self.test_password
        }
        
        response = requests.post(url, json=data)
        self.assertEqual(response.status_code, 200, f"נכשל בהתחברות: {response.content}")
        
        # שמירת הטוקנים לשימוש בהמשך
        response_data = response.json()
        self.__class__.access_token = response_data['access']
        self.__class__.refresh_token = response_data['refresh']
        
        # בדיקה שהתקבלו טוקנים
        self.assertIn('access', response_data)
        self.assertIn('refresh', response_data)
    
    def test_03_refresh_token(self):
        """בדיקת רענון טוקן"""
        url = f"{self.base_url}/auth/refresh/"
        data = {
            "refresh": self.__class__.refresh_token
        }
        
        response = requests.post(url, json=data)
        self.assertEqual(response.status_code, 200, f"נכשל ברענון טוקן: {response.content}")
        
        # שמירת הטוקן החדש
        response_data = response.json()
        self.__class__.access_token = response_data['access']
        
        # בדיקה שהתקבל טוקן גישה חדש
        self.assertIn('access', response_data)
    
    def test_04_create_task(self):
        """בדיקת יצירת משימה חדשה"""
        url = f"{self.base_url}/tasks/"
        
        # יצירת נתוני משימה לבדיקה
        due_date = (datetime.now() + timedelta(days=3)).isoformat()
        data = {
            "title": f"API Test Task {random.randint(1000, 9999)}",
            "description": "This is a test task created via API tests",
            "due_date": due_date,
            "status": "TODO",
            "priority": "HIGH",
            "assigned_to": self.__class__.user_id,
            "owner": self.__class__.user_id
        }
        
        headers = {
            "Authorization": f"Bearer {self.__class__.access_token}"
        }
        
        response = requests.post(url, json=data, headers=headers)
        self.assertEqual(response.status_code, 201, f"נכשל ביצירת משימה חדשה: {response.content}")
        
        # שמירת מזהה המשימה
        response_data = response.json()
        self.__class__.task_id = response_data['id']
        
        # בדיקה שהמשימה נוצרה עם הנתונים הנכונים
        self.assertEqual(response_data['title'], data['title'])
        self.assertEqual(response_data['description'], data['description'])
        self.assertEqual(response_data['status'], data['status'])
        self.assertEqual(response_data['priority'], data['priority'])
        self.assertEqual(response_data['owner'], data['owner'])
        self.assertEqual(response_data['assigned_to'], data['assigned_to'])
    
    def test_05_get_tasks(self):
        """בדיקת קבלת רשימת משימות"""
        url = f"{self.base_url}/tasks/"
        
        headers = {
            "Authorization": f"Bearer {self.__class__.access_token}"
        }
        
        response = requests.get(url, headers=headers)
        self.assertEqual(response.status_code, 200, f"נכשל בקבלת רשימת משימות: {response.content}")
        
        # בדיקה שרשימת המשימות אינה ריקה
        tasks = response.json()
        self.assertTrue(len(tasks) > 0, "רשימת המשימות ריקה למרות שנוצרה משימה חדשה")
        
        # בדיקה שהמשימה שיצרנו נמצאת ברשימה
        found = False
        for task in tasks:
            if task['id'] == self.__class__.task_id:
                found = True
                break
        
        self.assertTrue(found, f"המשימה עם ID {self.__class__.task_id} לא נמצאה ברשימת המשימות")
    
    def test_06_get_single_task(self):
        """בדיקת קבלת משימה בודדת"""
        url = f"{self.base_url}/tasks/{self.__class__.task_id}/"
        
        headers = {
            "Authorization": f"Bearer {self.__class__.access_token}"
        }
        
        response = requests.get(url, headers=headers)
        self.assertEqual(response.status_code, 200, f"נכשל בקבלת משימה בודדת: {response.content}")
        
        # בדיקה שהתקבלה המשימה הנכונה
        task = response.json()
        self.assertEqual(task['id'], self.__class__.task_id)
    
    def test_07_update_task(self):
        """בדיקת עדכון משימה"""
        url = f"{self.base_url}/tasks/{self.__class__.task_id}/"
        
        # עדכון המשימה
        updated_data = {
            "status": "IN_PROGRESS",
            "description": "This task was updated via API tests",
            "owner": self.__class__.user_id,
            "assigned_to": self.__class__.user_id
        }
        
        headers = {
            "Authorization": f"Bearer {self.__class__.access_token}"
        }
        
        response = requests.patch(url, json=updated_data, headers=headers)
        self.assertEqual(response.status_code, 200, f"נכשל בעדכון משימה: {response.content}")
        
        # בדיקה שהמשימה עודכנה כראוי
        updated_task = response.json()
        self.assertEqual(updated_task['status'], updated_data['status'])
        self.assertEqual(updated_task['description'], updated_data['description'])
    
    def test_08_filter_tasks(self):
        """בדיקת סינון משימות"""
        url = f"{self.base_url}/tasks/?status=IN_PROGRESS"
        
        headers = {
            "Authorization": f"Bearer {self.__class__.access_token}"
        }
        
        response = requests.get(url, headers=headers)
        self.assertEqual(response.status_code, 200, f"נכשל בסינון משימות: {response.content}")
        
        # בדיקה שהסינון עובד כראוי
        filtered_tasks = response.json()
        self.assertTrue(len(filtered_tasks) > 0, "רשימת המשימות המסוננות ריקה")
        
        # בדיקה שכל המשימות בתוצאות הסינון הן במצב "בתהליך"
        for task in filtered_tasks:
            self.assertEqual(task['status'], "IN_PROGRESS", f"משימה עם סטטוס '{task['status']}' נמצאה בסינון למשימות 'IN_PROGRESS'")
    
    def test_09_search_tasks(self):
        """בדיקת חיפוש משימות"""
        # בקשת חיפוש עם מילת מפתח ייחודית מהתיאור העדכני
        url = f"{self.base_url}/tasks/?search=updated"
        
        headers = {
            "Authorization": f"Bearer {self.__class__.access_token}"
        }
        
        response = requests.get(url, headers=headers)
        self.assertEqual(response.status_code, 200, f"נכשל בחיפוש משימות: {response.content}")
        
        # בדיקה שהתקבלו תוצאות חיפוש
        search_results = response.json()
        self.assertTrue(len(search_results) > 0, "לא נמצאו תוצאות לחיפוש")
        
        # בדיקה שהמשימה המעודכנת נמצאת בתוצאות החיפוש
        found = False
        for task in search_results:
            if task['id'] == self.__class__.task_id:
                found = True
                break
        
        self.assertTrue(found, "המשימה המעודכנת לא נמצאה בתוצאות החיפוש")
    
    def test_10_delete_task(self):
        """בדיקת מחיקת משימה"""
        url = f"{self.base_url}/tasks/{self.__class__.task_id}/"
        
        headers = {
            "Authorization": f"Bearer {self.__class__.access_token}"
        }
        
        response = requests.delete(url, headers=headers)
        self.assertEqual(response.status_code, 204, f"נכשל במחיקת משימה: {response.content}")
        
        # בדיקה שהמשימה אכן נמחקה
        get_response = requests.get(url, headers=headers)
        self.assertEqual(get_response.status_code, 404, "המשימה עדיין קיימת למרות שנמחקה")
    
    def test_11_unauthorized_access(self):
        """בדיקת גישה לא מורשית"""
        url = f"{self.base_url}/tasks/"
        
        # ניסיון גישה ללא טוקן אימות
        response = requests.get(url)
        self.assertEqual(response.status_code, 401, "גישה ללא אימות לא נכשלה כצפוי")
        
        # ניסיון גישה עם טוקן שגוי
        headers = {
            "Authorization": "Bearer invalid_token"
        }
        
        response = requests.get(url, headers=headers)
        self.assertEqual(response.status_code, 401, "גישה עם טוקן שגוי לא נכשלה כצפוי")


if __name__ == '__main__':
    # הרצת הבדיקות בסדר הנכון
    test_suite = unittest.TestSuite()
    test_suite.addTest(TaskiAPITests('test_01_register_user'))
    test_suite.addTest(TaskiAPITests('test_02_login'))
    test_suite.addTest(TaskiAPITests('test_03_refresh_token'))
    test_suite.addTest(TaskiAPITests('test_04_create_task'))
    test_suite.addTest(TaskiAPITests('test_05_get_tasks'))
    test_suite.addTest(TaskiAPITests('test_06_get_single_task'))
    test_suite.addTest(TaskiAPITests('test_07_update_task'))
    test_suite.addTest(TaskiAPITests('test_08_filter_tasks'))
    test_suite.addTest(TaskiAPITests('test_09_search_tasks'))
    test_suite.addTest(TaskiAPITests('test_10_delete_task'))
    test_suite.addTest(TaskiAPITests('test_11_unauthorized_access'))
    
    unittest.TextTestRunner(verbosity=2).run(test_suite) 