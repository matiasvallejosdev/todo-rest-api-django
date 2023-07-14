from django.test import TestCase
from django.contrib.auth import get_user_model

from todo_api.models import Task, TaskList

from django.utils import timezone


class TestsModels(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testexample12345'
        )
        self.task_list = TaskList.objects.create(
            name='Inbox',
            created_by=self.user,
            created_at=timezone.now()
        )
        self.task = Task.objects.create(
            title='Task',
            created_by=self.user,
            task_list=self.task_list
        )

    def test_task_list_str(self):
        """Test that the __str__ method of TaskList returns the correct string"""
        self.assertEqual(str(self.task_list), 'Inbox')

    def test_task_str(self):
        """Test that the __str__ method of Task returns the correct string"""
        self.assertEqual(str(self.task), 'Task')

    def test_task_completed(self):
        """Test that the completed field of Task can be set and retrieved correctly"""
        self.assertFalse(self.task.completed)
        self.task.completed = True
        self.task.save()
        self.assertTrue(self.task.completed)

    def test_task_due_date(self):
        """Test that the due_date field of Task can be set and retrieved correctly"""
        self.assertIsNone(self.task.due_date)
        due_date = timezone.now()
        self.task.due_date = due_date
        self.task.save()
        self.assertEqual(self.task.due_date, due_date)
