from rest_framework import serializers
from .models import Category, Product, ReceiveStock

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'category_id', 'stock_quantity', 'price']


# Receive Stock Serializer
class ReceiveStockSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)

    class Meta:
        model = ReceiveStock
        fields = ['id', 'product', 'product_id', 'quantity_received', 'received_by', 'received_at', 'notes']
        read_only_fields = ['received_by', 'received_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['received_by'] = request.user
        return super().create(validated_data)
    
