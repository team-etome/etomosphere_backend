from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.TestAPIView.as_view(), name='test'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('demo/', views.RequestDemoView.as_view(), name='demo'),
]
