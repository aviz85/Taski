from rest_framework import serializers
from .models import Task, TaskComment, ChecklistItem
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistItem
        fields = ['id', 'task', 'text', 'is_completed', 'position', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class TaskSerializer(serializers.ModelSerializer):
    owner_details = UserSerializer(source='owner', read_only=True)
    assigned_to_details = UserSerializer(source='assigned_to', read_only=True)
    tags_list = serializers.ListField(
        child=serializers.CharField(),
        source='get_tags_list',
        required=False,
        write_only=True
    )
    checklist_items = ChecklistItemSerializer(many=True, read_only=True)
    checklist_completion = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'created_at', 'due_date', 
                 'status', 'priority', 'owner', 'assigned_to', 
                 'owner_details', 'assigned_to_details', 'tags', 'tags_list', 
                 'duration', 'checklist_items', 'checklist_completion']
        read_only_fields = ['created_at']
    
    def get_checklist_completion(self, obj):
        """Calculate the completion percentage of checklist items."""
        items = obj.checklist_items.all()
        if not items:
            return 0
        completed = items.filter(is_completed=True).count()
        return int((completed / items.count()) * 100)
        
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
        read_only_fields = ['created_at', 'updated_at', 'task', 'author']
    
    def validate_content(self, value):
        """
        Validate that the content field is not empty and can handle any character encoding.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Comment content cannot be empty")
        
        # The content is valid if we got here
        return value
    
    def create(self, validated_data):
        return TaskComment.objects.create(**validated_data)
        
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance 