from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products/(?P<product_pk>\d+)/reviews', views.ProductReviewViewSet, basename='product-reviews')

urlpatterns = [
    # Class-based API views
    path('api/products/<int:product_pk>/reviews/', views.ProductReviewListAPIView.as_view(), name='product-review-list'),
    path('api/reviews/<int:pk>/', views.ProductReviewDetailAPIView.as_view(), name='product-review-detail'),
    path('api/my-reviews/', views.UserReviewListAPIView.as_view(), name='user-review-list'),
    
    # ViewSet URLs
    path('', include(router.urls)),
]
