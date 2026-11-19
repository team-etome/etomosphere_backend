from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import OEMRegistration


class OEMRegistrationSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = OEMRegistration
        exclude = ['status', 'admin_note', 'submitted_at', 'updated_at']

    def validate(self, data):
        if data.get('password') != data.pop('password2', None):
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class OEMRegistrationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OEMRegistration
        fields = ['id', 'full_name', 'email', 'company_name', 'status', 'submitted_at']
