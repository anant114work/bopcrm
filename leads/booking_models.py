from django.db import models
from django.utils import timezone
from .booking_source_models import BookingSourceCategory, BookingSource

class UnitedNetworkBooking(models.Model):
    """Model to store booking data received from United Network CRM"""
    
    # Booking identification
    api_key = models.CharField(max_length=50)
    booking_id = models.CharField(max_length=50, unique=True)
    
    # Customer information
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField(blank=True)
    customer_address = models.TextField(blank=True)
    nominee_name = models.CharField(max_length=200, blank=True)
    
    # Unit details
    unit_type = models.CharField(max_length=50)
    unit_number = models.CharField(max_length=50)
    area = models.CharField(max_length=100)
    
    # Financial details
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    booking_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Project information
    project_name = models.CharField(max_length=200)
    project_location = models.CharField(max_length=200)
    developer = models.CharField(max_length=200)
    
    # Channel Partner details
    cp_code = models.CharField(max_length=50, blank=True)
    cp_company = models.CharField(max_length=200, blank=True)
    cp_name = models.CharField(max_length=200, blank=True)
    cp_phone = models.CharField(max_length=20, blank=True)
    cp_email = models.EmailField(blank=True)
    
    # Status and metadata
    status = models.CharField(max_length=50)
    booking_source = models.CharField(max_length=50, default='web_form')
    source_category = models.ForeignKey(BookingSourceCategory, on_delete=models.SET_NULL, null=True, blank=True)
    source_detail = models.ForeignKey(BookingSource, on_delete=models.SET_NULL, null=True, blank=True)
    custom_source = models.CharField(max_length=100, blank=True, help_text="Custom source if not in predefined list")
    
    # Timestamps
    created_at = models.DateTimeField()  # From payload
    received_at = models.DateTimeField(auto_now_add=True)  # When we received it
    
    # Raw payload for debugging
    raw_payload = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-received_at']
        verbose_name = 'United Network Booking'
        verbose_name_plural = 'United Network Bookings'
    
    def __str__(self):
        return f"{self.booking_id} - {self.customer_name} - {self.project_name}"
    
    @property
    def formatted_amount(self):
        """Format total amount in lakhs/crores"""
        amount = float(self.total_amount)
        if amount >= 10000000:  # 1 crore
            return f"₹{amount/10000000:.2f} Cr"
        elif amount >= 100000:  # 1 lakh
            return f"₹{amount/100000:.2f} L"
        else:
            return f"₹{amount:,.0f}"