from venv import create
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from todo_api.models import TaskList
from todo_api.serializers import TaskListSerializer

TASKS_LISTS_URL = reverse("todo_api:lists-list")


def list_detail_url(list_uuid):
    return reverse(
        "todo_api:lists-detail",
        args=[
            list_uuid,
        ],
    )


def create_task_list(user, **params):
    payload = {"name": "List"}
    payload.update(params)
    return TaskList.objects.create(created_by=user, **payload)


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
            email="user@example.com", password="userexample123"
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_list_tasks(self):
        """Test retrieve list of tasks lists"""
        create_task_list(user=self.user)
        create_task_list(user=self.user)
        create_task_list(user=self.user)

        res = self.client.get(TASKS_LISTS_URL)

        tasks_list = TaskList.objects.all().order_by("created_at")
        serializer = TaskListSerializer(tasks_list, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 3)

    def test_retrieve_list_tasks_limited_to_user(self):
        """Test retrieve list of tasks lists limited to user"""
        user_two = get_user_model().objects.create(
            email="usertwo@example.com", password="userexample123"
        )
        create_task_list(user=user_two)
        create_task_list(user=self.user)
        create_task_list(user=self.user)

        res = self.client.get(TASKS_LISTS_URL)

        tasks_list = TaskList.objects.filter(created_by=self.user).order_by(
            "created_at"
        )
        serializer = TaskListSerializer(tasks_list, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_list_pk_from_name(self):
        """Test retrieve list primary key from name field"""
        create_task_list(user=self.user, name="List 1")
        list_2 = create_task_list(user=self.user, name="List 2")
        create_task_list(user=self.user, name="List 3")

        res = self.client.get(list_detail_url(list_2.list_uuid))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(list_2.id, res.data["id"])
    

    def test_retrieve_inbox_from_name(self):
        """Test retrieve and create if inbox not exists using slug name"""
        url = list_detail_url("inbox")
        res = self.client.get(url)
        exists = TaskList.objects.filter(name="inbox").exists()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(exists)
        
    def test_retrieve_unique_inbox_for_each_account(self):
        """Test retrieve and create unique inbox for account"""
        user_two = get_user_model().objects.create(
            email="usertwo@example.com", password="userexample123"
        )
        list_inbox = create_task_list(user=user_two, name="inbox")
        url = list_detail_url("inbox")
        res = self.client.get(url)
        exists = TaskList.objects.filter(name="inbox", created_by=self.user).exists()
        list = TaskList.objects.filter(name="inbox", created_by=self.user)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(exists)
        self.assertNotEqual(list_inbox.list_uuid, list[0].list_uuid)
        
    def test_fully_update_task_list(self):
        """Test partial update list with patch"""
        list = create_task_list(user=self.user)
        payload = {
            "name": "New name"
        }
        url = list_detail_url(list.list_uuid)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        list.refresh_from_db()
        self.assertEqual(list.name, payload["name"])

    def test_update_unauthorized_failure(self):
        new_user = get_user_model().objects.create_user(
            email="user@new.com", password="usernew123"
        )
        list = create_task_list(user=new_user)
        url = list_detail_url(list.list_uuid)
        res = self.client.patch(url, {
            "name": "new name"
        })
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotEqual(list.name, "new name")