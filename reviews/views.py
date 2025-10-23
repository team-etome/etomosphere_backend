from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import ProductReview
from .serializers import ProductReviewSerializer


class ProductReviewListAPIView(generics.ListCreateAPIView):
    """API view for listing and creating product reviews"""
    serializer_class = ProductReviewSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        product_id = self.kwargs.get('product_pk')
        if product_id:
            return ProductReview.objects.filter(product_id=product_id)
        return ProductReview.objects.all()
    
    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_pk')
        serializer.save(user=self.request.user, product_id=product_id)


class ProductReviewDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API view for product review details"""
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ProductReview.objects.filter(user=self.request.user)


class UserReviewListAPIView(generics.ListAPIView):
    """API view for listing user's reviews"""
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ProductReview.objects.filter(user=self.request.user)


class ProductReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for product reviews"""
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        product_id = self.kwargs.get('product_pk')
        if product_id:
            return ProductReview.objects.filter(product_id=product_id)
        return ProductReview.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_pk')
        serializer.save(user=self.request.user, product_id=product_id)