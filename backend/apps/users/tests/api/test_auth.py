import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestJWTAuthentication:
    def test_obtain_token_pair(self):
        password = "StrongPass123!"
        user = UserFactory(password=password)
        client = APIClient()

        response = client.post(
            reverse("api-jwt-create"),
            data={"email": user.email, "password": password},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["user"] == {
            "id": user.pk,
            "email": user.email,
            "name": user.name,
        }

    def test_reject_invalid_credentials(self):
        user = UserFactory(password="StrongPass123!")
        client = APIClient()

        response = client.post(
            reverse("api-jwt-create"),
            data={"email": user.email, "password": "wrong-pass"},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "access" not in response.data
        assert "refresh" not in response.data
