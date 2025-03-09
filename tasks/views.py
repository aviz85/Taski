from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Task, TaskComment, ChecklistItem, TaskDependency
from .serializers import TaskSerializer, TaskCommentSerializer, ChecklistItemSerializer, TaskDependencySerializer
import logging

# Set up logger
logger = logging.getLogger(__name__)

# Create your views here.

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'owner', 'assigned_to']
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['created_at', 'due_date', 'priority', 'duration']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Task.objects.filter(
            Q(owner=self.request.user) | Q(assigned_to=self.request.user)
        )
        
        # Filter by tag if provided in query params
        tag = self.request.query_params.get('tag', None)
        if tag is not None:
            queryset = queryset.filter(tags__contains=tag)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['get'])
    def blockers(self, request, pk=None):
        """
        Get all tasks that are blocking the specified task (tasks this task depends on).
        """
        task = self.get_object()
        # Get all active dependencies
        dependencies = task.dependencies.filter(active=True)
        # Extract the tasks that this task depends on
        blocking_tasks = [dep.depends_on for dep in dependencies]
        
        # Serialize these tasks
        serializer = self.get_serializer(blocking_tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def blocked(self, request, pk=None):
        """
        Get all tasks that are blocked by the specified task (tasks that depend on this task).
        """
        task = self.get_object()
        # Get all active dependencies where this task is the one that others depend on
        dependencies = task.dependent_tasks.filter(active=True)
        # Extract the tasks that depend on this task
        blocked_tasks = [dep.task for dep in dependencies]
        
        # Serialize these tasks
        serializer = self.get_serializer(blocked_tasks, many=True)
        return Response(serializer.data)


class TaskCommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing comments on a specific task.
    """
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['created_at']
    
    def get_queryset(self):
        """
        Return comments for the specified task where the user is either 
        the task owner, assigned to the task, or the comment author.
        """
        task_id = self.kwargs.get('task_pk')
        task = get_object_or_404(Task, pk=task_id)
        
        # Check if user is associated with the task
        if not (task.owner == self.request.user or task.assigned_to == self.request.user):
            return TaskComment.objects.none()
            
        return TaskComment.objects.filter(task=task)
    
    def perform_create(self, serializer):
        """
        Create a new comment, automatically setting the task and author.
        """
        task_id = self.kwargs.get('task_pk')
        task = get_object_or_404(Task, pk=task_id)
        
        # Check if user is associated with the task
        if not (task.owner == self.request.user or task.assigned_to == self.request.user):
            # This should be prevented by permissions, but check anyway
            raise PermissionDenied("You don't have permission to comment on this task")
        
        # Log the content for debugging
        content = self.request.data.get('content', '')
        logger.debug(f"Creating comment with content: {content}")
        
        try:
            serializer.save(task=task, author=self.request.user)
        except Exception as e:
            logger.error(f"Error creating comment: {str(e)}")
            raise ValidationError(f"Error creating comment: {str(e)}")


class ChecklistItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing checklist items on a specific task.
    """
    serializer_class = ChecklistItemSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['position', 'created_at']
    
    def get_queryset(self):
        """
        Return checklist items for the specified task where the user is either
        the task owner or assigned to the task.
        """
        task_id = self.kwargs.get('task_pk')
        task = get_object_or_404(Task, pk=task_id)
        
        # Check if user is associated with the task
        if not (task.owner == self.request.user or task.assigned_to == self.request.user):
            return ChecklistItem.objects.none()
            
        return ChecklistItem.objects.filter(task=task)
    
    def perform_create(self, serializer):
        """
        Create a new checklist item, automatically setting the task.
        Also set the position to be the highest position + 1.
        """
        task_id = self.kwargs.get('task_pk')
        task = get_object_or_404(Task, pk=task_id)
        
        # Check if user is associated with the task
        if not (task.owner == self.request.user or task.assigned_to == self.request.user):
            raise PermissionDenied("You don't have permission to add checklist items to this task")
        
        # Get the highest position and add 1
        highest_position = ChecklistItem.objects.filter(task=task).order_by('-position').first()
        position = 1
        if highest_position:
            position = highest_position.position + 1
            
        serializer.save(task=task, position=position)
    
    @action(detail=True, methods=['patch'])
    def complete(self, request, task_pk=None, pk=None):
        """
        Mark a checklist item as completed.
        """
        checklist_item = self.get_object()
        checklist_item.is_completed = True
        checklist_item.save()
        
        serializer = self.get_serializer(checklist_item)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def incomplete(self, request, task_pk=None, pk=None):
        """
        Mark a checklist item as incomplete.
        """
        checklist_item = self.get_object()
        checklist_item.is_completed = False
        checklist_item.save()
        
        serializer = self.get_serializer(checklist_item)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def reorder(self, request, task_pk=None):
        """
        Reorder checklist items based on the provided order.
        Expects an array of item IDs in the desired order.
        """
        task = get_object_or_404(Task, pk=task_pk)
        
        # Check if user is associated with the task
        if not (task.owner == self.request.user or task.assigned_to == self.request.user):
            raise PermissionDenied("You don't have permission to reorder checklist items for this task")
        
        # Get the IDs from the request data
        items_order = request.data.get('order', [])
        if not items_order:
            return Response({"error": "No order provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update the position of each item
        checklist_items = {item.id: item for item in ChecklistItem.objects.filter(task=task)}
        
        for position, item_id in enumerate(items_order, 1):
            try:
                item_id = int(item_id)
                if item_id in checklist_items:
                    item = checklist_items[item_id]
                    item.position = position
                    item.save()
            except (ValueError, KeyError):
                pass
        
        # Return the updated list
        return Response(
            self.get_serializer(ChecklistItem.objects.filter(task=task), many=True).data
        )


class TaskDependencyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing task dependencies.
    """
    serializer_class = TaskDependencySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Return task dependencies for the specified task where the user is either
        the task owner or assigned to the task.
        """
        task_id = self.kwargs.get('task_pk')
        task = get_object_or_404(Task, pk=task_id)
        
        # Check if user is associated with the task
        if not (task.owner == self.request.user or task.assigned_to == self.request.user):
            return TaskDependency.objects.none()
            
        return TaskDependency.objects.filter(task=task)
    
    def perform_create(self, serializer):
        """
        Create a new task dependency, automatically setting the task and created_by fields.
        """
        task_id = self.kwargs.get('task_pk')
        task = get_object_or_404(Task, pk=task_id)
        
        # Check if user is associated with the task
        if not (task.owner == self.request.user or task.assigned_to == self.request.user):
            raise PermissionDenied("You don't have permission to add dependencies to this task")
        
        # Validate that the depends_on task is accessible to the user
        depends_on_id = serializer.validated_data.get('depends_on').id
        depends_on_task = get_object_or_404(Task, pk=depends_on_id)
        
        if not (depends_on_task.owner == self.request.user or depends_on_task.assigned_to == self.request.user):
            raise PermissionDenied("You don't have permission to use this task as a dependency")
            
        serializer.save(task=task, created_by=self.request.user)
    
    @action(detail=True, methods=['patch'])
    def toggle(self, request, task_pk=None, pk=None):
        """
        Toggle the active status of a dependency.
        """
        dependency = self.get_object()
        
        # Toggle the active status
        dependency.active = not dependency.active
        dependency.save()
        
        serializer = self.get_serializer(dependency)
        return Response(serializer.data)
