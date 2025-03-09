from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from tasks.models import Task, ChecklistItem, TaskDependency
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

class ChecklistItemModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create users for testing
        cls.user1 = User.objects.create_user(username='testuser1', password='12345', email='user1@example.com')
        cls.user2 = User.objects.create_user(username='testuser2', password='12345', email='user2@example.com')
        
        # Create a task for testing
        cls.task = Task.objects.create(
            title='Test Task with Checklist',
            description='This is a test task with a checklist',
            due_date=timezone.now() + datetime.timedelta(days=7),
            status='TODO',
            priority='MEDIUM',
            owner=cls.user1,
            assigned_to=cls.user2
        )
        
        # Create checklist items
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
        
        cls.item3 = ChecklistItem.objects.create(
            task=cls.task,
            text='Third step',
            position=3,
            is_completed=True
        )
    
    def test_checklist_item_creation(self):
        """Test creating a checklist item."""
        item = ChecklistItem.objects.get(id=self.item1.id)
        
        self.assertEqual(item.text, 'First step')
        self.assertEqual(item.task, self.task)
        self.assertEqual(item.position, 1)
        self.assertFalse(item.is_completed)
    
    def test_checklist_item_str_method(self):
        """Test the __str__ method."""
        item = ChecklistItem.objects.get(id=self.item1.id)
        self.assertEqual(str(item), "○ First step (Test Task with Checklist)")
        
        item = ChecklistItem.objects.get(id=self.item3.id)
        self.assertEqual(str(item), "✓ Third step (Test Task with Checklist)")
    
    def test_checklist_item_ordering(self):
        """Test that checklist items are ordered by position."""
        items = ChecklistItem.objects.filter(task=self.task)
        self.assertEqual(items[0], self.item1)
        self.assertEqual(items[1], self.item2)
        self.assertEqual(items[2], self.item3)
    
    def test_task_relationship(self):
        """Test the relationship between task and checklist items."""
        checklist_items = self.task.checklist_items.all()
        self.assertEqual(checklist_items.count(), 3)
        self.assertTrue(self.item1 in checklist_items)
        
    def test_complete_incomplete(self):
        """Test marking items as complete and incomplete."""
        # Mark as complete
        item = ChecklistItem.objects.get(id=self.item1.id)
        item.is_completed = True
        item.save()
        
        item_refreshed = ChecklistItem.objects.get(id=self.item1.id)
        self.assertTrue(item_refreshed.is_completed)
        
        # Mark as incomplete
        item_refreshed.is_completed = False
        item_refreshed.save()
        
        item_refreshed_again = ChecklistItem.objects.get(id=self.item1.id)
        self.assertFalse(item_refreshed_again.is_completed)

class TaskDependencyModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create users for testing
        cls.user1 = User.objects.create_user(username='testuser1', password='12345', email='user1@example.com')
        cls.user2 = User.objects.create_user(username='testuser2', password='12345', email='user2@example.com')
        
        # Create tasks for testing
        cls.task1 = Task.objects.create(
            title='Task 1',
            description='This is the first task',
            due_date=timezone.now() + datetime.timedelta(days=7),
            status='TODO',
            priority='MEDIUM',
            owner=cls.user1,
            assigned_to=cls.user2
        )
        
        cls.task2 = Task.objects.create(
            title='Task 2',
            description='This is the second task',
            due_date=timezone.now() + datetime.timedelta(days=10),
            status='TODO',
            priority='HIGH',
            owner=cls.user1,
            assigned_to=cls.user2
        )
        
        cls.task3 = Task.objects.create(
            title='Task 3',
            description='This is the third task',
            due_date=timezone.now() + datetime.timedelta(days=14),
            status='TODO',
            priority='LOW',
            owner=cls.user1,
            assigned_to=cls.user2
        )
        
        # Create dependencies
        cls.dependency1 = TaskDependency.objects.create(
            task=cls.task2,
            depends_on=cls.task1,
            created_by=cls.user1,
            notes='Task 2 depends on Task 1'
        )
    
    def test_dependency_creation(self):
        """Test creating a task dependency."""
        dependency = TaskDependency.objects.get(id=self.dependency1.id)
        
        self.assertEqual(dependency.task, self.task2)
        self.assertEqual(dependency.depends_on, self.task1)
        self.assertEqual(dependency.created_by, self.user1)
        self.assertEqual(dependency.notes, 'Task 2 depends on Task 1')
        self.assertTrue(dependency.active)
    
    def test_dependency_string_representation(self):
        """Test the string representation of a task dependency."""
        dependency = TaskDependency.objects.get(id=self.dependency1.id)
        expected_string = f"{self.task2.title} → depends on → {self.task1.title}"
        
        self.assertEqual(str(dependency), expected_string)
    
    def test_dependency_ordering(self):
        """Test that dependencies are ordered by created_at in descending order."""
        # Create another dependency
        dependency2 = TaskDependency.objects.create(
            task=self.task3,
            depends_on=self.task2,
            created_by=self.user1,
            notes='Task 3 depends on Task 2'
        )
        
        dependencies = TaskDependency.objects.all()
        self.assertEqual(dependencies[0], dependency2)  # newer dependency should be first
        self.assertEqual(dependencies[1], self.dependency1)
    
    def test_dependency_relationships(self):
        """Test the relationship between tasks and their dependencies."""
        # Task2 depends on Task1
        self.assertEqual(self.task2.dependencies.first(), self.dependency1)
        
        # Task1 is depended on by Task2
        self.assertEqual(self.task1.dependent_tasks.first(), self.dependency1)
    
    def test_cannot_depend_on_self(self):
        """Test that a task cannot depend on itself."""
        with self.assertRaises(ValidationError):
            TaskDependency.objects.create(
                task=self.task1,
                depends_on=self.task1,
                created_by=self.user1
            )
    
    def test_toggle_active_status(self):
        """Test toggling the active status of a dependency."""
        dependency = TaskDependency.objects.get(id=self.dependency1.id)
        self.assertTrue(dependency.active)  # Initially active
        
        # Toggle to inactive
        dependency.active = False
        dependency.save()
        
        # Refetch from database and check
        refreshed_dependency = TaskDependency.objects.get(id=self.dependency1.id)
        self.assertFalse(refreshed_dependency.active)
        
        # Toggle back to active
        refreshed_dependency.active = True
        refreshed_dependency.save()
        
        # Refetch and check again
        refreshed_again = TaskDependency.objects.get(id=self.dependency1.id)
        self.assertTrue(refreshed_again.active)
    
    def test_unique_together_constraint(self):
        """Test that the same dependency can't be created twice."""
        from django.db import IntegrityError
        
        with self.assertRaises(IntegrityError):
            TaskDependency.objects.create(
                task=self.task2,
                depends_on=self.task1,
                created_by=self.user1,
                notes='Duplicate dependency'
            ) 