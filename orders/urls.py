from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='order')

urlpatterns = [
    # Class-based API views
    path('api/', views.OrderListAPIView.as_view(), name='order-list'),
    path('api/<int:pk>/', views.OrderDetailAPIView.as_view(), name='order-detail'),
    path('api/create/', views.CreateOrderAPIView.as_view(), name='create-order'),
    path('api/<int:order_id>/update-status/', views.UpdateOrderStatusAPIView.as_view(), name='update-order-status'),
    
    # ViewSet URLs
    path('', include(router.urls)),
]
