from django.contrib import admin
from .models import Product, Category, StockMove

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'category', 'price', 'current_stock', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('sku', 'name')
    readonly_fields = ('current_stock',) # Calculated field

@admin.register(StockMove)
class StockMoveAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'product', 'move_type', 'quantity', 'reference')
    list_filter = ('move_type', 'created_at')
    search_fields = ('product__sku', 'reference')
    date_hierarchy = 'created_at'
