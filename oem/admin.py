from django.contrib import admin
from .models import OEMRegistration


@admin.register(OEMRegistration)
class OEMRegistrationAdmin(admin.ModelAdmin):
    list_display  = ['company_name', 'full_name', 'email', 'mobile', 'status', 'submitted_at']
    list_filter   = ['status', 'company_type', 'submitted_at']
    search_fields = ['company_name', 'email', 'full_name', 'gst_number']
    readonly_fields = ['submitted_at', 'updated_at']
    ordering      = ['-submitted_at']

    fieldsets = (
        ('Contact', {'fields': ('full_name', 'email', 'mobile')}),
        ('Company', {'fields': ('company_name', 'company_type', 'gst_number', 'cin_number', 'pan_number', 'website', 'year_founded', 'num_employees')}),
        ('Documents', {'fields': ('gst_certificate', 'pan_card', 'incorporation_doc', 'cancelled_cheque')}),
        ('Address',  {'fields': ('address_line1', 'address_line2', 'city', 'state', 'pincode', 'country')}),
        ('Products', {'fields': ('product_categories', 'product_description')}),
        ('Admin',    {'fields': ('status', 'admin_note', 'submitted_at', 'updated_at')}),
    )
