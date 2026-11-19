from django.db import models


class OEMRegistration(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    COMPANY_TYPE_CHOICES = [
        ('pvt_ltd',     'Private Limited'),
        ('public_ltd',  'Public Limited'),
        ('llp',         'LLP'),
        ('partnership', 'Partnership'),
        ('proprietorship', 'Proprietorship'),
        ('other',       'Other'),
    ]

    # Step 1 – Account
    full_name    = models.CharField(max_length=200)
    email        = models.EmailField(unique=True)
    mobile       = models.CharField(max_length=20)
    password     = models.CharField(max_length=256)  # stored hashed

    # Step 2 – Company Details
    company_name  = models.CharField(max_length=300)
    company_type  = models.CharField(max_length=50, choices=COMPANY_TYPE_CHOICES, blank=True)
    gst_number    = models.CharField(max_length=20,  blank=True)
    cin_number    = models.CharField(max_length=30,  blank=True)
    pan_number    = models.CharField(max_length=15,  blank=True)
    website       = models.URLField(blank=True)
    year_founded  = models.CharField(max_length=4,   blank=True)
    num_employees = models.CharField(max_length=50,  blank=True)

    # Step 3 – Business Verification (file uploads)
    gst_certificate   = models.FileField(upload_to='oem/docs/', blank=True, null=True)
    pan_card          = models.FileField(upload_to='oem/docs/', blank=True, null=True)
    incorporation_doc = models.FileField(upload_to='oem/docs/', blank=True, null=True)
    cancelled_cheque  = models.FileField(upload_to='oem/docs/', blank=True, null=True)

    # Step 4 – Business Address
    address_line1 = models.CharField(max_length=300, blank=True)
    address_line2 = models.CharField(max_length=300, blank=True)
    city          = models.CharField(max_length=100, blank=True)
    state         = models.CharField(max_length=100, blank=True)
    pincode       = models.CharField(max_length=10,  blank=True)
    country       = models.CharField(max_length=100, default='India')

    # Step 5 – Product Categories
    product_categories = models.JSONField(default=list)
    product_description = models.TextField(blank=True)

    # Meta
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_note  = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'OEM Registration'
        verbose_name_plural = 'OEM Registrations'

    def __str__(self):
        return f"{self.company_name} ({self.email}) — {self.status}"
