from rest_framework import viewsets, permissions
from .models import Category, Product, ReceiveStock
from .serializers import CategorySerializer, ProductSerializer, ReceiveStockSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReceiveStockViewSet(viewsets.ModelViewSet):
    queryset = ReceiveStock.objects.select_related('product', 'received_by').all()
    serializer_class = ReceiveStockSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(received_by=self.request.user)
