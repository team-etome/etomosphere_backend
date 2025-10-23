from rest_framework import serializers
from accounts.models import *
from django.contrib.auth.hashers import make_password



class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email','password','first_name','phone','created_at','updated_at']