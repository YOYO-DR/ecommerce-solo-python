from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.views import TokenObtainPairView  # type: ignore[import-not-found]
from rest_framework_simplejwt.tokens import RefreshToken  # type: ignore[import-not-found]

from apps.users.models import User
from apps.users.tokens import account_activation_token
from apps.users.tasks import send_activation_email

from .serializers import EmailTokenObtainPairSerializer
from .serializers import UserSerializer
from .serializers import UserRegistrationSerializer
from .serializers import UserActivationSerializer


class UserViewSet(GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "pk"
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        user = getattr(self.request, "user", None)
        if not getattr(user, "is_authenticated", False):
            return User.objects.none()
        return self.queryset.filter(id=user.id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class EmailTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = EmailTokenObtainPairSerializer


class UserRegistrationView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate activation token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)

        # Build activation URL for frontend
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
        activation_link = f"{frontend_url}/activate-account?uid={uid}&token={token}"

        # Send activation email asynchronously using Celery
        send_activation_email.delay(user.id, activation_link)

        return Response(
            status=status.HTTP_201_CREATED,
            data={
                "message": "User registered successfully. Please check your email to activate your account.",
                "email": user.email,
            },
        )


class UserActivationView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserActivationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        uid = request.data.get("uid")

        if not uid:
            return Response(
                {"error": "UID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": "Invalid activation link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not account_activation_token.check_token(user, token):
            return Response(
                {"error": "Invalid or expired activation token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_active:
            return Response(
                {"message": "Account is already activated."},
                status=status.HTTP_200_OK,
            )

        user.is_active = True
        user.save(update_fields=["is_active"])

        return Response(
            {"message": "Account activated successfully. You can now login."},
            status=status.HTTP_200_OK,
        )
