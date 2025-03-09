from rest_framework import serializers
from .models import Task, TaskComment
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class TaskSerializer(serializers.ModelSerializer):
    owner_details = UserSerializer(source='owner', read_only=True)
    assigned_to_details = UserSerializer(source='assigned_to', read_only=True)
    tags_list = serializers.ListField(
        child=serializers.CharField(),
        source='get_tags_list',
        required=False,
        write_only=True
    )
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'created_at', 'due_date', 
                 'status', 'priority', 'owner', 'assigned_to', 
                 'owner_details', 'assigned_to_details', 'tags', 'tags_list', 'duration']
        read_only_fields = ['created_at']
        
    def create(self, validated_data):
        tags_list = validated_data.pop('get_tags_list', None)
        task = Task.objects.create(**validated_data)
        if tags_list:
            task.set_tags_list(tags_list)
            task.save()
        return task
    
    def update(self, instance, validated_data):
        tags_list = validated_data.pop('get_tags_list', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if tags_list is not None:
            instance.set_tags_list(tags_list)
        instance.save()
        return instance

class TaskCommentSerializer(serializers.ModelSerializer):
    author_details = UserSerializer(source='author', read_only=True)
    
    class Meta:
        model = TaskComment
        fields = ['id', 'task', 'author', 'content', 'created_at', 'updated_at', 'author_details']
        read_only_fields = ['created_at', 'updated_at']
    
    def create(self, validated_data):
        return TaskComment.objects.create(**validated_data)
        
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance 