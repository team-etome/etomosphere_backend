from django.urls import path

from accounts.views import LoginAPIView, RegisterView



urlpatterns = [
   
    path('api/register/', RegisterView.as_view(), name='user-register'),
    path('login/', LoginAPIView.as_view(), name='user-login'),

]
