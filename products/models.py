from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    stock_quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class ReceiveStock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_receipts')
    quantity_received = models.PositiveIntegerField()
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_stocks')
    received_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # On saving, increase the product's stock
        if self.pk is None:  # only increase stock on first creation
            self.product.stock_quantity += self.quantity_received
            self.product.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity_received} units of {self.product.name} received"
