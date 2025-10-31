from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cart', views.CartViewSet, basename='cart')

urlpatterns = [
    # Class-based API views
    # path('api/', views.CartDetailAPIView.as_view(), name='cart-detail'),
    path('api/addCart/', views.AddToCartAPIView.as_view(), name='add-to-cart'),
    # path('api/getCart/', views.GetCartAPIView.as_view(), name='get-cart'),
    path('api/remove/', views.RemoveFromCartAPIView.as_view(), name='remove-from-cart'),
    path('api/update/', views.UpdateCartItemAPIView.as_view(), name='update-cart-item'),
    path('api/clear/', views.ClearCartAPIView.as_view(), name='clear-cart'),
    
    # ViewSet URLs
    path('', include(router.urls)),
]
