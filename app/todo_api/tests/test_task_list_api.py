from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework.test import APIClient
from rest_framework import status

from todo_api.models import Task, TaskList
from todo_api.serializers import TaskListSerializer

TASKS_LISTS_URL = reverse('todo_api:lists-list')
TASK_LIST_PK_URL = reverse('todo_api:lists-find-by-name')


def create_task_list(user, **params):
    payload = {
        'name': 'List'
    }
    payload.update(params)
    return TaskList.objects.create(created_by=user, **payload)


# TODO: Get list primary key from name field
class TestPublicTaskListAPI(TestCase):
    """Test unauthorized API Request"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TASKS_LISTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPrivateTaskListAPI(TestCase):
    """Test authorized API Request"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='userexample123'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_list_tasks(self):
        """Test retrieve list of tasks lists"""
        create_task_list(user=self.user)
        create_task_list(user=self.user)
        create_task_list(user=self.user)

        res = self.client.get(TASKS_LISTS_URL)

        tasks_list = TaskList.objects.all().order_by('created_at')
        serializer = TaskListSerializer(tasks_list, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 3)

    def test_retrieve_list_tasks_limited_to_user(self):
        """Test retrieve list of tasks lists limited to user"""
        user_two = get_user_model().objects.create(
            email='usertwo@example.com',
            password='userexample123'
        )
        create_task_list(user=user_two)
        create_task_list(user=self.user)
        create_task_list(user=self.user)

        res = self.client.get(TASKS_LISTS_URL)

        tasks_list = TaskList.objects.filter(created_by=self.user).order_by('created_at')
        serializer = TaskListSerializer(tasks_list, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_list_pk_from_name(self):
        """Test retrieve list primary key from name field"""
        list_1 = create_task_list(user=self.user, name='List 1')
        list_2 = create_task_list(user=self.user, name='List 2')
        list_3 = create_task_list(user=self.user, name='List 3')

        payload = {
            'list_name': list_2.name
        }

        res = self.client.get(TASK_LIST_PK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(list_2.id, res.data['id'])
