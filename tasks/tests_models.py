from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from tasks.models import Task
import datetime

class TaskModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # יצירת משתמשים לבדיקה
        cls.user1 = User.objects.create_user(username='testuser1', password='12345', email='user1@example.com')
        cls.user2 = User.objects.create_user(username='testuser2', password='12345', email='user2@example.com')
        
        # יצירת משימה לבדיקה
        cls.task = Task.objects.create(
            title='Test Task',
            description='This is a test task',
            due_date=timezone.now() + datetime.timedelta(days=7),
            status='TODO',
            priority='MEDIUM',
            owner=cls.user1,
            assigned_to=cls.user2
        )
    
    def test_task_creation(self):
        """בדיקה שהמשימה נוצרה כהלכה"""
        task = Task.objects.get(id=self.task.id)
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.description, 'This is a test task')
        self.assertEqual(task.status, 'TODO')
        self.assertEqual(task.priority, 'MEDIUM')
        self.assertEqual(task.owner, self.user1)
        self.assertEqual(task.assigned_to, self.user2)
    
    def test_task_str_method(self):
        """בדיקה שמתודת ה-__str__ מחזירה את הכותרת"""
        task = Task.objects.get(id=self.task.id)
        self.assertEqual(str(task), task.title)
    
    def test_task_ordering(self):
        """בדיקה שהמשימות מסודרות לפי תאריך יצירה בסדר יורד"""
        # יצירת משימה נוספת עם תאריך יצירה מאוחר יותר
        task2 = Task.objects.create(
            title='Test Task 2',
            description='This is another test task',
            due_date=timezone.now() + datetime.timedelta(days=5),
            status='TODO',
            priority='HIGH',
            owner=self.user1,
            assigned_to=self.user2
        )
        
        tasks = Task.objects.all()
        # המשימה החדשה אמורה להופיע ראשונה בגלל ה-ordering
        self.assertEqual(tasks[0].id, task2.id)
        self.assertEqual(tasks[1].id, self.task.id) 