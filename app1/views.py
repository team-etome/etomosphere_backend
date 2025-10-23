from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

# Create your views here.

class TestAPIView(APIView):
    """
    API view to verify the backend is working
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Test endpoint to verify the backend is working
        """
        return Response({
            'message': 'Etomosphere Backend is working!',
            'status': 'success',
            'version': '1.0.0',
            'endpoints': {
                'accounts': '/api/accounts/',
                'products': '/api/products/',
                'cart': '/api/cart/',
                'orders': '/api/orders/',
                'reviews': '/api/reviews/',
                'admin': '/admin/',
            }
        }, status=status.HTTP_200_OK)
