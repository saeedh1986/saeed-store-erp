from django.contrib import admin
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'is_customer', 'is_vendor')
    list_filter = ('is_customer', 'is_vendor')
    search_fields = ('name', 'email')
