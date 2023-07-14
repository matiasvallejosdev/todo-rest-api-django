"""
URLs mapping for todo_api
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    TaskViewSet, TaskListViewSet
)

router = DefaultRouter()
router.register('tasks', TaskViewSet, basename='tasks')
router.register('lists', TaskListViewSet, basename='lists')

app_name = 'todo_api'
urlpatterns = [
    path('', include(router.urls)),
    path('tasks/count/', TaskViewSet.as_view({'GET': 'count'}), name='tasks-count'),
    path('lists/find-by-name/', TaskListViewSet.as_view({'GET': 'find-by-name'}), name='lists-find-by-name'),
]
