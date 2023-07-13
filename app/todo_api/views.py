"""
Views for todo_api endpoints
"""
from rest_framework import permissions, viewsets, status, generics
from rest_framework.views import APIView
from .models import Task, TaskList
from .serializers import (TaskSerializer, TaskDetailSerializer,
                          TaskCreateSerializer, TaskListSerializer,
                          TaskCountSerializer, )

from rest_framework.response import Response
from rest_framework.decorators import action


class TaskViewSet(viewsets.ModelViewSet):
    """Class for viewset tasks"""
    model = Task
    serializer_class = TaskDetailSerializer
    queryset = Task.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.filter(created_by=self.request.user)
        task_list = self.request.query_params.get('list', None)
        if task_list:
            task_list = str(task_list).lower()
            queryset = queryset.filter(task_list__name=task_list)
        return queryset.order_by('created_at').distinct()

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskSerializer
        elif self.action == 'create' or self.action == 'update':
            return TaskCreateSerializer
        elif self.action == 'count_tasks':
            return TaskCountSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(methods=['GET'], detail=False, url_path='count')
    def count_tasks(self, request, *args, **kwargs):
        """Count completed tasks and retrieve count"""
        tasks = self.get_queryset().count()
        tasks_completed = self.get_queryset().filter(completed=True).count()
        tasks_uncompleted = self.get_queryset().filter(completed=False).count()

        data = {
            'total': tasks,
            'completed': tasks_completed,
            'uncompleted': tasks_uncompleted
        }

        serializer = TaskCountSerializer(data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskListViewSet(viewsets.ModelViewSet):
    """Class for viewset task lists"""
    model = TaskList
    serializer_class = TaskListSerializer
    queryset = TaskList.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.filter(created_by=self.request.user)
        return queryset.order_by('created_at').distinct()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(methods=['GET'], detail=False, url_path='find-by-name')
    def find_by_name(self, request, *args, **kwargs):
        """Using query name to find task list and return a task_list object"""
        name = request.query_params.get('list_name', None)
        if name:
            name = str(name).lower()
            task_lists = self.get_queryset().get(name__contains=name)
            if task_lists:
                serializer = TaskListSerializer(task_lists, many=False)
                return Response(serializer.data)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
