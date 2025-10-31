from django.urls import path
from .views import EmployeeDetailView

urlpatterns = [
    path("api/employees/<slug:slug>", EmployeeDetailView.as_view(), name="employee_detail"),
]
