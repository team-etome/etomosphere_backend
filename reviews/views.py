from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ProductReview, PublicReview
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


class PublicReviewListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        reviews = PublicReview.objects.filter(is_approved=True)
        data = [
            {
                'id': r.id,
                'name': r.name,
                'school': r.school,
                'rating': r.rating,
                'comment': r.comment,
                'created_at': r.created_at.strftime('%b %Y'),
            }
            for r in reviews
        ]
        return Response(data)

    def post(self, request):
        d = request.data
        name    = str(d.get('name', '')).strip()
        school  = str(d.get('school', d.get('designation', ''))).strip()
        rating  = d.get('rating', 0)
        comment = str(d.get('comment', d.get('text', ''))).strip()

        if not name:
            return Response({'error': 'Name is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            rating = int(rating)
            if not 1 <= rating <= 5:
                raise ValueError
        except (ValueError, TypeError):
            return Response({'error': 'Rating must be 1–5.'}, status=status.HTTP_400_BAD_REQUEST)
        if len(comment) < 10:
            return Response({'error': 'Review must be at least 10 characters.'}, status=status.HTTP_400_BAD_REQUEST)

        PublicReview.objects.create(name=name, school=school, rating=rating, comment=comment)
        return Response({'message': 'Review submitted. It will appear after approval.'}, status=status.HTTP_201_CREATED)