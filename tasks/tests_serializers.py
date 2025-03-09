from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from tasks.models import Task
from tasks.serializers import TaskSerializer, UserSerializer
import datetime
import json

class TaskSerializerTest(TestCase):
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
    
    def test_task_serializer(self):
        """בדיקה שהסריאלייזר מחזיר את כל השדות הנדרשים"""
        serializer = TaskSerializer(instance=self.task)
        data = serializer.data
        
        # בדיקת שדות בסיסיים
        self.assertEqual(data['title'], 'Test Task')
        self.assertEqual(data['description'], 'This is a test task')
        self.assertEqual(data['status'], 'TODO')
        self.assertEqual(data['priority'], 'MEDIUM')
        
        # בדיקת קשרים למשתמשים
        self.assertEqual(data['owner'], self.user1.id)
        self.assertEqual(data['assigned_to'], self.user2.id)
        
        # בדיקת שדות המשתמשים המורחבים
        self.assertEqual(data['owner_details']['username'], 'testuser1')
        self.assertEqual(data['assigned_to_details']['username'], 'testuser2')
    
    def test_task_serializer_validation(self):
        """בדיקת ולידציה של הסריאלייזר"""
        data = {
            'title': '',
            'description': 'Test description',
            'due_date': timezone.now() + timezone.timedelta(days=5),
            'status': 'INVALID',
            'priority': 'SUPER_HIGH',
            'owner': self.user1.id,
            'assigned_to': self.user2.id
        }
        
        serializer = TaskSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
        self.assertIn('status', serializer.errors)
        self.assertIn('priority', serializer.errors)
        
    def test_task_serializer_create_with_tags_list(self):
        """Test creating a task with tags_list."""
        data = {
            'title': 'New Task with Tags',
            'description': 'Testing tags creation',
            'due_date': timezone.now() + timezone.timedelta(days=5),
            'status': 'TODO',
            'priority': 'MEDIUM',
            'owner': self.user1.id,
            'assigned_to': self.user2.id,
            'tags_list': ['important', 'frontend', 'bug']
        }
        
        serializer = TaskSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        task = serializer.save()
        
        # Verify tags were correctly saved
        self.assertEqual(task.tags, 'important,frontend,bug')
        self.assertEqual(task.get_tags_list(), ['important', 'frontend', 'bug'])
        
    def test_task_serializer_update_with_tags_list(self):
        """Test updating a task with tags_list."""
        # First create a task with initial tags
        task = Task.objects.create(
            title='Task to Update',
            description='Initial description',
            due_date=timezone.now() + timezone.timedelta(days=5),
            status='TODO',
            priority='MEDIUM',
            owner=self.user1,
            assigned_to=self.user2,
            tags='old,tags'
        )
        
        # Update data with new tags
        data = {
            'title': 'Updated Task',
            'description': 'Updated description',
            'tags_list': ['new', 'updated', 'tags']
        }
        
        serializer = TaskSerializer(task, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_task = serializer.save()
        
        # Verify the update worked
        self.assertEqual(updated_task.title, 'Updated Task')
        self.assertEqual(updated_task.description, 'Updated description')
        self.assertEqual(updated_task.tags, 'new,updated,tags')
        self.assertEqual(updated_task.get_tags_list(), ['new', 'updated', 'tags'])

class UserSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='user@example.com',
            password='password123'
        )
    
    def test_user_serializer(self):
        """בדיקת הסריאלייזר של המשתמש"""
        serializer = UserSerializer(instance=self.user)
        data = serializer.data
        
        # וידוא שהסריאלייזר מכיל את השדות הנכונים
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'user@example.com')
        
        # וידוא שסיסמה לא כלולה
        self.assertNotIn('password', data) 