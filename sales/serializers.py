from rest_framework import serializers
from .models import Customer, Product, Sale, SaleItem, Payment

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class SaleItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = SaleItem
        fields = ['product', 'quantity', 'price_at_sale']

class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)
    customer = CustomerSerializer()
    
    class Meta:
        model = Sale
        fields = ['id', 'customer', 'salesperson', 'payment_method', 'total_amount', 'paid_amount', 'created_at', 'items']

class CreateSaleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItem
        fields = ['product', 'quantity', 'price_at_sale']

class CreateSaleSerializer(serializers.ModelSerializer):
    items = CreateSaleItemSerializer(many=True)

    class Meta:
        model = Sale
        fields = ['customer', 'payment_method', 'total_amount', 'paid_amount', 'items']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
