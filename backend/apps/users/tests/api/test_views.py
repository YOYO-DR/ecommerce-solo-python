import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory
from unittest.mock import patch, MagicMock

from apps.users.api.views import UserViewSet
from apps.users.models import User


class TestUserViewSet:
    @pytest.fixture
    def api_rf(self) -> APIRequestFactory:
        return APIRequestFactory()

    def test_get_queryset(self, user: User, api_rf: APIRequestFactory):
        view = UserViewSet()
        request = api_rf.get("/fake-url/")
        request.user = user

        view.request = request

        assert user in view.get_queryset()

    def test_me(self, user: User, api_rf: APIRequestFactory):
        view = UserViewSet()
        request = api_rf.get("/fake-url/")
        request.user = user

        view.request = request

        response = view.me(request)  # type: ignore[call-arg, arg-type, misc]

        assert response.data == {
            "id": user.pk,
            "email": user.email,
            "name": user.name,
            "url": f"http://testserver/api/users/{user.pk}/",
        }


class TestUserRegistrationView:
    @pytest.fixture
    def api_client(self) -> APIClient:
        return APIClient()

    @pytest.mark.django_db
    @patch("apps.users.api.views.send_activation_email.delay")
    def test_register_user_success(self, mock_send_email: MagicMock, api_client: APIClient):  # type: ignore[no-untyped-def]
        payload = {
            "email": "new.user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "StrongPass!234",
            "password_confirmation": "StrongPass!234",
        }

        url = reverse("api:user-register")
        response = api_client.post(url, data=payload)

        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert "message" in body
        assert body["email"] == payload["email"]

        # Verify user was created but is inactive
        user = User.objects.get(email=payload["email"])
        assert user.is_active is False
        assert user.first_name == payload["first_name"]
        assert user.last_name == payload["last_name"]

        # Verify Celery task was called
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args[0]
        assert call_args[0] == user.id  # user_id
        assert "activate-account" in call_args[1]  # activation_link

    @pytest.mark.django_db
    def test_register_user_password_mismatch(self, api_client: APIClient):
        payload = {
            "email": "mismatch@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "password": "StrongPass!234",
            "password_confirmation": "StrongPass!432",
        }

        url = reverse("api:user-register")
        response = api_client.post(url, data=payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password_confirmation" in response.json()
        assert not User.objects.filter(email=payload["email"]).exists()

    @pytest.mark.django_db
    def test_register_user_duplicate_email(self, api_client: APIClient, user: User):
        payload = {
            "email": user.email,
            "first_name": "Duplicate",
            "last_name": "User",
            "password": "StrongPass!234",
            "password_confirmation": "StrongPass!234",
        }

        url = reverse("api:user-register")
        response = api_client.post(url, data=payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.json()


class TestUserActivationView:
    @pytest.fixture
    def api_client(self) -> APIClient:
        return APIClient()

    @pytest.mark.django_db
    def test_activate_user_success(self, api_client: APIClient):
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        from apps.users.tests.factories import UserFactory
        from apps.users.tokens import account_activation_token

        user = UserFactory(is_active=False)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)

        url = reverse("api:user-activate")
        payload = {"uid": uid, "token": token}
        response = api_client.post(url, data=payload)

        assert response.status_code == status.HTTP_200_OK
        assert "activated successfully" in response.json()["message"].lower()

        user.refresh_from_db()
        assert user.is_active is True

    @pytest.mark.django_db
    def test_activate_user_invalid_token(self, api_client: APIClient):
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        from apps.users.tests.factories import UserFactory

        user = UserFactory(is_active=False)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        invalid_token = "invalid-token-123"

        url = reverse("api:user-activate")
        payload = {"uid": uid, "token": invalid_token}
        response = api_client.post(url, data=payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "invalid" in response.json()["error"].lower()

        user.refresh_from_db()
        assert user.is_active is False

    @pytest.mark.django_db
    def test_activate_user_already_active(self, api_client: APIClient):
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        from apps.users.tests.factories import UserFactory
        from apps.users.tokens import account_activation_token

        user = UserFactory(is_active=True)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)

        url = reverse("api:user-activate")
        payload = {"uid": uid, "token": token}
        response = api_client.post(url, data=payload)

        assert response.status_code == status.HTTP_200_OK
        assert "already activated" in response.json()["message"].lower()
