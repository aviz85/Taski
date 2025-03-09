import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from tasks.models import Task
import datetime

class TaskManagerIntegrationTest(TestCase):
    """בדיקות אינטגרציה מקיפות למערכת"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('token_obtain_pair')
        self.tasks_url = reverse('task-list')
        
        # נתוני משתמש לבדיקה
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        }

    def test_full_user_workflow(self):
        """בדיקת זרימת עבודה מלאה של משתמש: הרשמה, כניסה, ניהול משימות"""
        
        # 1. הרשמת משתמש חדש
        register_response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        
        # הוצאת נתוני טוקן מהתשובה
        tokens = register_response.data['tokens']
        access_token = tokens['access']
        
        # 2. הגדרת הטוקן בהדרים לבדיקות הבאות
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # 3. יצירת משימה חדשה
        due_date = timezone.now() + datetime.timedelta(days=7)
        task_data = {
            'title': 'Integration Test Task',
            'description': 'This task tests the full integration flow',
            'due_date': due_date.strftime('%Y-%m-%dT%H:%M:%S%z'),
            'status': 'TODO',
            'priority': 'HIGH',
            'assigned_to': register_response.data['user']['id'],
            'owner': register_response.data['user']['id']
        }
        
        create_task_response = self.client.post(self.tasks_url, task_data, format='json')
        
        # הדפסת הודעת שגיאה אם יש
        if create_task_response.status_code != status.HTTP_201_CREATED:
            print(f"Error response: {create_task_response.data}")
        
        self.assertEqual(create_task_response.status_code, status.HTTP_201_CREATED)
        task_id = create_task_response.data['id']
        
        # 4. קבלת רשימת המשימות
        tasks_list_response = self.client.get(self.tasks_url)
        self.assertEqual(tasks_list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(tasks_list_response.data), 1)
        
        # 5. קבלת משימה ספציפית
        task_detail_url = reverse('task-detail', args=[task_id])
        task_detail_response = self.client.get(task_detail_url)
        self.assertEqual(task_detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(task_detail_response.data['title'], 'Integration Test Task')
        
        # 6. עדכון משימה
        update_data = {
            'status': 'IN_PROGRESS',
            'description': 'Updated description during integration test'
        }
        update_response = self.client.patch(task_detail_url, update_data, format='json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['status'], 'IN_PROGRESS')
        self.assertEqual(update_response.data['description'], 'Updated description during integration test')
        
        # 7. סינון משימות
        filter_response = self.client.get(f'{self.tasks_url}?status=IN_PROGRESS')
        self.assertEqual(filter_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(filter_response.data), 1)
        
        # 8. חיפוש משימות
        search_response = self.client.get(f'{self.tasks_url}?search=integration')
        self.assertEqual(search_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(search_response.data), 1)
        
        # 9. מחיקת משימה
        delete_response = self.client.delete(task_detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 10. וידוא שהמשימה נמחקה
        check_deleted_response = self.client.get(task_detail_url)
        self.assertEqual(check_deleted_response.status_code, status.HTTP_404_NOT_FOUND)
        
        # 11. וידוא שרשימת המשימות ריקה
        empty_list_response = self.client.get(self.tasks_url)
        self.assertEqual(empty_list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(empty_list_response.data), 0)
        
    def test_authentication_required(self):
        """בדיקה שפעולות על משימות דורשות אימות"""
        
        # ניסיון לגשת למשימות ללא אימות
        response = self.client.get(self.tasks_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # ניסיון ליצור משימה ללא אימות
        task_data = {
            'title': 'Unauthenticated Task',
            'description': 'This should fail',
            'due_date': (timezone.now() + datetime.timedelta(days=1)).isoformat(),
            'status': 'TODO',
            'priority': 'LOW',
        }
        
        response = self.client.post(self.tasks_url, task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) 