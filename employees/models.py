import uuid
from io import BytesIO
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from storages.backends.s3boto3 import S3Boto3Storage
import qrcode


PUBLIC_BASE_URL = "https://etomosphere.com"

def employee_upload_path(instance, filename):
    """Store files under /employees/<slug>/"""
    return f"employees/{instance.slug}/{filename}"

def validate_image_size(image_field_file, max_mb=5):
    """Ensure uploaded image is below max_mb megabytes."""
    if not image_field_file:
        return
    if image_field_file.size > max_mb * 1024 * 1024:
        raise ValidationError(f"Image too large (>{max_mb} MB).")



class Employee(models.Model):
    name        = models.CharField(max_length=120)
    designation = models.CharField(max_length=120, blank=True)
    phone       = models.CharField(max_length=20, blank=True)
    email       = models.EmailField(unique=True)
    region      = models.CharField(max_length=100, blank=True)  
    address     = models.TextField(blank=True, null=True)

    # Permanent slug (used in URLs and QR codes)
    slug = models.SlugField(unique=True, blank=True)

    # Files (photo & QR)
    photo      =  models.ImageField(storage=S3Boto3Storage() , upload_to='logos', max_length=5000000, blank=True, null=True)
    qr_code    =  models.ImageField(storage=S3Boto3Storage() , upload_to='logos', max_length=5000000, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.region})" if self.region else self.name

    # ---------- URL helpers ----------
       # ---------- URL helpers ----------
    def public_base(self):
        """
        Base domain used in QR links.
        Set in settings.py as:
        PUBLIC_BASE_URL = "https://etomosphere.com"
        """
        return getattr(settings, "PUBLIC_BASE_URL", "https://etomosphere.com")

    def public_profile_url(self):
        """URL encoded inside the QR code — points to React frontend."""
        return f"{self.public_base()}/employee/{self.slug}"

    # ---------- Slug ----------
    def _ensure_slug(self):
        """Assign a permanent slug once."""
        if not self.slug:
            self.slug = uuid.uuid4().hex

    # ---------- QR Code ----------
    def generate_qr_code(self, force=False):
        """Generate a high-quality QR image for the employee’s profile."""
        if self.qr_code and not force:
            return

        url = self.public_profile_url()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        filename = f"{self.slug}_qr.png"
        self.qr_code.save(filename, ContentFile(buffer.read()), save=False)

    # ---------- Save Override ----------
    def save(self, *args, **kwargs):
        """
        When saved (from admin or API), automatically:
        - Assigns a slug if missing
        - Validates photo size
        - Generates QR code
        """
        is_create = self.pk is None
        self._ensure_slug()

        # Validate photo file size before upload (optional)
        try:
            if self.photo and hasattr(self.photo, 'file'):
                validate_image_size(self.photo.file, max_mb=5)
        except AttributeError:
            pass  # skip if storage doesn’t expose .file before save

        # First save to ensure slug exists
        if is_create:
            super().save(*args, **kwargs)

        # Generate QR if missing
        self.generate_qr_code(force=False)

        # Final save with QR code included
        super().save(*args, **kwargs)