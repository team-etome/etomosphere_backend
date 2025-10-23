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



class LoginView(APIView):

    def post(self, request):

        data       = request.data
        email      = (request.data.get("email") or "").strip().lower()
        password   = data.get("password")

        if not email or not password:
            return Response(
                {"detail": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Avoid leaking which field failed
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # check_password() compares the given plain password with the stored *hashed* password
        if not user.check_password(password):
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"detail": "Account is inactive."},
                status=status.HTTP_403_FORBIDDEN,
            )

        

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        return Response({
            "message": "Login successful.",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": getattr(user, "first_name", ""),
                "phone": getattr(user, "phone", ""),
            },
            "tokens": {
                "access": str(access_token),
                "refresh": str(refresh)
            }
        }, status=status.HTTP_200_OK)
        