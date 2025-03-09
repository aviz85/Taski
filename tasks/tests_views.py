from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from tasks.models import Task
import datetime
import json

class TaskViewSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # יצירת משתמשים לבדיקה
        cls.user1 = User.objects.create_user(username='testuser1', password='12345', email='user1@example.com')
        cls.user2 = User.objects.create_user(username='testuser2', password='12345', email='user2@example.com')
        
        # יצירת משימות לבדיקה
        cls.task1 = Task.objects.create(
            title='Test Task 1',
            description='This is test task 1',
            due_date=timezone.now() + datetime.timedelta(days=7),
            status='TODO',
            priority='MEDIUM',
            owner=cls.user1,
            assigned_to=cls.user1
        )
        
        cls.task2 = Task.objects.create(
            title='Test Task 2',
            description='This is test task 2',
            due_date=timezone.now() + datetime.timedelta(days=5),
            status='IN_PROGRESS',
            priority='HIGH',
            owner=cls.user1,
            assigned_to=cls.user2
        )
        
        cls.task3 = Task.objects.create(
            title='Test Task 3',
            description='This is test task 3',
            due_date=timezone.now() + datetime.timedelta(days=3),
            status='DONE',
            priority='LOW',
            owner=cls.user2,
            assigned_to=cls.user1
        )
    
    def setUp(self):
        self.client = APIClient()
    
    def test_list_tasks_authenticated(self):
        """בדיקה שמשתמש מאומת יכול לראות את המשימות שלו"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('task-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # המשתמש 1 הוא הבעלים של 2 משימות ומשויך למשימה 3
        self.assertEqual(len(response.data), 3)
        
        # וידוא שהתוצאות מכילות את המשימות הנכונות
        task_ids = [task['id'] for task in response.data]
        self.assertIn(self.task1.id, task_ids)
        self.assertIn(self.task2.id, task_ids)
        self.assertIn(self.task3.id, task_ids)
    
    def test_list_tasks_unauthenticated(self):
        """בדיקה שמשתמש לא מאומת לא יכול לראות משימות"""
        response = self.client.get(reverse('task-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_retrieve_task(self):
        """בדיקה שמשתמש יכול לראות משימה ספציפית"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('task-detail', args=[self.task1.id]))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Task 1')
        self.assertEqual(response.data['status'], 'TODO')
    
    def test_create_task(self):
        """בדיקת יצירת משימה חדשה"""
        self.client.force_authenticate(user=self.user1)
        
        due_date = timezone.now() + datetime.timedelta(days=10)
        
        new_task_data = {
            'title': 'New Task',
            'description': 'This is a new task',
            'due_date': due_date.strftime('%Y-%m-%dT%H:%M:%S%z'),  # פורמט תאריך סטנדרטי
            'status': 'TODO',
            'priority': 'MEDIUM',
            'assigned_to': self.user1.id,
            'owner': self.user1.id  # הוספת שדה הבעלים
        }
        
        response = self.client.post(reverse('task-list'), new_task_data, format='json')
        
        # הדפסת פרטי השגיאה אם יש
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Error response: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Task')
        self.assertEqual(response.data['description'], 'This is a new task')
        self.assertEqual(response.data['status'], 'TODO')
        
        # וידוא שהבעלים הוא המשתמש המחובר
        self.assertEqual(response.data['owner'], self.user1.id)
    
    def test_update_task(self):
        """בדיקת עדכון משימה קיימת"""
        self.client.force_authenticate(user=self.user1)
        
        update_data = {
            'title': 'Updated Task',
            'status': 'IN_PROGRESS',
            'priority': 'HIGH',
            'due_date': (timezone.now() + datetime.timedelta(days=5)).isoformat(),
            'assigned_to': self.user2.id
        }
        
        response = self.client.patch(
            reverse('task-detail', args=[self.task1.id]),
            update_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Task')
        self.assertEqual(response.data['status'], 'IN_PROGRESS')
        self.assertEqual(response.data['priority'], 'HIGH')
    
    def test_delete_task(self):
        """בדיקת מחיקת משימה"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.delete(reverse('task-detail', args=[self.task1.id]))
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # וידוא שהמשימה אכן נמחקה
        self.assertFalse(Task.objects.filter(id=self.task1.id).exists())
    
    def test_filter_tasks(self):
        """בדיקת סינון משימות"""
        self.client.force_authenticate(user=self.user1)
        
        # סינון לפי סטטוס
        response = self.client.get(f"{reverse('task-list')}?status=TODO")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Task 1')
        
        # סינון לפי עדיפות
        response = self.client.get(f"{reverse('task-list')}?priority=HIGH")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Task 2')
    
    def test_search_tasks(self):
        """בדיקת חיפוש משימות"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(f"{reverse('task-list')}?search=test task 2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Task 2') 