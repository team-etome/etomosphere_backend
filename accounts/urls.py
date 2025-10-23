from django.urls import path
from accounts import views



urlpatterns = [
   
    path('api/register/', views.RegisterView.as_view(), name='user-register'),
    path('api/login/', views.LoginView.as_view(), name='user-login'),

]
