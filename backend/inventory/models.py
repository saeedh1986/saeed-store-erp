from django.db import models
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Store price in standard decimal for Django (easier than cents logic for Admin)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Selling Price")
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sku} - {self.name}"

    @property
    def current_stock(self):
        # Calculate from stock moves
        # For simplicity in Admin display, we might want to cache this or use an annotated query
        total = self.stock_moves.aggregate(total=models.Sum('quantity'))['total']
        return total or 0

class StockMove(models.Model):
    TYPE_CHOICES = [
        ('purchase', 'Purchase (IN)'),
        ('sale', 'Sale (OUT)'),
        ('adjustment', 'Adjustment'),
        ('return', 'Return (IN)'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stock_moves")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Positive for IN, Negative for OUT")
    move_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='adjustment')
    reference = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.sku} ({self.quantity}) - {self.move_type}"
