from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'customer', 'status', 'total_amount', 'created_at', 'ai_risk_score')
    list_filter = ('status', 'created_at')
    search_fields = ('external_id', 'customer__username', 'customer__email')
    inlines = [OrderItemInline]
    readonly_fields = ('ai_risk_score', 'ai_notes')
