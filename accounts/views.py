# views.py
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import *
from accounts.serializers import LoginSerializer
from backend.response import success_, error_
from backend import constants as const


@method_decorator(csrf_exempt, name='dispatch')  # disables CSRF for all methods
class RegisterView(APIView):
    permission_classes = [AllowAny]  # public endpoint
    authentication_classes = []      # don’t use SessionAuthentication here

    def post(self, request):
        data       = request.data
        email      = data.get("email")
        password   = data.get("password")
        first_name = data.get("first_name", "")
        phone      = data.get("phone", "")

        if not email or not password:
            return Response(
                {"detail": "Email and password required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {"detail": "Email already registered."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(
            username=first_name,
            email=email,
            password=password,
            first_name=first_name,
            phone=phone,  # include if your model supports it
        )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        return Response({
            "detail": "Account created successfully.",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "phone": user.phone,
            },
            "tokens": {
                "access": str(access_token),
                "refresh": str(refresh)
            }
        }, status=201)

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        try:
            serializer = LoginSerializer(
                data=request.data,
            )
            if not serializer.is_valid():
                return Response(error_(message=const.VALIDATION_FAILED, data=serializer.errors),
                                status=status.HTTP_400_BAD_REQUEST)
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)

            return Response(success_(message=const.LOGIN_SUCCESS,
                data={
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "phone": user.phone,
                    },
                }),status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_(message=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        