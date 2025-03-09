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
        task1 = self.task
        task2 = Task.objects.create(
            title='Test Task 2',
            description='This is another test task',
            due_date=timezone.now() + timezone.timedelta(days=7),
            status='TODO',
            priority='HIGH',
            owner=self.user1,
            assigned_to=self.user2
        )
        
        tasks = Task.objects.all()
        self.assertEqual(tasks[0], task2)  # newer task should be first due to ordering
        self.assertEqual(tasks[1], task1)
    
    def test_get_tags_list_empty(self):
        """Test get_tags_list with empty tags."""
        task = Task.objects.create(
            title='Task with no tags',
            description='Testing tag methods',
            due_date=timezone.now() + timezone.timedelta(days=5),
            status='TODO',
            priority='MEDIUM',
            owner=self.user1,
            assigned_to=self.user2,
            tags=''
        )
        
        self.assertEqual(task.get_tags_list(), [])
        
    def test_get_tags_list_with_tags(self):
        """Test get_tags_list with tags."""
        task = Task.objects.create(
            title='Task with tags',
            description='Testing tag methods',
            due_date=timezone.now() + timezone.timedelta(days=5),
            status='TODO',
            priority='MEDIUM',
            owner=self.user1,
            assigned_to=self.user2,
            tags='urgent, feature, bug'
        )
        
        expected_tags = ['urgent', 'feature', 'bug']
        self.assertEqual(task.get_tags_list(), expected_tags)
        
    def test_set_tags_list_with_tags(self):
        """Test set_tags_list with tags."""
        task = Task.objects.create(
            title='Setting tags task',
            description='Testing set_tags_list method',
            due_date=timezone.now() + timezone.timedelta(days=5),
            status='TODO',
            priority='MEDIUM',
            owner=self.user1,
            assigned_to=self.user2
        )
        
        new_tags = ['priority', 'backend', 'v2']
        task.set_tags_list(new_tags)
        
        self.assertEqual(task.tags, 'priority,backend,v2')
        self.assertEqual(task.get_tags_list(), new_tags)
        
    def test_set_tags_list_empty(self):
        """Test set_tags_list with empty list."""
        task = Task.objects.create(
            title='Setting empty tags',
            description='Testing set_tags_list with empty list',
            due_date=timezone.now() + timezone.timedelta(days=5),
            status='TODO',
            priority='MEDIUM',
            owner=self.user1,
            assigned_to=self.user2,
            tags='old,tags'
        )
        
        task.set_tags_list([])
        
        self.assertEqual(task.tags, "")
        self.assertEqual(task.get_tags_list(), []) 