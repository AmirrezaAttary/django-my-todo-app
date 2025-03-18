import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from datetime import datetime
from accounts.models import User


@pytest.fixture
def api_client():
    client = APIClient()
    return client


@pytest.fixture
def authenticated_user():
    user = User.objects.create_user(
        email="test2test.com", password="testpass", is_verified=True
    )
    return user


@pytest.mark.django_db
class TestPostApi:

    def test_get_post_response_200(self, api_client):

        url = reverse("todo:api-v1:task-list")
        response = api_client.get(url)
        assert response.status_code == 200

    def test_create_task_response_401_status(self, api_client):
        url = reverse("todo:api-v1:task-list")
        data = {
            "title": "Test Post",
            "complete": False,
        }
        response = api_client.post(url, data)
        assert response.status_code == 401

    def test_create_task_response_201_status(
        self, api_client, authenticated_user
    ):
        url = reverse("todo:api-v1:task-list")
        data = {
            "title": "Test Post",
            "complete": False,
        }
        user = authenticated_user
        api_client.force_login(user=user)
        response = api_client.post(url, data)
        assert response.status_code == 201

    def test_create_task_invalid_data_response_400_status(
        self, api_client, authenticated_user
    ):
        url = reverse("todo:api-v1:task-list")
        data = {
            "complete": True,
        }
        user = authenticated_user
        api_client.force_login(user=user)
        response = api_client.post(url, data)
        assert response.status_code == 400
