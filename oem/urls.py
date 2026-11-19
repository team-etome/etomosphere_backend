from django.urls import path
from .views import OEMRegisterView, OEMListView, OEMApproveView

urlpatterns = [
    path('oem/register/',        OEMRegisterView.as_view(), name='oem-register'),
    path('oem/registrations/',   OEMListView.as_view(),     name='oem-list'),
    path('oem/registrations/<int:pk>/status/', OEMApproveView.as_view(), name='oem-approve'),
]
