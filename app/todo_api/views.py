"""
Views for todo_api endpoints
"""
from rest_framework import permissions, viewsets, status, generics
from .models import Task, TaskList
from .serializers import TaskSerializer, TaskDetailSerializer, TaskCreateSerializer, TaskListSerializer


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
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TaskListCreateListView(generics.ListCreateAPIView):
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
