from django.db import models
from django.conf import settings


class Task(models.Model):
    """Task object."""
    title = models.CharField(max_length=255, blank=False)
    completed = models.BooleanField(default=False)
    task_list = models.ForeignKey('TaskList', null=True, blank=True, on_delete=models.CASCADE)
    due_date = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.CASCADE,
                                   blank=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.task_list is None:
            exists = TaskList.objects.filter(name='inbox').exists()
            if not exists:
                TaskList.objects.create(name='inbox', created_by=self.created_by)
            inbox = TaskList.objects.get(name='inbox')
            self.task_list = inbox
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class TaskList(models.Model):
    """TaskList object."""
    name = models.CharField(max_length=255, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.CASCADE,
                                   blank=False, null=True)

    def __str__(self):
        return self.name
