from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from todo_api.models import Task, TaskList

from core.serializers import UserSerializer


class TaskListSerializer(ModelSerializer):
    """Serializer for TaskList instances"""

    class Meta:
        model = TaskList
        fields = ('id', 'name', 'created_by',)
        read_only_fields = ('id',)


class TaskSerializer(ModelSerializer):
    """Serializer for Task instances to list tasks"""

    class Meta:
        model = Task
        fields = ('id', 'title', 'completed',)
        read_only_fields = ('id',)


class TaskCountSerializer(serializers.Serializer):
    """Serializer for counting tasks"""
    total = serializers.IntegerField(default=0, read_only=True)
    completed = serializers.IntegerField(default=0, read_only=True)
    uncompleted = serializers.IntegerField(default=0, read_only=True)


class TaskDetailSerializer(ModelSerializer):
    """Serializer for Task instances to detail"""
    created_by = UserSerializer(many=False, read_only=True)
    task_list = TaskListSerializer(many=False, read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'title', 'completed', 'due_date', 'task_list', 'created_by', 'created_at',)
        read_only_fields = ('id',)


class TaskCreateSerializer(ModelSerializer):
    """Serializer for Task instances to create"""
    created_by = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'title', 'completed', 'due_date', 'task_list', 'created_by',)
        read_only_fields = ('id',)
