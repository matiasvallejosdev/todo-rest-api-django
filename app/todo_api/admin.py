from django.contrib import admin
from todo_api.models import Task, TaskList

admin.site.register(Task)
admin.site.register(TaskList)