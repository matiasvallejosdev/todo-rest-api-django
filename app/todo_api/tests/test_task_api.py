from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework.test import APIClient
from rest_framework import status

from todo_api.models import Task, TaskList
from todo_api.serializers import TaskSerializer, TaskDetailSerializer

TASKS_URL = reverse('todo_api:task-list')


def task_detail_url_pk(pk):
    return reverse('todo_api:task-detail', args=[pk, ])


def create_task(user, **params):
    payload = {
        'title': 'Task',
        'completed': False,
    }
    payload.update(params)
    return Task.objects.create(created_by=user, **payload)


def create_list(user, **params):
    payload = {
        'name': 'List'
    }
    payload.update(params)
    return TaskList.objects.create(created_by=user, **payload)


class TestPublicTaskAPI(TestCase):
    """Test unauthorized API Request"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TASKS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPrivateTaskAPI(TestCase):
    """Test authorized API Request"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='userexample123'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tasks(self):
        """Test retrieve list of tasks"""
        create_task(user=self.user)
        create_task(user=self.user)
        create_task(user=self.user)

        res = self.client.get(TASKS_URL)
        tasks = Task.objects.all().order_by('created_at')
        serializer = TaskSerializer(tasks, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_tasks_limited_to_user(self):
        user_two = get_user_model().objects.create(email='email@test.com', password='userexample123')
        create_task(user=user_two)
        create_task(user=self.user)
        create_task(user=self.user)

        res = self.client.get(TASKS_URL)

        tasks = Task.objects.filter(created_by=self.user).order_by('created_at')
        serializer = TaskSerializer(tasks, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_task_details(self):
        """Test retrieving task's details from recipe."""
        task = create_task(user=self.user)

        res = self.client.get(task_detail_url_pk(task.pk))
        serializer = TaskDetailSerializer(task, many=False)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_task_success(self):
        """Test creating task with success"""
        payload = {
            'title': 'Task Title',
            'created_by': self.user
        }
        res = self.client.post(TASKS_URL, payload)
        exists = Task.objects.filter(id=res.data['id']).exists()
        task = Task.objects.get(id=res.data['id'])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for k, v in payload.items():
            self.assertEqual(getattr(task, k), v)
        self.assertTrue(exists)
        self.assertEqual(task.created_by, self.user)

    def test_delete_task_success(self):
        """Test delete task success"""
        task = create_task(user=self.user)
        res = self.client.delete(task_detail_url_pk(task.pk))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        exists = Task.objects.filter(id=task.pk).exists()
        self.assertFalse(exists)

    def test_delete_task_failure_unauthorized(self):
        """Test delete task failure"""
        taskTwo = create_task(user=get_user_model().objects.create(
            email='base@example.com',
            password='password123'
        ))
        res = self.client.delete(task_detail_url_pk(taskTwo.pk))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        exists = Task.objects.filter(id=taskTwo.pk).exists()
        self.assertTrue(exists)

    def test_create_task_with_list(self):
        """Test creating a task with a list"""
        list = create_list(user=self.user)
        payload = {
            'title': 'Task Title',
            'created_by': self.user,
            'task_list': list.pk
        }
        res = self.client.post(TASKS_URL, payload)
        exists = Task.objects.filter(id=res.data['id']).exists()
        task = Task.objects.get(id=res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['task_list'], payload['task_list'])
        payload.pop('task_list')
        for k, v in payload.items():
            self.assertEqual(getattr(task, k), v)
        self.assertTrue(exists)
        self.assertEqual(task.created_by, self.user)

    def test_filter_task_by_list(self):
        """Test list tasks by list."""
        list = create_list(user=self.user, name='shopping')
        list2 = create_list(user=self.user, name='job')
        task = create_task(user=self.user, title='task one', task_list=list)
        task2 = create_task(user=self.user, title='task one', task_list=list)
        task3 = create_task(user=self.user, title='task two', task_list=list2)
        task4 = create_task(user=self.user, title='task two')

        params = {
            'list': 'shopping'
        }
        res = self.client.get(TASKS_URL, params)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer_task = TaskSerializer(task)
        serializer_task2 = TaskSerializer(task2)
        serializer_task3 = TaskSerializer(task3)
        serializer_task4 = TaskSerializer(task4)

        self.assertEqual(len(res.data), 2)
        self.assertIn(serializer_task.data, res.data)
        self.assertIn(serializer_task2.data, res.data)
        self.assertNotIn(serializer_task3.data, res.data)
        self.assertNotIn(serializer_task4.data, res.data)

    def test_filter_task_by_empty_list(self):
        list = create_list(user=self.user, name='shopping')
        list2 = create_list(user=self.user, name='job')
        task = create_task(user=self.user, title='task one', task_list=list)
        task2 = create_task(user=self.user, title='task one', task_list=list2)
        task3 = create_task(user=self.user, title='task two')
        task4 = create_task(user=self.user, title='task two')

        params = {
            'list': 'inbox'
        }
        res = self.client.get(TASKS_URL, params)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer_task = TaskSerializer(task)
        serializer_task2 = TaskSerializer(task2)
        serializer_task3 = TaskSerializer(task3)
        serializer_task4 = TaskSerializer(task4)

        self.assertNotIn(serializer_task, res.data)
        self.assertNotIn(serializer_task2, res.data)
        self.assertIn(serializer_task3.data, res.data)
        self.assertIn(serializer_task4.data, res.data)

    def test_partial_update_task(self):
        """Test updating a task with patch"""
        task = create_task(user=self.user)
        payload = {'title': 'New Title', 'completed': True}
        url = task_detail_url_pk(task.pk)
        self.client.patch(url, payload)
        task.refresh_from_db()
        self.assertEqual(task.title, payload['title'])
        self.assertEqual(task.completed, payload['completed'])

    def test_fully_update_task(self):
        """Test updating a task with put"""
        list = create_list(user=self.user)
        task = create_task(user=self.user)
        payload = {
            'title': 'New Title',
            'completed': True,
            'task_list': list.pk,
            'due_date': timezone.now(),
        }
        url = task_detail_url_pk(task.pk)
        self.client.put(url, payload)
        task.refresh_from_db()
        self.assertEqual(task.title, payload['title'])
        self.assertEqual(task.created_by, self.user)
