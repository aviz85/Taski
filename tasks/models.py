from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Task(models.Model):
    STATUS_CHOICES = [
        ('TODO', 'Todo'),
        ('IN_PROGRESS', 'In Progress'),
        ('DONE', 'Done'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    
    # New fields
    tags = models.TextField(blank=True, null=True, help_text="Comma-separated tags")
    duration = models.FloatField(null=True, blank=True, help_text="Estimated duration in hours")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_tags_list(self):
        """Return tags as a list."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def set_tags_list(self, tags_list):
        """Set tags from a list."""
        if not tags_list:
            self.tags = ""
        else:
            self.tags = ",".join(tags_list)


class TaskComment(models.Model):
    """Model for comments on tasks."""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.title}"


class ChecklistItem(models.Model):
    """Model for checklist items within a task."""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='checklist_items')
    text = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position', 'created_at']
        
    def __str__(self):
        status = "✓" if self.is_completed else "○"
        return f"{status} {self.text} ({self.task.title})"


class TaskDependency(models.Model):
    """
    Model for task dependencies.
    
    A dependency represents a relationship where 'task' cannot be started or completed
    until 'depends_on' task is completed.
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='dependencies')
    depends_on = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='dependent_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_dependencies')
    notes = models.TextField(blank=True, null=True, help_text="Optional notes about this dependency")
    active = models.BooleanField(default=True, help_text="Whether this dependency is active")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Task Dependencies"
        # Ensure we don't have duplicate dependencies
        unique_together = ['task', 'depends_on']
        
    def __str__(self):
        return f"{self.task.title} → depends on → {self.depends_on.title}"
    
    def clean(self):
        """Validate that a task cannot depend on itself."""
        if self.task == self.depends_on:
            raise ValidationError("A task cannot depend on itself")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
