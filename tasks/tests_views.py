from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from tasks.models import Task, ChecklistItem, TaskDependency
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


class ChecklistItemViewSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create users for testing
        cls.user1 = User.objects.create_user(username='testuser1', password='12345', email='user1@example.com')
        cls.user2 = User.objects.create_user(username='testuser2', password='12345', email='user2@example.com')
        
        # Create tasks for testing
        cls.task = Task.objects.create(
            title='Task with Checklist',
            description='This is a task with a checklist',
            due_date=timezone.now() + datetime.timedelta(days=7),
            status='TODO',
            priority='MEDIUM',
            owner=cls.user1,
            assigned_to=cls.user2
        )
        
        # Create some initial checklist items
        cls.item1 = ChecklistItem.objects.create(
            task=cls.task,
            text='First step',
            position=1
        )
        
        cls.item2 = ChecklistItem.objects.create(
            task=cls.task,
            text='Second step',
            position=2
        )
    
    def setUp(self):
        self.client = APIClient()
    
    def test_list_checklist_items(self):
        """Test retrieving all checklist items for a task."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('task-checklist-list', kwargs={'task_pk': self.task.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        item_texts = [item['text'] for item in response.data]
        self.assertIn('First step', item_texts)
        self.assertIn('Second step', item_texts)
    
    def test_get_checklist_item(self):
        """Test retrieving a specific checklist item."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('task-checklist-detail', kwargs={'task_pk': self.task.id, 'pk': self.item1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['text'], 'First step')
        self.assertEqual(response.data['position'], 1)
    
    def test_create_checklist_item(self):
        """Test creating a new checklist item."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('task-checklist-list', kwargs={'task_pk': self.task.id})
        
        data = {
            'text': 'New checklist item',
            'task': self.task.id  # Include task ID in request
        }
        
        response = self.client.post(url, data, format='json')
        
        # Debug output if needed
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Error response: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['text'], 'New checklist item')
        self.assertEqual(response.data['is_completed'], False)
        
        # Check that position is automatically set to 3 (after existing items)
        self.assertEqual(response.data['position'], 3)
        
        # Verify it's in the database
        self.assertTrue(ChecklistItem.objects.filter(id=response.data['id']).exists())
    
    def test_update_checklist_item(self):
        """Test updating a checklist item."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('task-checklist-detail', kwargs={'task_pk': self.task.id, 'pk': self.item1.id})
        
        data = {
            'text': 'Updated first step'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['text'], 'Updated first step')
        
        # Position and completion status should remain unchanged
        self.assertEqual(response.data['position'], 1)
        self.assertEqual(response.data['is_completed'], False)
    
    def test_delete_checklist_item(self):
        """Test deleting a checklist item."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('task-checklist-detail', kwargs={'task_pk': self.task.id, 'pk': self.item1.id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ChecklistItem.objects.filter(id=self.item1.id).exists())
    
    def test_complete_checklist_item(self):
        """Test marking a checklist item as complete."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('task-checklist-complete', kwargs={'task_pk': self.task.id, 'pk': self.item1.id})
        
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_completed'])
        
        # Verify in database
        item = ChecklistItem.objects.get(id=self.item1.id)
        self.assertTrue(item.is_completed)
    
    def test_incomplete_checklist_item(self):
        """Test marking a checklist item as incomplete."""
        # First mark it as complete
        self.item1.is_completed = True
        self.item1.save()
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('task-checklist-incomplete', kwargs={'task_pk': self.task.id, 'pk': self.item1.id})
        
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_completed'])
        
        # Verify in database
        item = ChecklistItem.objects.get(id=self.item1.id)
        self.assertFalse(item.is_completed)
    
    def test_reorder_checklist_items(self):
        """Test reordering checklist items."""
        # Add a third item
        item3 = ChecklistItem.objects.create(
            task=self.task,
            text='Third step',
            position=3
        )
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('task-checklist-reorder', kwargs={'task_pk': self.task.id})
        
        # Reorder to: item3, item1, item2
        data = {
            'order': [item3.id, self.item1.id, self.item2.id]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the new order in the database
        items = ChecklistItem.objects.filter(task=self.task).order_by('position')
        self.assertEqual(items[0].id, item3.id)
        self.assertEqual(items[0].position, 1)
        self.assertEqual(items[1].id, self.item1.id)
        self.assertEqual(items[1].position, 2)
        self.assertEqual(items[2].id, self.item2.id)
        self.assertEqual(items[2].position, 3)
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access checklist items."""
        url = reverse('task-checklist-list', kwargs={'task_pk': self.task.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthorized_access(self):
        """Test that users who are not owners or assignees cannot access checklist items."""
        # Create a third user with no association to the task
        user3 = User.objects.create_user(username='testuser3', password='12345', email='user3@example.com')
        
        self.client.force_authenticate(user=user3)
        url = reverse('task-checklist-list', kwargs={'task_pk': self.task.id})
        
        # Try to get the list (should return empty list)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        
        # Try to create an item (this should be blocked at the view level)
        data = {
            'text': 'Unauthorized item',
            'task': self.task.id  # Include task ID in request
        }
        
        response = self.client.post(url, data, format='json')
        
        # Either HTTP_403_FORBIDDEN or HTTP_400_BAD_REQUEST is acceptable
        # since authorization may be happening at different levels
        self.assertIn(response.status_code, 
                      [status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST]) 


class TaskDependencyViewSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create users for testing
        cls.user1 = User.objects.create_user(username='testuser1', password='12345', email='user1@example.com')
        cls.user2 = User.objects.create_user(username='testuser2', password='12345', email='user2@example.com')
        cls.user3 = User.objects.create_user(username='testuser3', password='12345', email='user3@example.com')
        
        # Create tasks for testing
        cls.task1 = Task.objects.create(
            title='Task 1',
            description='First task',
            due_date=timezone.now() + datetime.timedelta(days=7),
            status='TODO',
            priority='MEDIUM',
            owner=cls.user1,
            assigned_to=cls.user2
        )
        
        cls.task2 = Task.objects.create(
            title='Task 2',
            description='Second task',
            due_date=timezone.now() + datetime.timedelta(days=10),
            status='TODO',
            priority='HIGH',
            owner=cls.user1,
            assigned_to=cls.user2
        )
        
        cls.task3 = Task.objects.create(
            title='Task 3',
            description='Third task',
            due_date=timezone.now() + datetime.timedelta(days=14),
            status='TODO',
            priority='LOW',
            owner=cls.user3,  # Different owner
            assigned_to=cls.user3
        )
        
        # Create a dependency
        cls.dependency = TaskDependency.objects.create(
            task=cls.task2,
            depends_on=cls.task1,
            created_by=cls.user1,
            notes='Task 2 depends on Task 1'
        )
    
    def setUp(self):
        self.client = APIClient()
    
    def test_list_dependencies(self):
        """Test retrieving all dependencies for a task."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('task-dependency-list', kwargs={'task_pk': self.task2.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['notes'], 'Task 2 depends on Task 1')
    
    def test_get_dependency(self):
        """Test retrieving a specific dependency."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('task-dependency-detail', kwargs={'task_pk': self.task2.id, 'pk': self.dependency.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['notes'], 'Task 2 depends on Task 1')
        self.assertTrue(response.data['active'])
    
    def test_create_dependency(self):
        """Test creating a new dependency."""
        self.client.force_authenticate(user=self.user1)
        
        # Create two new tasks owned by user1
        task4 = Task.objects.create(
            title='Task 4',
            description='Fourth task',
            due_date=timezone.now() + datetime.timedelta(days=14),
            status='TODO',
            priority='MEDIUM',
            owner=self.user1,
            assigned_to=self.user2
        )
        
        task5 = Task.objects.create(
            title='Task 5',
            description='Fifth task',
            due_date=timezone.now() + datetime.timedelta(days=21),
            status='TODO',
            priority='LOW',
            owner=self.user1,
            assigned_to=self.user2
        )
        
        url = reverse('task-dependency-list', kwargs={'task_pk': task4.id})
        
        data = {
            'task': task4.id,
            'depends_on': task5.id,  # Using task5 which is owned by user1
            'notes': 'Task 4 depends on Task 5'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Debug output to understand failures
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Error response for create dependency: {response.status_code} - {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['notes'], 'Task 4 depends on Task 5')
        self.assertTrue(response.data['active'])
        
        # Verify it's in the database
        self.assertTrue(TaskDependency.objects.filter(id=response.data['id']).exists())
    
    def test_update_dependency(self):
        """Test updating a dependency."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('task-dependency-detail', kwargs={'task_pk': self.task2.id, 'pk': self.dependency.id})
        
        data = {
            'notes': 'Updated dependency notes',
            'task': self.task2.id,  # Include task ID explicitly
            'depends_on': self.task1.id  # Include depends_on ID explicitly
        }
        
        response = self.client.patch(url, data, format='json')
        
        # Debug output to understand failures
        if response.status_code != status.HTTP_200_OK:
            print(f"Error response for update dependency: {response.status_code} - {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['notes'], 'Updated dependency notes')
        
        # Refresh from database and verify update
        self.dependency.refresh_from_db()
        self.assertEqual(self.dependency.notes, 'Updated dependency notes')
    
    def test_delete_dependency(self):
        """Test deleting a dependency."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('task-dependency-detail', kwargs={'task_pk': self.task2.id, 'pk': self.dependency.id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify it's removed from the database
        self.assertFalse(TaskDependency.objects.filter(id=self.dependency.id).exists())
    
    def test_toggle_dependency(self):
        """Test toggling a dependency's active status."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('task-dependency-toggle', kwargs={'task_pk': self.task2.id, 'pk': self.dependency.id})
        
        # Initially active
        self.assertTrue(self.dependency.active)
        
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['active'])
        
        # Toggle back to active
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['active'])
    
    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access dependencies."""
        self.client.force_authenticate(user=self.user3)  # Use a user not associated with the task
        url = reverse('task-dependency-list', kwargs={'task_pk': self.task2.id})
        
        response = self.client.get(url)
        
        # Should return an empty list, not 403 Forbidden (per the viewset implementation)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_task_blockers_endpoint(self):
        """Test the blockers endpoint that shows tasks blocking the current task."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('task-blockers', kwargs={'pk': self.task2.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.task1.id)
    
    def test_task_blocked_endpoint(self):
        """Test the blocked endpoint that shows tasks blocked by the current task."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('task-blocked', kwargs={'pk': self.task1.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.task2.id) 