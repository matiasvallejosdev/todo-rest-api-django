from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework.test import APIClient
from rest_framework import status

from todo_api.models import Task, TaskList
from todo_api.serializers import TaskSerializer, TaskDetailSerializer

TASKS_URL = reverse("todo_api:tasks-list")
TASKS_COUNT_URL = reverse("todo_api:tasks-count")
TASKS_UPCOMING_URL = reverse("todo_api:tasks-upcoming")


def create_user(email="user@example.com", password="userexample123"):
    payload = {
        "email": email,
        "password": password,
    }
    return get_user_model().objects.create_user(**payload)


def task_detail_url_pk(pk):
    return reverse(
        "todo_api:tasks-detail",
        args=[
            pk,
        ],
    )


def create_task(user, **params):
    payload = {
        "title": "Task",
        "completed": False,
    }
    payload.update(params)
    return Task.objects.create(created_by=user, **payload)


def create_list(user, **params):
    payload = {"name": "List"}
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
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tasks(self):
        """Test retrieve list of tasks"""
        create_task(user=self.user)
        create_task(user=self.user)
        create_task(user=self.user)

        res = self.client.get(TASKS_URL)
        tasks = Task.objects.all().order_by("created_at")
        serializer = TaskSerializer(tasks, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_tasks_failure_list_not_found(self):
        """Test retrieve list of tasks failure list not found"""
        create_task(user=self.user)
        create_task(user=self.user)
        res = self.client.get(TASKS_URL, {"list": "list-not-found"})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_upcoming_task(self):
        """Test retrieving upcoming tasks using due_date"""
        create_task(
            user=self.user, due_date=timezone.now() + timezone.timedelta(days=1)
        )
        create_task(
            user=self.user, due_date=timezone.now() + timezone.timedelta(days=2)
        )
        create_task(
            user=self.user, due_date=timezone.now() + timezone.timedelta(days=3)
        )
        create_task(user=self.user)

        res = self.client.get(TASKS_UPCOMING_URL, {})

        tasks = Task.objects.filter(due_date__isnull=False).order_by("due_date")
        serializer = TaskSerializer(tasks, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 3)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_tasks_limited_to_user(self):
        """Test retrieve list of tasks limited to user"""
        user_two = create_user(email="email@test.com", password="userexample123")
        create_task(user=user_two)
        create_task(user=self.user)
        create_task(user=self.user)

        res = self.client.get(TASKS_URL)

        tasks = Task.objects.filter(created_by=self.user).order_by("created_at")
        serializer = TaskSerializer(tasks, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_task_details(self):
        """Test retrieving task's details from uuid4."""
        task = create_task(user=self.user)

        res = self.client.get(task_detail_url_pk(task.task_uuid))
        serializer = TaskDetailSerializer(task, many=False)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_task_success(self):
        """Test creating task with success"""
        payload = {"title": "Task Title", "created_by": self.user}
        res = self.client.post(TASKS_URL, payload)
        exists = Task.objects.filter(id=res.data["id"]).exists()
        task = Task.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for k, v in payload.items():
            self.assertEqual(getattr(task, k), v)
        self.assertTrue(exists)
        self.assertEqual(task.created_by, self.user)

    def test_delete_task_success(self):
        """Test delete task success"""
        task = create_task(user=self.user)
        res = self.client.delete(task_detail_url_pk(task.task_uuid))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        exists = Task.objects.filter(id=task.pk).exists()
        self.assertFalse(exists)

    def test_delete_task_failure_unauthorized(self):
        """Test delete task failure"""
        taskTwo = create_task(
            user=get_user_model().objects.create(
                email="base@example.com", password="password123"
            )
        )
        res = self.client.delete(task_detail_url_pk(taskTwo.pk))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        exists = Task.objects.filter(id=taskTwo.pk).exists()
        self.assertTrue(exists)

    def test_create_task_with_list(self):
        """Test creating a task with a list using list_uuid"""
        list = create_list(user=self.user)
        payload = {
            "title": "Task Title",
            "created_by": self.user,
            "task_list": list.list_uuid,
        }
        res = self.client.post(TASKS_URL, payload)
        exists = Task.objects.filter(id=res.data["id"]).exists()
        task = Task.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["task_list"], payload["task_list"])
        payload.pop("task_list")
        for k, v in payload.items():
            self.assertEqual(getattr(task, k), v)
        self.assertTrue(exists)
        self.assertEqual(task.created_by, self.user)

    def test_filter_task_by_list(self):
        """Test list tasks by list."""
        list = create_list(user=self.user, name="shopping")
        list2 = create_list(user=self.user, name="job")
        task = create_task(user=self.user, title="task one", task_list=list)
        task2 = create_task(user=self.user, title="task one", task_list=list)
        task3 = create_task(user=self.user, title="task two", task_list=list2)
        task4 = create_task(user=self.user, title="task two")

        params = {"list": list.list_uuid}
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
        list = create_list(user=self.user, name="shopping")
        list2 = create_list(user=self.user, name="job")
        task = create_task(user=self.user, title="task one", task_list=list)
        task2 = create_task(user=self.user, title="task one", task_list=list2)
        task3 = create_task(user=self.user, title="task two")
        task4 = create_task(user=self.user, title="task two")

        params = {"list": "inbox"}
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
        payload = {"title": "New Title", "completed": True}
        url = task_detail_url_pk(task.task_uuid)
        self.client.patch(url, payload)
        task.refresh_from_db()
        self.assertEqual(task.title, payload["title"])
        self.assertEqual(task.completed, payload["completed"])

    def test_partial_update_date(self):
        """Test partial update task due_date"""
        task = create_task(user=self.user)
        payload = {"due_date": timezone.now()}
        url = task_detail_url_pk(task.task_uuid)
        self.client.patch(url, payload)

        task.refresh_from_db()
        self.assertEqual(task.due_date, payload["due_date"])

    def test_fully_update_task(self):
        """Test updating a task with put"""
        list_task = create_list(user=self.user)
        task = create_task(user=self.user)
        payload = {
            "title": "New Title",
            "completed": True,
            "task_list": list_task.list_uuid,
            "due_date": timezone.now(),
        }
        url = task_detail_url_pk(task.task_uuid)
        self.client.put(url, payload)
        task.refresh_from_db()
        self.assertEqual(task.title, payload["title"])
        self.assertEqual(task.created_by, self.user)

    def test_update_task_failure_unauthorized(self):
        """Test update task failure"""
        task_two = create_task(
            user=get_user_model().objects.create(
                email="user@email.com", password="password19573"
            )
        )
        task = create_task(user=self.user)
        payload = {"title": "Other Title", "completed": True}
        url = task_detail_url_pk(task_two.pk)
        res = self.client.put(url, payload)
        task.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotEqual(task_two.title, payload["title"])
        self.assertNotEqual(task_two.completed, payload["completed"])
        self.assertNotEqual(task_two.created_by, self.user)

    def test_retrieve_count_tasks(self):
        """Test retrieving count of tasks"""
        create_task(user=self.user, completed=True)
        create_task(user=self.user, completed=True)
        create_task(user=self.user, completed=False)

        res = self.client.get(TASKS_COUNT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["total"], 3)
        self.assertEqual(res.data["completed"], 2)
        self.assertEqual(res.data["uncompleted"], 1)

    def test_retrieve_count_tasks_by_list(self):
        """Test retrieving count of tasks by list"""
        list = create_list(user=self.user, name="shopping")
        list2 = create_list(user=self.user, name="job")
        create_task(user=self.user, completed=True, task_list=list)
        create_task(user=self.user, completed=True, task_list=list)
        create_task(user=self.user, completed=False, task_list=list)
        create_task(user=self.user, completed=True, task_list=list2)
        create_task(user=self.user, completed=True, task_list=list2)
        create_task(user=self.user, completed=False, task_list=list2)

        params = {"list": list.list_uuid}

        res = self.client.get(TASKS_COUNT_URL, params)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["total"], 3)
        self.assertEqual(res.data["completed"], 2)
        self.assertEqual(res.data["uncompleted"], 1)

    def test_retrieve_count_upcoming_tasks(self):
        """Test retrieving count of upcoming tasks"""
        list = create_list(user=self.user, name="inbox")

        create_task(user=self.user, due_date=timezone.now(), task_list=list)
        create_task(user=self.user, due_date=timezone.now(), task_list=list)
        create_task(user=self.user)

        params = {"list": "upcoming"}

        res = self.client.get(TASKS_COUNT_URL, params)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["total"], 2)
        self.assertEqual(res.data["completed"], 0)
        self.assertEqual(res.data["uncompleted"], 2)

    def test_retrieve_count_error_task_not_found(self):
        """Test 404 not found list cannot count tasks"""
        res = self.client.get(TASKS_COUNT_URL, {"list": "list-not-found"})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            res.data["message"], "List was not found. We cannot count tasks."
        )
