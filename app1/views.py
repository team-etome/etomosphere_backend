from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.core.mail import EmailMultiAlternatives
from django.conf import settings


class TestAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'message': 'Etomosphere Backend is working!',
            'status': 'success',
            'version': '1.0.0',
        }, status=status.HTTP_200_OK)


def _send_contact_email(subject_tag, name, email, phone, message, extra_fields=None):
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@etomosphere.local')
    team_email = [getattr(settings, 'ENQUIRY_RECEIVER_EMAIL', 'info@etome.in'), 'parvathy@etomeworks.com']

    extra_html = ''
    extra_plain = ''
    if extra_fields:
        for label, value in extra_fields.items():
            extra_plain += f'{label}: {value or "-"}\n'
            extra_html += f'<tr><td style="padding:6px 0;font-size:14px;color:#555;width:140px;">{label}</td><td style="padding:6px 0;font-size:14px;color:#0f0f23;font-weight:600;">{value or "-"}</td></tr>'

    team_plain = (
        f"{subject_tag}\n\nName: {name}\nEmail: {email}\nPhone: {phone}\n"
        f"{extra_plain}Message:\n{message or '-'}\n\nSubmitted via etomosphere.com"
    )

    team_html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f0f0f0;font-family:Arial,Helvetica,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f0f0;padding:32px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.1);">
  <tr><td style="background:#0f0f23;padding:26px 32px;">
    <p style="margin:0;font-size:20px;font-weight:700;color:#fff;letter-spacing:1.5px;">ETOMOSPHERE</p>
    <p style="margin:4px 0 0;font-size:12px;color:#aaa;">{subject_tag}</p>
  </td></tr>
  <tr><td style="padding:28px 32px;">
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr><td style="padding:6px 0;font-size:14px;color:#555;width:140px;">Name</td><td style="padding:6px 0;font-size:14px;color:#0f0f23;font-weight:600;">{name}</td></tr>
      <tr><td style="padding:6px 0;font-size:14px;color:#555;">Email</td><td style="padding:6px 0;font-size:14px;color:#0f0f23;font-weight:600;">{email}</td></tr>
      <tr><td style="padding:6px 0;font-size:14px;color:#555;">Phone</td><td style="padding:6px 0;font-size:14px;color:#0f0f23;font-weight:600;">{phone}</td></tr>
      {extra_html}
      <tr><td colspan="2" style="padding:14px 0 0;font-size:14px;color:#555;">Message</td></tr>
      <tr><td colspan="2" style="padding:6px 0;font-size:14px;color:#0f0f23;">{message or '-'}</td></tr>
    </table>
  </td></tr>
</table>
</td></tr>
</table>
</body></html>"""

    user_plain = (
        f"Hello {name},\n\nThank you for reaching out to Etomosphere.\n"
        f"Our team will get back to you shortly.\n\nBest regards,\nEtomosphere Team"
    )
    user_html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f0f0f0;font-family:Arial,Helvetica,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f0f0;padding:32px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.1);">
  <tr><td style="background:#0f0f23;padding:26px 32px;">
    <p style="margin:0;font-size:20px;font-weight:700;color:#fff;letter-spacing:1.5px;">ETOMOSPHERE</p>
  </td></tr>
  <tr><td style="padding:44px 40px;text-align:center;">
    <h2 style="margin:0 0 12px;font-size:22px;color:#0f0f23;">Thank You, {name}!</h2>
    <p style="margin:0 0 8px;font-size:15px;color:#555;line-height:1.7;">We've received your message and our team will get back to you shortly.</p>
    <p style="margin:0;font-size:13px;color:#999;">Meanwhile, explore our solutions at<br>
      <a href="https://etomosphere.com" style="color:#0f0f23;font-weight:700;text-decoration:none;">etomosphere.com</a>
    </p>
  </td></tr>
</table>
</td></tr>
</table>
</body></html>"""

    team_msg = EmailMultiAlternatives(subject_tag, team_plain, from_email, team_email)
    team_msg.attach_alternative(team_html, 'text/html')
    team_msg.send(fail_silently=False)

    user_msg = EmailMultiAlternatives(f'Thank you for contacting Etomosphere', user_plain, from_email, [email])
    user_msg.attach_alternative(user_html, 'text/html')
    user_msg.send(fail_silently=False)


def _get(data, *keys):
    for k in keys:
        v = data.get(k, '')
        if v:
            return str(v).strip()
    return ''


class ContactView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data    = request.data
            name    = _get(data, 'name', 'full_name', 'fullName')
            email   = _get(data, 'email', 'email_address', 'emailAddress')
            phone   = _get(data, 'phone', 'contact_number', 'contactNumber', 'phone_number', 'phoneNumber')
            message = _get(data, 'message', 'your_message', 'yourMessage', 'msg')

            if not all([name, email, phone]):
                return Response({'error': 'Name, email and phone are required.', 'received': dict(data)}, status=status.HTTP_400_BAD_REQUEST)
            if '@' not in email:
                return Response({'error': 'Invalid email.'}, status=status.HTTP_400_BAD_REQUEST)

            _send_contact_email('New Contact Sales Enquiry', name, email, phone, message)
            return Response({'message': 'Message sent successfully.'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RequestDemoView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data         = request.data
            name         = _get(data, 'name', 'full_name', 'fullName')
            email        = _get(data, 'email', 'email_address', 'emailAddress')
            phone        = _get(data, 'phone', 'phone_number', 'phoneNumber', 'mobile', 'mobileNumber', 'mobile_number', 'contact_number', 'contactNumber')
            organisation = _get(data, 'organisation', 'organization', 'institution', 'institutionName', 'institution_name', 'company', 'school')
            designation  = _get(data, 'designation', 'role', 'position')
            location     = _get(data, 'location', 'city', 'state')
            demo_link    = _get(data, 'demo_link', 'demoLink', 'virtual', 'virtualLink', 'link')
            message      = _get(data, 'message', 'additional_message', 'additionalMessage', 'msg', 'comment')

            if not all([name, email, phone]):
                return Response({'error': 'Name, email and phone are required.', 'received': dict(data)}, status=status.HTTP_400_BAD_REQUEST)
            if '@' not in email:
                return Response({'error': 'Invalid email.'}, status=status.HTTP_400_BAD_REQUEST)

            extra = {}
            if organisation:
                extra['Institution'] = organisation
            if designation:
                extra['Designation'] = designation
            if location:
                extra['Location'] = location
            if demo_link:
                extra['Demo Link (Virtual/Physical)'] = demo_link

            _send_contact_email('New Demo Request', name, email, phone, message, extra_fields=extra)
            return Response({'message': 'Demo request sent successfully.'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
