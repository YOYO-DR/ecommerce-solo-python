from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from apps.users.api.views import UserActivationView
from apps.users.api.views import UserRegistrationView
from apps.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)


app_name = "api"
urlpatterns = router.urls + [
    path("users/register/", UserRegistrationView.as_view(), name="user-register"),
    path("users/activate/", UserActivationView.as_view(), name="user-activate"),
]
