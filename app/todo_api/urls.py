"""
URLs mapping for todo_api
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    TaskViewSet, TaskListCreateListView
)

router = DefaultRouter()
router.register('tasks', TaskViewSet)

app_name = 'todo_api'
urlpatterns = [
    path('', include(router.urls)),
    path('lists/', TaskListCreateListView.as_view(), name='lists')
]