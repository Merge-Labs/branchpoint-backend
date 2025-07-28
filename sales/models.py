from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# 1. Customer Model
class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# 2. Product Model
class Product(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# 3. Sale Model
class Sale(models.Model):
    PAYMENT_CHOICES = (
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
        ('account', 'On Account'),
    )

    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales'
    )
    salesperson = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='sales_made'
    )
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale #{self.pk} - {self.get_payment_method_display()}"


# 4. SaleItem Model
class SaleItem(models.Model):
    sale = models.ForeignKey(
        Sale, related_name='items', on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='sale_items'
    )
    quantity = models.PositiveIntegerField()
    price_at_sale = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} @ {self.price_at_sale}"


# 5. Payment Model (for Receive Payment page)
class Payment(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    received_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='payments_received'
    )
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} received from {self.customer.name}"
