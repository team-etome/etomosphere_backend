from django.db.models import Q
from rest_framework import serializers
from accounts.models import User
from django.contrib.auth.hashers import make_password
from backend import constants as const
from utils.validator import UTILS


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email','password','first_name','phone','created_at','updated_at']

class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        identifier = attrs["identifier"].strip()
        password = attrs["password"]

        user = User.objects.filter(
            Q(email__iexact=identifier.lower()) | Q(phone=identifier)
        ).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError(const.INVALID_CREDENTIALS)

        if not user.is_active:
            raise serializers.ValidationError(const.USER_ACCOUNT_INACTIVE)

        attrs["user"] = user
        return attrs

class RegisterSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True, max_length=254)
    password = serializers.CharField(required=True, write_only=True)

    def validate_identifier(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                const.IDENTIFIER_REQUIRED
            )

        if UTILS.is_valid_email(value):
            if User.objects.filter(email__iexact=value).exists():
                raise serializers.ValidationError(
                    const.EMAIL_ALREADY_EXISTS
                )
        else:
            if User.objects.filter(phone=value).exists():
                raise serializers.ValidationError(
                    const.PHONE_ALREADY_EXISTS
                )

        return value
    
