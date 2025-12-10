from django.db import models

class Contact(models.Model):
    """
    Unified model for Customers and Vendors.
    For simplicity in phase 1, we might just use the User model for customers, 
    but a dedicated Contact model is better for CRM features.
    """
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    is_vendor = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
