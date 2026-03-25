"""
Account serializers for registration, login, profiles, and addresses.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import StyleProfile, Address

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(write_only=True, min_length=8, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email", "first_name", "last_name", "password",
            "password_confirm", "phone", "gender", "date_of_birth",
            "marketing_consent",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        StyleProfile.objects.create(user=user)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT serializer including user data in the response."""

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserProfileSerializer(self.user).data
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for reading and updating user profiles."""

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "full_name",
            "phone", "date_of_birth", "gender", "avatar",
            "is_influencer", "influencer_code", "email_verified",
            "marketing_consent", "created_at",
        ]
        read_only_fields = ["id", "email", "is_influencer", "influencer_code", "email_verified", "created_at"]


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing user password."""

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": "Passwords do not match."})
        return attrs


class StyleProfileSerializer(serializers.ModelSerializer):
    """Serializer for style profile management."""

    class Meta:
        model = StyleProfile
        fields = [
            "id", "preferred_styles", "preferred_fit", "body_type",
            "preferred_colors", "avoided_colors", "preferred_brands",
            "budget_min", "budget_max", "height_cm", "weight_kg",
            "chest_cm", "waist_cm", "hip_cm", "shoe_size_eu",
            "sustainability_preference", "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for user addresses."""

    class Meta:
        model = Address
        fields = [
            "id", "address_type", "full_name", "phone",
            "street_address_1", "street_address_2", "city",
            "state", "postal_code", "country", "is_default",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
