from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import OEMRegistration
from .serializers import OEMRegistrationSerializer, OEMRegistrationListSerializer


class OEMRegisterView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        # Check duplicate email
        email = request.data.get('email', '').lower().strip()
        if OEMRegistration.objects.filter(email=email).exists():
            return Response(
                {'email': 'An application with this email already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data.copy()
        if hasattr(data, '_mutable'):
            data._mutable = True
        data['email'] = email

        serializer = OEMRegistrationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Registration submitted successfully. We will review and contact you shortly.'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OEMListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        registrations = OEMRegistration.objects.all()
        status_filter = request.query_params.get('status')
        if status_filter:
            registrations = registrations.filter(status=status_filter)
        serializer = OEMRegistrationListSerializer(registrations, many=True)
        return Response(serializer.data)


class OEMApproveView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            reg = OEMRegistration.objects.get(pk=pk)
        except OEMRegistration.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if new_status not in ['approved', 'rejected', 'pending']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        reg.status     = new_status
        reg.admin_note = request.data.get('admin_note', reg.admin_note)
        reg.save()
        return Response({'message': f'Registration {new_status}.', 'status': reg.status})
