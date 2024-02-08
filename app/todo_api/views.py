"""
Views for todo_api endpoints
"""
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, viewsets, status
from .models import Task, TaskList
from .serializers import (
    TaskSerializer,
    TaskDetailSerializer,
    TaskCreateSerializer,
    TaskListSerializer,
    TaskCountSerializer,
)

from rest_framework.response import Response
from rest_framework.decorators import action
from urllib.parse import unquote
import uuid


class TaskViewSet(viewsets.ModelViewSet):
    """Class for viewset tasks"""

    model = Task
    serializer_class = TaskDetailSerializer
    queryset = Task.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "task_uuid"

    def get_queryset(self):
        queryset = self.queryset.filter(created_by=self.request.user)
        task_list = self.request.query_params.get("list", "")
        if task_list:
            if task_list == "inbox":
                queryset = queryset.filter(task_list__name="inbox")
            elif task_list == "":
                queryset = queryset
            else:
                task_list = unquote(task_list)  # Decode the URL-encoded string
                task_list = str(task_list).lower().replace(" ", "-")
                task_list = uuid.UUID(task_list)
                queryset = queryset.filter(task_list__list_uuid=task_list)
        return queryset.order_by("created_at").distinct()

    # override get method
    def list(self, request, *args, **kwargs):
        """
        Return the list of tasks for the authenticated user,
        filtered by the task list specified in the query parameters.
        If the list is not specified, return the list of tasks in the inbox.
        In case inbox is not created, create it. If the list is not found,
        it wil return a 404 error.
        """
        task_list = self.request.query_params.get("list", "")
        if task_list != "inbox" and task_list != "":
            try:
                task_list = unquote(task_list)  # Decode the URL-encoded string
                task_list = str(task_list).lower().replace(" ", "-")
                list_uuid = uuid.UUID(task_list)
                exists = get_object_or_404(TaskList, list_uuid=list_uuid)
                if not exists:
                    return Response(
                        status=status.HTTP_404_NOT_FOUND,
                        body={"message": "List was not found. We can not count tasks."},
                    )
            except ValueError:
                return Response(
                    status=status.HTTP_404_NOT_FOUND,
                    data={"message": "Task list was not found. We cannot list tasks."},
                )
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "list":
            return TaskSerializer
        elif self.action == "create" or self.action == "update":
            return TaskCreateSerializer
        elif self.action == "count_tasks":
            return TaskCountSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(methods=["GET"], detail=False, url_path="count")
    def count_tasks(self, queryset, *args, **kwargs):
        """
        Count completed tasks and retrieve count.
        If a task list is specified in the query parameters, it will count
        the tasks in that list.
        If the list is not found, it will return a 404 error.
        """
        task_list = self.request.query_params.get("list", None)
        if task_list == "upcoming":
            # Count upcoming tasks
            tasks = Task.objects.filter(due_date__isnull=False)
            tasks_completed = tasks.filter(completed=True).count()
            tasks_uncompleted = tasks.filter(completed=False).count()
            data = {
                "total": tasks.count(),
                "completed": tasks_completed,
                "uncompleted": tasks_uncompleted,
            }
        else:
            # Count inbox tasks or listed tasks using UUID
            if task_list and task_list != "inbox":
                try:
                    task_list = unquote(task_list)  # Decode the URL-encoded string
                    task_list = str(task_list).lower().replace(" ", "-")
                    list_uuid = uuid.UUID(task_list)
                    exists = get_object_or_404(TaskList, list_uuid=list_uuid)
                    if not exists:
                        return Response(
                            status=status.HTTP_404_NOT_FOUND,
                            body={"message": "List was not found. We can not count tasks."},
                        )
                except ValueError:
                    # If the conversion fails, handle the error gracefully
                    return Response(
                        status=status.HTTP_404_NOT_FOUND,
                        data={"message": "List was not found. We cannot count tasks."},
                    )
            tasks = self.get_queryset().count()
            tasks_completed = self.get_queryset().filter(completed=True).count()
            tasks_uncompleted = self.get_queryset().filter(completed=False).count()
            data = {
                "total": tasks,
                "completed": tasks_completed,
                "uncompleted": tasks_uncompleted,
            }

        serializer = TaskCountSerializer(data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=False, url_path="upcoming")
    def upcoming_tasks(self, request, *args, **kwargs):
        """
        List all upcoming tasks scheduled ordered by date
        """
        tasks = self.get_queryset().filter(due_date__isnull=False).order_by('due_date')
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

class TaskListViewSet(viewsets.ModelViewSet):
    """Class for viewset task lists"""

    model = TaskList
    serializer_class = TaskListSerializer
    queryset = TaskList.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "list_uuid"

    def get_queryset(self):
        queryset = self.queryset.filter(created_by=self.request.user)
        return queryset.order_by("created_at").distinct()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def retrieve(self, request, list_uuid=None, *args, **kwargs):
        """Using list_uuid to find task list and return a task_list object"""
        list_uuid = list_uuid.lower()
        queryset = self.get_queryset()
        try:
            if list_uuid == "inbox":
                # case inbox os is not created
                inbox = TaskList.objects.filter(
                    name="inbox", created_by=self.request.user
                ).exists()  # noqa: E501
                if not inbox:
                    TaskList.objects.create(name="inbox", created_by=self.request.user)
                queryset = queryset.get(name__iexact="inbox")
            else:
                queryset = queryset.get(list_uuid__iexact=list_uuid)
        except TaskList.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"message": "List Not found."}
            )
        serializer = self.get_serializer(queryset, many=False)
        return Response(serializer.data)
