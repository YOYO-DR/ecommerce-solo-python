from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer  # type: ignore[import-not-found]

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["id", "name", "email", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "pk"},
        }


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)
        token["email"] = user.email
        token["name"] = user.name
        return token

    def validate(self, attrs):  # type: ignore[override]
        data = super().validate(attrs)
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "name": self.user.name,
        }
        return data


class UserRegistrationSerializer(serializers.ModelSerializer[User]):
    password = serializers.CharField(write_only=True, required=True)
    password_confirmation = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "password", "password_confirmation"]
        read_only_fields = ["id"]

    def validate_email(self, value: str) -> str:
        email = User.objects.normalize_email(value)
        if User.objects.filter(email=email).exists():
            msg = "A user with that email already exists."
            raise serializers.ValidationError(msg)
        return email

    def validate(self, attrs):  # type: ignore[override]
        password = attrs.get("password")
        password_confirmation = attrs.get("password_confirmation")

        if not password:
            msg = "Password is required."
            raise serializers.ValidationError({"password": msg})

        if password != password_confirmation:
            msg = "Passwords do not match."
            raise serializers.ValidationError({"password_confirmation": msg})

        try:
            sample_user = User(
                email=attrs.get("email"),
                first_name=attrs.get("first_name", ""),
                last_name=attrs.get("last_name", ""),
            )
            validate_password(password, user=sample_user)
        except DjangoValidationError as exc:  # pragma: no cover - direct pass-through
            raise serializers.ValidationError({"password": list(exc.messages)}) from exc

        return attrs

    def create(self, validated_data):  # type: ignore[override]
        password = validated_data.pop("password")
        validated_data.pop("password_confirmation", None)
        # Create user as inactive until email is verified
        user = User.objects.create_user(
            password=password,
            is_active=False,
            **validated_data,
        )
        return user


class UserActivationSerializer(serializers.Serializer):  # type: ignore[type-arg]
    token = serializers.CharField(required=True)
