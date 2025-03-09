from rest_framework import serializers
from .models import Task
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class TaskSerializer(serializers.ModelSerializer):
    owner_details = UserSerializer(source='owner', read_only=True)
    assigned_to_details = UserSerializer(source='assigned_to', read_only=True)
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'created_at', 'due_date', 
                 'status', 'priority', 'owner', 'assigned_to', 
                 'owner_details', 'assigned_to_details']
        read_only_fields = ['created_at'] 