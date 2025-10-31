from django.http import JsonResponse, Http404
from django.views import View
from .models import Employee


class EmployeeDetailView(View):
    """Return employee details as JSON based on slug."""

    def get(self, request, slug):
        try:
            emp = Employee.objects.get(slug=slug)
        except Employee.DoesNotExist:
            raise Http404("Employee not found")

        data = {
            "slug": emp.slug,
            "name": emp.name,
            "designation": emp.designation,
            "region": emp.region,
            "phone": emp.phone,
            "email": emp.email,
            "address": emp.address,
            "photo_url": emp.photo.url if emp.photo else None,
            "qr_url": emp.qr_code.url if emp.qr_code else None, 
            "profile_url": emp.public_profile_url(),
        }
        return JsonResponse(data, status=200)
