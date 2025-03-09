from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Task, TaskComment
from .serializers import TaskSerializer, TaskCommentSerializer

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
            
        serializer.save(task=task, author=self.request.user)
