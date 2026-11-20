from rest_framework import serializers
from accounts.models import *
from django.contrib.auth.hashers import make_password



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
            raise serializers.ValidationError("Invalid credentials.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        attrs["user"] = user
        return attrs