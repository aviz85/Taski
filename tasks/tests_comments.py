from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
import datetime
import json
from .models import Task, TaskComment

class TaskCommentAPITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test users
        cls.user1 = User.objects.create_user(username='testuser1', password='12345', email='user1@example.com')
        cls.user2 = User.objects.create_user(username='testuser2', password='12345', email='user2@example.com')
        
        # Create a test task
        cls.task = Task.objects.create(
            title='Test Task',
            description='This is a test task',
            due_date=timezone.now() + datetime.timedelta(days=7),
            status='TODO',
            priority='MEDIUM',
            owner=cls.user1,
            assigned_to=cls.user2
        )
    
    def setUp(self):
        self.client = APIClient()
        
    def test_create_comment_authenticated(self):
        """Test creating a comment when authenticated"""
        # Login as owner of the task
        self.client.force_authenticate(user=self.user1)
        
        # URL for creating a comment on the task
        url = f'/api/tasks/{self.task.id}/comments/'
        
        # Simple comment data
        comment_data = {'content': 'This is a test comment'}
        
        # Print debug info
        print(f"\nAttempting to create comment at URL: {url}")
        print(f"Comment data: {comment_data}")
        
        # Make request
        response = self.client.post(url, comment_data, format='json')
        
        # Debug output
        print(f"Response status: {response.status_code}")
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response data: {response.data}")
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'This is a test comment')
        self.assertEqual(response.data['author'], self.user1.id)
        self.assertEqual(response.data['task'], self.task.id)
        
        # Verify comment was created in database
        self.assertTrue(TaskComment.objects.filter(content='This is a test comment').exists())
        
    def test_create_comment_with_hebrew(self):
        """Test creating a comment with Hebrew text"""
        # Login as owner of the task
        self.client.force_authenticate(user=self.user1)
        
        # URL for creating a comment on the task
        url = f'/api/tasks/{self.task.id}/comments/'
        
        # Comment with Hebrew content
        comment_data = {'content': 'זהו תגובה בעברית'}
        
        # Print debug info
        print(f"\nAttempting to create Hebrew comment at URL: {url}")
        print(f"Comment data: {comment_data}")
        
        # Make request
        response = self.client.post(url, comment_data, format='json')
        
        # Debug output
        print(f"Response status: {response.status_code}")
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response data: {response.data}")
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'זהו תגובה בעברית')
        
    def test_create_comment_without_content(self):
        """Test that creating a comment without content fails"""
        # Login as owner of the task
        self.client.force_authenticate(user=self.user1)
        
        # URL for creating a comment on the task
        url = f'/api/tasks/{self.task.id}/comments/'
        
        # Empty comment data
        comment_data = {'content': ''}
        
        # Make request
        response = self.client.post(url, comment_data, format='json')
        
        # Debug output
        print(f"\nAttempting to create empty comment")
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_create_comment_with_just_task_id(self):
        """Test creating a comment with just content field"""
        # Login as owner of the task
        self.client.force_authenticate(user=self.user1)
        
        # URL for creating a comment on the task
        url = f'/api/tasks/{self.task.id}/comments/'
        
        # Create raw JSON - just the content without any task ID
        raw_data = json.dumps({'content': 'Simple test comment'})
        
        # Print debug info
        print(f"\nAttempting to create comment with raw JSON: {raw_data}")
        
        # Make request with raw JSON and content-type header
        response = self.client.post(
            url, 
            raw_data, 
            content_type='application/json'
        )
        
        # Debug output
        print(f"Response status: {response.status_code}")
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response data: {response.data}")
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Simple test comment')
        
    def test_create_comment_with_missing_content_field(self):
        """Test that creating a comment with missing content field fails"""
        # Login as owner of the task
        self.client.force_authenticate(user=self.user1)
        
        # URL for creating a comment on the task
        url = f'/api/tasks/{self.task.id}/comments/'
        
        # Data with no content field
        comment_data = {}
        
        # Make request
        response = self.client.post(url, comment_data, format='json')
        
        # Debug output
        print(f"\nAttempting to create comment without content field")
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 